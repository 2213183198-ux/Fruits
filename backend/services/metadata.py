from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from backend.config import settings


SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _count_images(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for path in directory.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES)


def _read_data_config() -> dict[str, Any]:
    if not settings.data_config_path.exists():
        return {}
    with settings.data_config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _read_training_metrics() -> dict[str, Any]:
    default = {
        "epochs": 0,
        "precision": 0.0,
        "recall": 0.0,
        "map50": 0.0,
        "map50_95": 0.0,
    }
    if not settings.training_results_path.exists():
        return default

    with settings.training_results_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        return default

    last = {key.strip(): value for key, value in rows[-1].items()}
    return {
        "epochs": int(float(last.get("epoch", 0))),
        "precision": round(float(last.get("metrics/precision(B)", 0.0)), 4),
        "recall": round(float(last.get("metrics/recall(B)", 0.0)), 4),
        "map50": round(float(last.get("metrics/mAP50(B)", 0.0)), 4),
        "map50_95": round(float(last.get("metrics/mAP50-95(B)", 0.0)), 4),
    }


@lru_cache(maxsize=1)
def get_project_metadata() -> dict[str, Any]:
    data_config = _read_data_config()
    dataset_root = settings.project_root / str(data_config.get("path", "data"))

    train_dir = dataset_root / str(data_config.get("train", "images/train"))
    val_dir = dataset_root / str(data_config.get("val", "images/valid"))
    test_dir = dataset_root / str(data_config.get("test", "images/test"))

    train_images = _count_images(train_dir)
    val_images = _count_images(val_dir)
    test_images = _count_images(test_dir)

    model_exists = settings.model_path.exists()
    model_size_mb = round(settings.model_path.stat().st_size / (1024 * 1024), 2) if model_exists else 0.0
    class_names = [str(name) for name in data_config.get("names", [])]

    return {
        "project_name": "面向生鲜分拣场景的多模型视觉质检与自动化回流平台",
        "model_path": str(settings.model_path),
        "model_exists": model_exists,
        "model_size_mb": model_size_mb,
        "class_names": class_names,
        "dataset": {
            "train_images": train_images,
            "val_images": val_images,
            "test_images": test_images,
            "total_images": train_images + val_images + test_images,
        },
        "metrics": _read_training_metrics(),
        "highlights": [
            "支持单图、批量、摄像头三种生鲜质检入口",
            "支持 .pt / .onnx 多模型上传、切换、对比与部署",
            "支持人工复核、bad case 回流、复训样本整理与批次导出",
            "支持标准样本包导出、部署评测与质检迭代闭环",
        ],
    }
