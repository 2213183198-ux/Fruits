from __future__ import annotations

import importlib
import shutil
import time
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

from backend.config import settings


class DeploymentService:
    def __init__(self, torch_model_path: Path | None, onnx_model_path: Path | None, tensorrt_model_path: Path | None = None) -> None:
        self.torch_model_path = torch_model_path
        self.onnx_model_path = onnx_model_path
        self.tensorrt_model_path = tensorrt_model_path
        self._onnx_model: YOLO | None = None
        self._tensorrt_model: YOLO | None = None

    def set_model_targets(self, pytorch_path: Path | None, onnx_path: Path | None, tensorrt_path: Path | None = None) -> None:
        self.torch_model_path = pytorch_path.resolve() if pytorch_path else None
        self.onnx_model_path = onnx_path.resolve() if onnx_path else None
        self.tensorrt_model_path = tensorrt_path.resolve() if tensorrt_path else None
        self._onnx_model = None
        self._tensorrt_model = None

    def _artifact_payload(self, path: Path | None) -> dict[str, Any]:
        if path is None:
            return {"path": "", "exists": False, "size_mb": 0.0}

        exists = path.exists()
        return {
            "path": str(path),
            "exists": exists,
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2) if exists else 0.0,
        }

    def get_status(self) -> dict[str, Any]:
        providers: list[str] = []
        onnx_ready = self._onnx_dependencies_ready()
        if onnx_ready:
            import onnxruntime as ort

            providers = list(ort.get_available_providers())

        return {
            "pytorch": self._artifact_payload(self.torch_model_path),
            "onnx": self._artifact_payload(self.onnx_model_path),
            "tensorrt": self._artifact_payload(self.tensorrt_model_path),
            "onnx_dependencies_ready": onnx_ready,
            "tensorrt_dependencies_ready": self._tensorrt_dependencies_ready(),
            "onnxruntime_providers": providers,
        }

    def export_onnx(self, imgsz: int) -> dict[str, Any]:
        if self.torch_model_path is None:
            raise FileNotFoundError("Active model is not a PyTorch model, so ONNX export is unavailable.")
        if not self.torch_model_path.exists():
            raise FileNotFoundError(f"PyTorch model not found: {self.torch_model_path}")
        if self.onnx_model_path is None:
            raise FileNotFoundError("No writable ONNX target path is configured.")
        if not self._onnx_dependencies_ready():
            raise RuntimeError("ONNX export dependencies are not installed in the current environment.")

        model = YOLO(str(self.torch_model_path))
        exported_path = Path(model.export(format="onnx", imgsz=imgsz, simplify=False, dynamic=False))
        if exported_path.resolve() != self.onnx_model_path.resolve():
            self.onnx_model_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(exported_path, self.onnx_model_path)

        self._onnx_model = None
        return {
            "status": "ok",
            "onnx": self._artifact_payload(self.onnx_model_path),
            "image_size": imgsz,
            "message": "ONNX export completed successfully.",
        }

    def export_tensorrt(self, imgsz: int) -> dict[str, Any]:
        if self.torch_model_path is None:
            raise FileNotFoundError("Active model is not a PyTorch model, so TensorRT export is unavailable.")
        if not self.torch_model_path.exists():
            raise FileNotFoundError(f"PyTorch model not found: {self.torch_model_path}")
        if self.tensorrt_model_path is None:
            raise FileNotFoundError("No writable TensorRT target path is configured.")
        if not self._tensorrt_dependencies_ready():
            raise RuntimeError("TensorRT export dependencies are not installed in the current environment.")
        if not self._cuda_available():
            raise RuntimeError("TensorRT export requires an available CUDA device.")

        model = YOLO(str(self.torch_model_path))
        exported_path = Path(model.export(format="engine", imgsz=imgsz))
        if exported_path.resolve() != self.tensorrt_model_path.resolve():
            self.tensorrt_model_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(exported_path, self.tensorrt_model_path)

        self._tensorrt_model = None
        return {
            "status": "ok",
            "tensorrt": self._artifact_payload(self.tensorrt_model_path),
            "image_size": imgsz,
            "message": "TensorRT export completed successfully.",
        }

    def benchmark_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        imgsz: int,
        conf: float,
        runs: int,
    ) -> dict[str, Any]:
        image = self._decode_image(file_bytes)
        engines: list[dict[str, Any]] = []
        notes: list[str] = []
        capabilities = self._benchmark_capabilities()

        torch_metrics = None
        if self.torch_model_path and self.torch_model_path.exists():
            torch_metrics = self._benchmark_engine(
                engine_name="pytorch",
                model=YOLO(str(self.torch_model_path)),
                image=image,
                imgsz=imgsz,
                conf=conf,
                runs=runs,
                predict_kwargs={"device": 0 if self._cuda_available() else "cpu"},
            )
            engines.append(torch_metrics)
        else:
            notes.append("PyTorch benchmark skipped because no active .pt model is available.")

        onnx_metrics = None
        if not self.onnx_model_path or not self.onnx_model_path.exists():
            notes.append("ONNX benchmark skipped because no ONNX model is available.")
        elif not self._onnx_dependencies_ready():
            notes.append("ONNX benchmark skipped because ONNX runtime dependencies are not installed.")
        else:
            onnx_model = self._load_onnx_model()
            onnx_metrics = self._benchmark_engine(
                engine_name="onnx",
                model=onnx_model,
                image=image,
                imgsz=imgsz,
                conf=conf,
                runs=runs,
                predict_kwargs={"device": "cpu"},
            )
            engines.append(onnx_metrics)

        tensorrt_metrics = None
        if not self.tensorrt_model_path or not self.tensorrt_model_path.exists():
            notes.append("TensorRT benchmark skipped because no TensorRT engine is available.")
        elif not self._tensorrt_dependencies_ready():
            notes.append("TensorRT benchmark skipped because TensorRT dependencies are not installed.")
        elif not self._cuda_available():
            notes.append("TensorRT benchmark skipped because no CUDA device is available.")
        else:
            tensorrt_model = self._load_tensorrt_model()
            tensorrt_metrics = self._benchmark_engine(
                engine_name="tensorrt",
                model=tensorrt_model,
                image=image,
                imgsz=imgsz,
                conf=conf,
                runs=runs,
                predict_kwargs={"device": 0},
            )
            engines.append(tensorrt_metrics)

        if torch_metrics is None and onnx_metrics is None and tensorrt_metrics is None:
            raise FileNotFoundError("No executable benchmark engine is available.")

        speedup = None
        if torch_metrics is not None and onnx_metrics is not None and onnx_metrics["average_ms"] > 0:
            speedup = round(torch_metrics["average_ms"] / onnx_metrics["average_ms"], 3)

        tensorrt_speedup = None
        if torch_metrics is not None and tensorrt_metrics is not None and tensorrt_metrics["average_ms"] > 0:
            tensorrt_speedup = round(torch_metrics["average_ms"] / tensorrt_metrics["average_ms"], 3)

        return {
            "filename": filename,
            "image_size": imgsz,
            "confidence_threshold": conf,
            "engines": engines,
            "capabilities": capabilities,
            "speedup_vs_pytorch": speedup,
            "tensorrt_speedup_vs_pytorch": tensorrt_speedup,
            "notes": notes,
        }

    def _benchmark_engine(
        self,
        engine_name: str,
        model: YOLO,
        image: np.ndarray,
        imgsz: int,
        conf: float,
        runs: int,
        predict_kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        timings: list[float] = []
        final_result = None

        model.predict(source=image, imgsz=imgsz, conf=conf, verbose=False, **predict_kwargs)
        for _ in range(runs):
            start = time.perf_counter()
            results = model.predict(source=image, imgsz=imgsz, conf=conf, verbose=False, **predict_kwargs)
            timings.append((time.perf_counter() - start) * 1000)
            final_result = results[0]

        class_counts: Counter[str] = Counter()
        total_detections = 0
        if final_result is not None and final_result.boxes is not None:
            total_detections = len(final_result.boxes)
            for box in final_result.boxes:
                class_id = int(box.cls.item())
                label = self._resolve_label(final_result.names, class_id)
                class_counts[label] += 1

        return {
            "engine": engine_name,
            "runs": runs,
            "average_ms": round(sum(timings) / len(timings), 2),
            "best_ms": round(min(timings), 2),
            "worst_ms": round(max(timings), 2),
            "total_detections": total_detections,
            "class_counts": dict(sorted(class_counts.items())),
        }

    def _benchmark_capabilities(self) -> list[dict[str, Any]]:
        onnx_dependency_ready = self._onnx_dependencies_ready()
        return [
            {
                "engine": "pytorch",
                "implemented": True,
                "available": bool(self.torch_model_path and self.torch_model_path.exists()),
                "reason": None if self.torch_model_path and self.torch_model_path.exists() else "No active .pt model found.",
            },
            {
                "engine": "onnx",
                "implemented": True,
                "available": bool(self.onnx_model_path and self.onnx_model_path.exists() and onnx_dependency_ready),
                "reason": self._onnx_capability_reason(),
            },
            {
                "engine": "tensorrt",
                "implemented": True,
                "available": bool(self.tensorrt_model_path and self.tensorrt_model_path.exists() and self._tensorrt_dependencies_ready() and self._cuda_available()),
                "reason": self._tensorrt_capability_reason(),
            },
            {
                "engine": "openvino",
                "implemented": False,
                "available": False,
                "reason": "Reserved for future support.",
            },
        ]

    def _onnx_capability_reason(self) -> str | None:
        if not self.onnx_model_path or not self.onnx_model_path.exists():
            return "No ONNX model found."
        if not self._onnx_dependencies_ready():
            return "ONNX runtime dependencies are missing."
        return None

    def _tensorrt_capability_reason(self) -> str | None:
        if not self.tensorrt_model_path or not self.tensorrt_model_path.exists():
            return "No TensorRT engine found."
        if not self._tensorrt_dependencies_ready():
            return "TensorRT dependencies are missing."
        if not self._cuda_available():
            return "CUDA device is unavailable."
        return None

    def _load_onnx_model(self) -> YOLO:
        if self.onnx_model_path is None:
            raise FileNotFoundError("No ONNX model is configured.")
        if self._onnx_model is None:
            self._onnx_model = YOLO(str(self.onnx_model_path), task="detect")
        return self._onnx_model

    def _load_tensorrt_model(self) -> YOLO:
        if self.tensorrt_model_path is None:
            raise FileNotFoundError("No TensorRT engine is configured.")
        if self._tensorrt_model is None:
            self._tensorrt_model = YOLO(str(self.tensorrt_model_path), task="detect")
        return self._tensorrt_model

    def _decode_image(self, file_bytes: bytes) -> np.ndarray:
        buffer = np.frombuffer(file_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Uploaded file is not a valid image.")
        return image

    def _resolve_label(self, names: Any, class_id: int) -> str:
        if isinstance(names, dict):
            return str(names.get(class_id, class_id))
        if isinstance(names, list) and 0 <= class_id < len(names):
            return str(names[class_id])
        return str(class_id)

    def _onnx_dependencies_ready(self) -> bool:
        required_modules = ["onnx", "onnxruntime"]
        for name in required_modules:
            try:
                importlib.import_module(name)
            except Exception:
                return False
        return True

    def _tensorrt_dependencies_ready(self) -> bool:
        try:
            importlib.import_module("tensorrt")
        except Exception:
            return False
        return True

    def _cuda_available(self) -> bool:
        try:
            import torch
        except Exception:
            return False
        return bool(torch.cuda.is_available())


deployment_service = DeploymentService(settings.model_path, settings.onnx_model_path, settings.model_path.with_suffix(".engine"))
