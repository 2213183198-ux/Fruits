from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import cv2
import uvicorn

from backend.config import settings
from backend.services.deployment import deployment_service
from backend.services.history import history_service
from backend.services.inference import inference_service
from backend.services.metadata import get_project_metadata
from backend.services.training import train_model


SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _load_file_bytes(path: Path) -> bytes:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_bytes()


def _collect_image_paths(paths: Iterable[str]) -> list[Path]:
    collected: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if path.is_dir():
            collected.extend(
                sorted(
                    child for child in path.iterdir() if child.is_file() and child.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
                )
            )
        elif path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES:
            collected.append(path)
        else:
            raise FileNotFoundError(f"Unsupported or missing image path: {path}")

    if not collected:
        raise FileNotFoundError("No supported image files were found in the provided paths.")

    return collected


def serve_command(args: argparse.Namespace) -> None:
    uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=args.reload)


def metadata_command(_: argparse.Namespace) -> None:
    _print_json(get_project_metadata())


def deployment_status_command(_: argparse.Namespace) -> None:
    _print_json(deployment_service.get_status())


def export_onnx_command(args: argparse.Namespace) -> None:
    payload = deployment_service.export_onnx(imgsz=args.imgsz)
    _print_json(payload)


def benchmark_command(args: argparse.Namespace) -> None:
    source = Path(args.source).expanduser().resolve()
    payload = deployment_service.benchmark_bytes(
        file_bytes=_load_file_bytes(source),
        filename=source.name,
        imgsz=args.imgsz,
        conf=args.conf,
        runs=args.runs,
    )
    _print_json(payload)


def predict_image_command(args: argparse.Namespace) -> None:
    source = Path(args.source).expanduser().resolve()
    result = inference_service.predict_bytes(
        file_bytes=_load_file_bytes(source),
        filename=source.name,
        imgsz=args.imgsz,
        conf=args.conf,
        save_artifact=args.save_artifact,
    )
    run_id = history_service.record_run(
        mode="single",
        image_size=args.imgsz,
        confidence_threshold=args.conf,
        results=[result],
        failures=[],
    )
    result["history_run_id"] = run_id
    _print_json(result)


def predict_batch_command(args: argparse.Namespace) -> None:
    image_paths = _collect_image_paths(args.sources)
    results = []
    failures = []

    for path in image_paths:
        try:
            results.append(
                inference_service.predict_bytes(
                    file_bytes=_load_file_bytes(path),
                    filename=path.name,
                    imgsz=args.imgsz,
                    conf=args.conf,
                    save_artifact=args.save_artifact,
                )
            )
        except Exception as exc:  # pragma: no cover - CLI should continue per file
            failures.append({"filename": path.name, "error": str(exc)})

    csv_url = inference_service.export_batch_csv(results) if args.export_csv and results else None
    excel_url = (
        inference_service.export_batch_excel(results=results, failures=failures, total_files=len(image_paths))
        if args.export_excel and results
        else None
    )
    status_counts = Counter(item["report"]["status"] for item in results)
    run_id = history_service.record_run(
        mode="batch",
        image_size=args.imgsz,
        confidence_threshold=args.conf,
        results=results,
        failures=failures,
        csv_url=csv_url,
        excel_url=excel_url,
    )

    payload = {
        "history_run_id": run_id,
        "total_files": len(image_paths),
        "successful_files": len(results),
        "failed_files": len(failures),
        "total_detections": sum(item["summary"]["total_detections"] for item in results),
        "status_counts": dict(sorted(status_counts.items())),
        "csv_url": csv_url,
        "excel_url": excel_url,
        "results": results,
        "failures": failures,
    }
    _print_json(payload)


def history_command(args: argparse.Namespace) -> None:
    if args.run_id is not None:
        payload = history_service.get_run(args.run_id)
        if payload is None:
            raise SystemExit(f"History record not found: {args.run_id}")
        _print_json(payload)
        return

    _print_json(history_service.list_runs(limit=args.limit))


def train_command(args: argparse.Namespace) -> None:
    payload = train_model(
        model_path=Path(args.model).expanduser().resolve(),
        data_path=Path(args.data).expanduser().resolve(),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        project=args.project,
        name=args.name,
    )
    _print_json(payload)


