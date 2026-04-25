from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _path_from_env(name: str, default: Path) -> Path:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return Path(raw_value).expanduser().resolve()


def _float_from_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return float(raw_value)


def _int_from_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return int(raw_value)


@dataclass(frozen=True)
class Settings:
    project_root: Path
    model_path: Path
    onnx_model_path: Path
    data_config_path: Path
    training_results_path: Path
    artifacts_dir: Path
    model_store_dir: Path
    history_db_path: Path
    quality_rules_path: Path
    default_image_size: int
    default_confidence: float
    background_task_workers: int


settings = Settings(
    project_root=PROJECT_ROOT,
    model_path=_path_from_env(
        "FRUIT_MODEL_PATH",
        PROJECT_ROOT / "runs" / "train" / "fruit_quality_check" / "weights" / "best.pt",
    ),
    onnx_model_path=_path_from_env(
        "FRUIT_ONNX_MODEL_PATH",
        PROJECT_ROOT / "runs" / "train" / "fruit_quality_check" / "weights" / "best.onnx",
    ),
    data_config_path=_path_from_env("FRUIT_DATA_CONFIG_PATH", PROJECT_ROOT / "data.yaml"),
    training_results_path=_path_from_env(
        "FRUIT_RESULTS_CSV_PATH",
        PROJECT_ROOT / "runs" / "train" / "fruit_quality_check" / "results.csv",
    ),
    artifacts_dir=_path_from_env("FRUIT_ARTIFACTS_DIR", PROJECT_ROOT / "backend" / "artifacts"),
    model_store_dir=_path_from_env("FRUIT_MODEL_STORE_DIR", PROJECT_ROOT / "backend" / "models"),
    history_db_path=_path_from_env("FRUIT_HISTORY_DB_PATH", PROJECT_ROOT / "backend" / "artifacts" / "history.db"),
    quality_rules_path=_path_from_env(
        "FRUIT_QUALITY_RULES_PATH",
        PROJECT_ROOT / "backend" / "runtime" / "quality_rules.json",
    ),
    default_image_size=_int_from_env("FRUIT_DEFAULT_IMGSZ", 416),
    default_confidence=_float_from_env("FRUIT_DEFAULT_CONF", 0.25),
    background_task_workers=_int_from_env("FRUIT_BACKGROUND_TASK_WORKERS", 2),
)
