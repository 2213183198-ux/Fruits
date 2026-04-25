from __future__ import annotations

from pathlib import Path
from typing import Any

from ultralytics import YOLO


def train_model(
    model_path: Path,
    data_path: Path,
    epochs: int,
    imgsz: int,
    batch: int,
    device: str,
    workers: int,
    project: str,
    name: str,
) -> dict[str, Any]:
    model = YOLO(str(model_path))
    results = model.train(
        data=str(data_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        device=device,
        amp=True,
        optimizer="AdamW",
        lr0=0.001,
        cos_lr=True,
        close_mosaic=10,
        patience=50,
        seed=42,
        mosaic=1.0,
        mixup=0.1,
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.3,
        fliplr=0.5,
        flipud=0.2,
        project=project,
        name=name,
        save=True,
        plots=True,
    )
    save_dir = getattr(results, "save_dir", "")
    return {
        "status": "ok",
        "model": str(model_path),
        "data": str(data_path),
        "epochs": epochs,
        "image_size": imgsz,
        "batch": batch,
        "device": device,
        "save_dir": str(save_dir),
    }

