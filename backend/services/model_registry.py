from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


ALLOWED_MODEL_SUFFIXES = {
    ".pt": "pytorch",
    ".onnx": "onnx",
}
META_SUFFIX = ".meta.json"
BENCHMARK_META_KEYS = {
    "benchmarked_at",
    "benchmark_image_size",
    "benchmark_confidence_threshold",
    "benchmark_pytorch_average_ms",
    "benchmark_onnx_average_ms",
    "benchmark_speedup_vs_pytorch",
    "benchmark_tensorrt_average_ms",
    "benchmark_tensorrt_speedup_vs_pytorch",
}


class ModelRegistryService:
    def __init__(self, default_model_path: Path, model_store_dir: Path, default_data_config_path: Path | None = None) -> None:
        self.default_model_path = default_model_path.resolve()
        self.model_store_dir = model_store_dir.resolve()
        self.default_data_config_path = default_data_config_path.resolve() if default_data_config_path else None
        self.model_store_dir.mkdir(parents=True, exist_ok=True)
        self.active_record_path = self.model_store_dir / "active_model.json"
        self._ensure_active_record()

    def get_inventory(self) -> dict[str, Any]:
        models = self._collect_models()
        active = next((item for item in models if item["is_active"]), models[0])
        return {
            "active_model_id": active["id"],
            "active_model_name": active["name"],
            "active_model_path": active["path"],
            "active_model_type": active["type"],
            "active_class_names": active["class_names"],
            "models": models,
        }

    def get_active_model_path(self) -> Path:
        path = self._read_active_path()
        if path.exists():
            return path
        self._write_active_path(self.default_model_path)
        return self.default_model_path

    def get_active_descriptor(self) -> dict[str, Any]:
        inventory = self.get_inventory()
        active_id = inventory["active_model_id"]
        return next(item for item in inventory["models"] if item["id"] == active_id)

    def save_upload(
        self,
        filename: str,
        payload: bytes,
        yaml_filename: str | None = None,
        yaml_payload: bytes | None = None,
    ) -> dict[str, Any]:
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_MODEL_SUFFIXES:
            raise ValueError("仅支持上传 .pt 或 .onnx 模型文件。")

        safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", Path(filename).stem).strip("_") or "uploaded_model"
        target = self.model_store_dir / f"{safe_stem}{suffix}"
        index = 1
        while target.exists():
            target = self.model_store_dir / f"{safe_stem}_{index}{suffix}"
            index += 1

        target.write_bytes(payload)

        yaml_name = None
        class_names: list[str] = []
        if yaml_filename and yaml_payload:
            yaml_name = self._save_yaml_for_model(target, yaml_filename, yaml_payload)
            class_names = self._parse_class_names(yaml_payload)

        self._write_meta(target, {"yaml_name": yaml_name, "class_names": class_names})
        return self._descriptor_for_path(target, self.get_active_model_path())

    def update_descriptor_meta(self, model_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        models = self._collect_models()
        selected = next((item for item in models if item["id"] == model_id), None)
        if selected is None:
            raise ValueError("未找到要更新的模型。")

        model_path = Path(selected["path"])
        current_meta = self._read_meta(model_path)
        current_meta.update(
            {
                key: value
                for key, value in patch.items()
                if key in BENCHMARK_META_KEYS and value is not None
            }
        )
        if current_meta.get("yaml_name") is None:
            current_meta["yaml_name"] = selected.get("yaml_name")
        if current_meta.get("class_names") is None:
            current_meta["class_names"] = selected.get("class_names", [])
        self._write_meta(model_path, current_meta)
        return self._descriptor_for_path(model_path, self.get_active_model_path())

    def activate(self, model_id: str) -> dict[str, Any]:
        models = self._collect_models()
        selected = next((item for item in models if item["id"] == model_id), None)
        if selected is None:
            raise ValueError("未找到要启用的模型。")
        self._write_active_path(Path(selected["path"]))
        return self._descriptor_for_path(Path(selected["path"]), Path(selected["path"]))

    def delete(self, model_id: str) -> dict[str, Any]:
        models = self._collect_models()
        selected = next((item for item in models if item["id"] == model_id), None)
        if selected is None:
            raise ValueError("未找到要删除的模型。")
        if selected["is_default"]:
            raise ValueError("默认模型不能删除。")

        target = Path(selected["path"])
        self._delete_related_files(target)

        if selected["is_active"]:
            self._write_active_path(self.default_model_path)

        inventory = self.get_inventory()
        return {
            "deleted_model_id": selected["id"],
            "deleted_model_name": selected["name"],
            "active_model_id": inventory["active_model_id"],
            "active_model_name": inventory["active_model_name"],
            "active_model_type": inventory["active_model_type"],
            "active_class_names": inventory["active_class_names"],
            "message": "模型已删除，当前活动模型已更新。",
        }

    def _ensure_active_record(self) -> None:
        if self.active_record_path.exists():
            return
        self._write_active_path(self.default_model_path)

    def _read_active_path(self) -> Path:
        if not self.active_record_path.exists():
            return self.default_model_path
        try:
            data = json.loads(self.active_record_path.read_text(encoding="utf-8"))
        except Exception:
            return self.default_model_path

        raw_path = str(data.get("active_model_path", "")).strip()
        if not raw_path:
            return self.default_model_path
        return Path(raw_path).expanduser().resolve()

    def _write_active_path(self, path: Path) -> None:
        self.active_record_path.write_text(
            json.dumps({"active_model_path": str(path.resolve())}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _collect_models(self) -> list[dict[str, Any]]:
        active_path = self.get_active_model_path().resolve()
        candidates: list[Path] = [self.default_model_path]

        for path in sorted(self.model_store_dir.iterdir()):
            if not path.is_file():
                continue
            if path.name == self.active_record_path.name or path.name.endswith(META_SUFFIX):
                continue
            if path.suffix.lower() in ALLOWED_MODEL_SUFFIXES:
                candidates.append(path.resolve())

        unique_paths: list[Path] = []
        seen: set[str] = set()
        for path in candidates:
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            unique_paths.append(path.resolve())

        return [self._descriptor_for_path(path, active_path) for path in unique_paths]

    def _descriptor_for_path(self, path: Path, active_path: Path) -> dict[str, Any]:
        resolved = path.resolve()
        is_default = resolved == self.default_model_path
        source = "default" if is_default else "uploaded"
        identifier_prefix = "default" if is_default else "uploaded"
        metadata = self._read_meta(resolved)
        return {
            "id": f"{identifier_prefix}:{resolved.name}",
            "name": resolved.name,
            "path": str(resolved),
            "type": ALLOWED_MODEL_SUFFIXES.get(resolved.suffix.lower(), "unknown"),
            "size_mb": round(resolved.stat().st_size / (1024 * 1024), 4) if resolved.exists() else 0.0,
            "source": source,
            "is_default": is_default,
            "is_active": resolved == active_path,
            "can_delete": not is_default,
            "yaml_name": metadata.get("yaml_name"),
            "class_names": metadata.get("class_names", []),
            "benchmarked_at": metadata.get("benchmarked_at"),
            "benchmark_image_size": metadata.get("benchmark_image_size"),
            "benchmark_confidence_threshold": metadata.get("benchmark_confidence_threshold"),
            "benchmark_pytorch_average_ms": metadata.get("benchmark_pytorch_average_ms"),
            "benchmark_onnx_average_ms": metadata.get("benchmark_onnx_average_ms"),
            "benchmark_speedup_vs_pytorch": metadata.get("benchmark_speedup_vs_pytorch"),
            "benchmark_tensorrt_average_ms": metadata.get("benchmark_tensorrt_average_ms"),
            "benchmark_tensorrt_speedup_vs_pytorch": metadata.get("benchmark_tensorrt_speedup_vs_pytorch"),
        }

    def _read_meta(self, model_path: Path) -> dict[str, Any]:
        default_payload = {
            "yaml_name": self.default_data_config_path.name if self.default_data_config_path and self.default_data_config_path.exists() else None,
            "class_names": self._read_default_class_names() if model_path.resolve() == self.default_model_path else [],
            "benchmarked_at": None,
            "benchmark_image_size": None,
            "benchmark_confidence_threshold": None,
            "benchmark_pytorch_average_ms": None,
            "benchmark_onnx_average_ms": None,
            "benchmark_speedup_vs_pytorch": None,
            "benchmark_tensorrt_average_ms": None,
            "benchmark_tensorrt_speedup_vs_pytorch": None,
        }

        meta_path = self._meta_path(model_path)
        if not meta_path.exists():
            return default_payload

        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            return default_payload

        class_names = payload.get("class_names", [])
        if not isinstance(class_names, list):
            class_names = []

        return {
            **default_payload,
            "yaml_name": payload.get("yaml_name", default_payload["yaml_name"]),
            "class_names": [str(item) for item in class_names] or default_payload["class_names"],
            "benchmarked_at": str(payload.get("benchmarked_at") or "") or None,
            "benchmark_image_size": int(payload["benchmark_image_size"]) if payload.get("benchmark_image_size") is not None else None,
            "benchmark_confidence_threshold": float(payload["benchmark_confidence_threshold"]) if payload.get("benchmark_confidence_threshold") is not None else None,
            "benchmark_pytorch_average_ms": float(payload["benchmark_pytorch_average_ms"]) if payload.get("benchmark_pytorch_average_ms") is not None else None,
            "benchmark_onnx_average_ms": float(payload["benchmark_onnx_average_ms"]) if payload.get("benchmark_onnx_average_ms") is not None else None,
            "benchmark_speedup_vs_pytorch": float(payload["benchmark_speedup_vs_pytorch"]) if payload.get("benchmark_speedup_vs_pytorch") is not None else None,
            "benchmark_tensorrt_average_ms": float(payload["benchmark_tensorrt_average_ms"]) if payload.get("benchmark_tensorrt_average_ms") is not None else None,
            "benchmark_tensorrt_speedup_vs_pytorch": float(payload["benchmark_tensorrt_speedup_vs_pytorch"]) if payload.get("benchmark_tensorrt_speedup_vs_pytorch") is not None else None,
        }

    def _write_meta(self, model_path: Path, payload: dict[str, Any]) -> None:
        self._meta_path(model_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _delete_related_files(self, model_path: Path) -> None:
        for path in [model_path, self._meta_path(model_path), self._yaml_path(model_path)]:
            if path.exists() and path.is_file():
                path.unlink()

    def _save_yaml_for_model(self, model_path: Path, yaml_filename: str, yaml_payload: bytes) -> str:
        suffix = Path(yaml_filename).suffix.lower()
        if suffix not in {".yaml", ".yml"}:
            raise ValueError("类别映射文件仅支持 .yaml 或 .yml。")

        yaml_target = self._yaml_path(model_path)
        yaml_target.write_bytes(yaml_payload)
        return yaml_target.name

    def _parse_class_names(self, yaml_payload: bytes) -> list[str]:
        try:
            data = yaml.safe_load(yaml_payload.decode("utf-8"))
        except Exception as exc:
            raise ValueError(f"YAML 解析失败：{exc}") from exc

        names = data.get("names", []) if isinstance(data, dict) else []
        if isinstance(names, dict):
            ordered = [str(names[index]) for index in sorted(names, key=lambda item: int(item))]
            return ordered
        if isinstance(names, list):
            return [str(item) for item in names]
        return []

    def _read_default_class_names(self) -> list[str]:
        if not self.default_data_config_path or not self.default_data_config_path.exists():
            return []
        try:
            data = yaml.safe_load(self.default_data_config_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return []

        names = data.get("names", [])
        if isinstance(names, dict):
            return [str(names[index]) for index in sorted(names, key=lambda item: int(item))]
        if isinstance(names, list):
            return [str(item) for item in names]
        return []

    def _meta_path(self, model_path: Path) -> Path:
        return model_path.with_name(f"{model_path.name}{META_SUFFIX}")

    def _yaml_path(self, model_path: Path) -> Path:
        return model_path.with_suffix(".yaml")