def camera_command(args: argparse.Namespace) -> None:
    model = inference_service.load_model()
    capture = cv2.VideoCapture(args.camera_index)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open camera index {args.camera_index}.")

    print(f"Starting camera stream on index {args.camera_index}. Press 'q' to quit.")
    started_at = time.perf_counter()
    frames_processed = 0

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("Failed to read a frame from the camera.")

            infer_started_at = time.perf_counter()
            result = model.predict(source=frame, imgsz=args.imgsz, conf=args.conf, verbose=False)[0]
            annotated_frame = result.plot()
            frames_processed += 1

            if args.show_fps:
                elapsed = time.perf_counter() - infer_started_at
                fps = 0.0 if elapsed <= 0 else 1.0 / elapsed
                cv2.putText(
                    annotated_frame,
                    f"FPS: {fps:.2f}",
                    (16, 32),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow(args.window_name, annotated_frame)

            if args.max_frames is not None and frames_processed >= args.max_frames:
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            if cv2.getWindowProperty(args.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()

    duration = time.perf_counter() - started_at
    payload = {
        "status": "ok",
        "camera_index": args.camera_index,
        "frames_processed": frames_processed,
        "average_fps": round(frames_processed / duration, 2) if duration > 0 else 0.0,
        "window_name": args.window_name,
    }
    _print_json(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified CLI for the fruit inspection platform.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI service.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8001)
    serve_parser.add_argument("--reload", action="store_true")
    serve_parser.set_defaults(func=serve_command)

    metadata_parser = subparsers.add_parser("metadata", help="Show project metadata.")
    metadata_parser.set_defaults(func=metadata_command)

    status_parser = subparsers.add_parser("deployment-status", help="Show deployment artifact status.")
    status_parser.set_defaults(func=deployment_status_command)

    export_parser = subparsers.add_parser("export-onnx", help="Export the PyTorch model to ONNX.")
    export_parser.add_argument("--imgsz", type=int, default=settings.default_image_size)
    export_parser.set_defaults(func=export_onnx_command)

    benchmark_parser = subparsers.add_parser("benchmark", help="Benchmark PyTorch and ONNX inference.")
    benchmark_parser.add_argument("--source", required=True)
    benchmark_parser.add_argument("--imgsz", type=int, default=settings.default_image_size)
    benchmark_parser.add_argument("--conf", type=float, default=settings.default_confidence)
    benchmark_parser.add_argument("--runs", type=int, default=3)
    benchmark_parser.set_defaults(func=benchmark_command)

    image_parser = subparsers.add_parser("predict-image", help="Run single-image prediction.")
    image_parser.add_argument("--source", required=True)
    image_parser.add_argument("--imgsz", type=int, default=settings.default_image_size)
    image_parser.add_argument("--conf", type=float, default=settings.default_confidence)
    image_parser.add_argument("--save-artifact", action="store_true")
    image_parser.set_defaults(func=predict_image_command)

    batch_parser = subparsers.add_parser("predict-batch", help="Run batch prediction on files or directories.")
    batch_parser.add_argument("sources", nargs="+")
    batch_parser.add_argument("--imgsz", type=int, default=settings.default_image_size)
    batch_parser.add_argument("--conf", type=float, default=settings.default_confidence)
    batch_parser.add_argument("--save-artifact", action="store_true")
    batch_parser.add_argument("--export-csv", action="store_true")
    batch_parser.add_argument("--export-excel", action="store_true")
    batch_parser.set_defaults(func=predict_batch_command)

    history_parser = subparsers.add_parser("history", help="Show inspection history.")
    history_parser.add_argument("--limit", type=int, default=10)
    history_parser.add_argument("--run-id", type=int)
    history_parser.set_defaults(func=history_command)

    train_parser = subparsers.add_parser("train", help="Launch YOLO training with the project defaults.")
    train_parser.add_argument("--model", default=str((settings.project_root / "yolo11s.pt").resolve()))
    train_parser.add_argument("--data", default=str(settings.data_config_path))
    train_parser.add_argument("--epochs", type=int, default=300)
    train_parser.add_argument("--imgsz", type=int, default=640)
    train_parser.add_argument("--batch", type=int, default=8)
    train_parser.add_argument("--device", default="0")
    train_parser.add_argument("--workers", type=int, default=4)
    train_parser.add_argument("--project", default="runs/train")
    train_parser.add_argument("--name", default="fruit_quality_check")
    train_parser.set_defaults(func=train_command)

    camera_parser = subparsers.add_parser("camera", help="Run real-time webcam inference.")
    camera_parser.add_argument("--camera-index", type=int, default=0)
    camera_parser.add_argument("--imgsz", type=int, default=settings.default_image_size)
    camera_parser.add_argument("--conf", type=float, default=settings.default_confidence)
    camera_parser.add_argument("--window-name", default="Fruit Inspection Camera")
    camera_parser.add_argument("--show-fps", action="store_true")
    camera_parser.add_argument("--max-frames", type=int)
    camera_parser.set_defaults(func=camera_command)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
