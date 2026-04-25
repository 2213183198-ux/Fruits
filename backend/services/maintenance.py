from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.services.history import HistoryService


ALLOWED_ARTIFACT_SUFFIXES = {".jpg", ".jpeg", ".png", ".csv", ".xlsx"}


class MaintenanceService:
    def __init__(self, artifacts_dir: Path, history_db_path: Path, history_service: HistoryService) -> None:
        self.artifacts_dir = artifacts_dir
        self.history_db_path = history_db_path
        self.history_service = history_service
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def get_storage_status(self) -> dict[str, Any]:
        artifacts = [self._to_payload(path) for path in self._iter_artifacts()]
        history_db = self._history_payload()
        return {
            "artifact_count": len(artifacts),
            "artifact_total_size_mb": round(sum(item["size_mb"] for item in artifacts), 4),
            "artifacts": artifacts,
            "history_db": history_db,
        }

    def cleanup(self, artifact_names: list[str], delete_all: bool, delete_history: bool) -> dict[str, Any]:
        deleted_files: list[str] = []
        skipped_files: list[str] = []
        target_paths = list(self._iter_artifacts()) if delete_all else self._resolve_paths(artifact_names)

        for path in target_paths:
            if not path.exists() or not path.is_file():
                continue
            try:
                path.unlink()
                deleted_files.append(path.name)
            except OSError:
                skipped_files.append(path.name)

        history_cleared = False
        if delete_history:
            self.history_service.reset_history()
            history_cleared = True

        return {
            "deleted_files": deleted_files,
            "skipped_files": skipped_files,
            "deleted_count": len(deleted_files),
            "history_cleared": history_cleared,
            "remaining_count": len(list(self._iter_artifacts())),
        }

    def _iter_artifacts(self):
        for path in sorted(self.artifacts_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in ALLOWED_ARTIFACT_SUFFIXES:
                yield path

    def _resolve_paths(self, artifact_names: list[str]) -> list[Path]:
        resolved: list[Path] = []
        root = self.artifacts_dir.resolve()
        for name in artifact_names:
            safe_name = Path(name).name
            path = (self.artifacts_dir / safe_name).resolve()
            if path.parent != root:
                continue
            if path.exists() and path.is_file() and path.suffix.lower() in ALLOWED_ARTIFACT_SUFFIXES:
                resolved.append(path)
        return resolved

    def _to_payload(self, path: Path) -> dict[str, Any]:
        return {
            "name": path.name,
            "type": path.suffix.lower().lstrip("."),
            "size_mb": round(path.stat().st_size / (1024 * 1024), 4),
            "download_url": f"/artifacts/{path.name}",
        }

    def _history_payload(self) -> dict[str, Any] | None:
        if not self.history_db_path.exists():
            return None
        return {
            "name": self.history_db_path.name,
            "type": "db",
            "size_mb": round(self.history_db_path.stat().st_size / (1024 * 1024), 4),
            "download_url": None,
        }
