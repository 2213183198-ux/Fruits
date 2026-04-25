from __future__ import annotations

import csv
import json
import re
import sqlite3
import time
import zipfile
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any

from backend.config import settings


REVIEW_REQUIRED_STATUSES = {"warning", "critical", "failed", "no_detection"}


class HistoryService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS inspection_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    image_size INTEGER NOT NULL,
                    confidence_threshold REAL NOT NULL,
                    total_files INTEGER NOT NULL,
                    successful_files INTEGER NOT NULL,
                    failed_files INTEGER NOT NULL,
                    total_detections INTEGER NOT NULL,
                    csv_url TEXT,
                    excel_url TEXT
                );

                CREATE TABLE IF NOT EXISTS inspection_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_detections INTEGER NOT NULL,
                    rotten_rate REAL NOT NULL,
                    recommendation TEXT,
                    artifact_url TEXT,
                    error TEXT,
                    FOREIGN KEY (run_id) REFERENCES inspection_runs(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS inspection_item_reviews (
                    item_id INTEGER PRIMARY KEY,
                    review_status TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    notes TEXT,
                    feedback_status TEXT NOT NULL DEFAULT 'none',
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES inspection_items(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS retrain_catalog_items (
                    item_id INTEGER PRIMARY KEY,
                    catalog_status TEXT NOT NULL DEFAULT 'pending',
                    catalog_notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES inspection_items(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS retrain_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_name TEXT NOT NULL UNIQUE,
                    batch_status TEXT NOT NULL DEFAULT 'draft',
                    batch_notes TEXT,
                    export_name TEXT,
                    export_url TEXT,
                    exported_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS retrain_batch_items (
                    batch_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL UNIQUE,
                    added_at TEXT NOT NULL,
                    PRIMARY KEY (batch_id, item_id),
                    FOREIGN KEY (batch_id) REFERENCES retrain_batches(id) ON DELETE CASCADE,
                    FOREIGN KEY (item_id) REFERENCES retrain_catalog_items(item_id) ON DELETE CASCADE
                );

                """
            )
            self._ensure_column(connection, "inspection_runs", "source_model_name", "TEXT")
            self._ensure_column(connection, "inspection_runs", "source_model_type", "TEXT")
            self._ensure_column(connection, "retrain_catalog_items", "annotation_draft", "TEXT")
            self._ensure_column(connection, "retrain_catalog_items", "annotation_updated_at", "TEXT")

    def _ensure_column(self, connection: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
        columns = {str(row["name"]) for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()}
        if column_name not in columns:
            connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    def _generate_retrain_batch_name(self) -> str:
        return f"retrain_batch_{int(time.time() * 1000)}"

    def _load_json_dict(self, value: Any) -> dict[str, Any]:
        if not value:
            return {}
        try:
            payload = json.loads(str(value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _load_json_list(self, value: Any) -> list[dict[str, Any]]:
        if not value:
            return []
        try:
            payload = json.loads(str(value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        return [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []

    def _prune_empty_retrain_batches(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            DELETE FROM retrain_batches
            WHERE id IN (
                SELECT retrain_batches.id
                FROM retrain_batches
                LEFT JOIN retrain_batch_items ON retrain_batch_items.batch_id = retrain_batches.id
                GROUP BY retrain_batches.id
                HAVING COUNT(retrain_batch_items.item_id) = 0
            )
            """
        )

    def _make_safe_export_name(self, value: str, default: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value or "")).strip("_")
        return safe or default

    def _resolve_artifact_path(self, artifact_url: str | None) -> Path | None:
        artifact_name = Path(str(artifact_url or "")).name
        if not artifact_name:
            return None
        artifact_path = (settings.artifacts_dir / artifact_name).resolve()
        try:
            artifact_path.relative_to(settings.artifacts_dir.resolve())
        except ValueError:
            return None
        if not artifact_path.exists() or not artifact_path.is_file():
            return None
        return artifact_path

    def _derive_annotation_status(
        self,
        *,
        annotation_draft: str | None,
        review_decision: str | None,
        status: str | None,
    ) -> str:
        if str(annotation_draft or "").strip():
            return "drafted"
        if str(review_decision or "") == "false_positive":
            return "ready_empty"
        if str(review_decision or "") == "confirm" and str(status or "") == "no_detection":
            return "ready_empty"
        return "pending"

    def record_run(
        self,
        mode: str,
        image_size: int,
        confidence_threshold: float,
        results: list[dict[str, Any]],
        failures: list[dict[str, Any]],
        csv_url: str | None = None,
        excel_url: str | None = None,
        source_model_name: str | None = None,
        source_model_type: str | None = None,
    ) -> int:
        total_files = len(results) + len(failures)
        total_detections = sum(item["summary"]["total_detections"] for item in results)
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO inspection_runs (
                    mode,
                    created_at,
                    image_size,
                    confidence_threshold,
                    total_files,
                    successful_files,
                    failed_files,
                    total_detections,
                    csv_url,
                    excel_url,
                    source_model_name,
                    source_model_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mode,
                    created_at,
                    image_size,
                    confidence_threshold,
                    total_files,
                    len(results),
                    len(failures),
                    total_detections,
                    csv_url,
                    excel_url,
                    source_model_name,
                    source_model_type,
                ),
            )
            run_id = int(cursor.lastrowid)

            for item in results:
                connection.execute(
                    """
                    INSERT INTO inspection_items (
                        run_id,
                        filename,
                        status,
                        total_detections,
                        rotten_rate,
                        recommendation,
                        artifact_url,
                        error
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        item["filename"],
                        item["report"]["status"],
                        item["summary"]["total_detections"],
                        item["report"]["rotten_rate"],
                        item["report"]["recommendation"],
                        item.get("artifact_url"),
                        None,
                    ),
                )

            for item in failures:
                connection.execute(
                    """
                    INSERT INTO inspection_items (
                        run_id,
                        filename,
                        status,
                        total_detections,
                        rotten_rate,
                        recommendation,
                        artifact_url,
                        error
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        item["filename"],
                        "failed",
                        0,
                        0.0,
                        None,
                        None,
                        item["error"],
                    ),
                )

        return run_id

    def list_runs(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    mode,
                    created_at,
                    source_model_name,
                    source_model_type,
                    total_files,
                    successful_files,
                    failed_files,
                    total_detections,
                    csv_url,
                    excel_url
                FROM inspection_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_run(self, run_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            run = connection.execute(
                """
                SELECT
                    id,
                    mode,
                    created_at,
                    source_model_name,
                    source_model_type,
                    image_size,
                    confidence_threshold,
                    total_files,
                    successful_files,
                    failed_files,
                    total_detections,
                    csv_url,
                    excel_url
                FROM inspection_runs
                WHERE id = ?
                """,
                (run_id,),
            ).fetchone()

            if run is None:
                return None

            items = connection.execute(
                """
                SELECT
                    inspection_items.id,
                    filename,
                    status,
                    total_detections,
                    rotten_rate,
                    recommendation,
                    artifact_url,
                    error,
                    inspection_item_reviews.review_status,
                    inspection_item_reviews.decision AS review_decision,
                    inspection_item_reviews.notes AS review_notes,
                    inspection_item_reviews.feedback_status,
                    inspection_item_reviews.updated_at AS review_updated_at,
                    retrain_catalog_items.catalog_status AS retrain_status,
                    retrain_catalog_items.updated_at AS retrain_updated_at
                FROM inspection_items
                LEFT JOIN inspection_item_reviews ON inspection_item_reviews.item_id = inspection_items.id
                LEFT JOIN retrain_catalog_items ON retrain_catalog_items.item_id = inspection_items.id
                WHERE run_id = ?
                ORDER BY inspection_items.id ASC
                """,
                (run_id,),
            ).fetchall()

        payload = dict(run)
        payload["items"] = [self._normalize_history_item(dict(item)) for item in items]
        return payload

    def get_review_summary(self) -> dict[str, int]:
        items = self._load_review_items()
        summary = {
            "total": len(items),
            "pending": 0,
            "optional": 0,
            "reviewed": 0,
            "feedback": 0,
            "false_positive_count": 0,
            "missed_detection_count": 0,
            "needs_feedback_count": 0,
        }
        for item in items:
            status = str(item.get("review_status") or "optional")
            if status not in summary:
                pass
            else:
                summary[status] += 1
            decision = str(item.get("review_decision") or "")
            if decision == "false_positive":
                summary["false_positive_count"] += 1
            elif decision == "missed_detection":
                summary["missed_detection_count"] += 1
            elif decision == "needs_feedback":
                summary["needs_feedback_count"] += 1
        return summary

    def list_review_items(
        self,
        *,
        limit: int = 30,
        queue: str = "focus",
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> list[dict[str, Any]]:
        items = self._apply_review_filters(
            self._load_review_items(),
            queue=queue,
            decision=decision,
            mode=mode,
            keyword=keyword,
        )
        return items[:limit]

    def get_feedback_pool_summary(
        self,
        *,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> dict[str, Any]:
        items = self._apply_review_filters(
            self._load_review_items(),
            queue="feedback",
            decision=decision,
            mode=mode,
            keyword=keyword,
        )
        latest_updated_at = None
        if items:
            latest_updated_at = max(str(item.get("review_updated_at") or item.get("created_at") or "") for item in items) or None

        return {
            "total": len(items),
            "false_positive_count": sum(1 for item in items if item.get("review_decision") == "false_positive"),
            "missed_detection_count": sum(1 for item in items if item.get("review_decision") == "missed_detection"),
            "needs_feedback_count": sum(1 for item in items if item.get("review_decision") == "needs_feedback"),
            "single_count": sum(1 for item in items if item.get("mode") == "single"),
            "batch_count": sum(1 for item in items if item.get("mode") == "batch"),
            "webcam_count": sum(1 for item in items if item.get("mode") == "webcam"),
            "artifact_ready_count": sum(1 for item in items if item.get("artifact_url")),
            "avg_rotten_rate": round(sum(float(item.get("rotten_rate") or 0.0) for item in items) / len(items), 4) if items else 0.0,
            "latest_updated_at": latest_updated_at,
        }

    def get_review_item(self, item_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    inspection_items.id AS item_id,
                    inspection_items.run_id,
                    inspection_runs.mode,
                    inspection_runs.created_at,
                    inspection_runs.source_model_name,
                    inspection_runs.source_model_type,
                    inspection_runs.image_size,
                    inspection_runs.confidence_threshold,
                    inspection_items.filename,
                    inspection_items.status,
                    inspection_items.total_detections,
                    inspection_items.rotten_rate,
                    inspection_items.recommendation,
                    inspection_items.artifact_url,
                    inspection_items.error,
                    inspection_item_reviews.review_status,
                    inspection_item_reviews.decision AS review_decision,
                    inspection_item_reviews.notes AS review_notes,
                    inspection_item_reviews.feedback_status,
                    inspection_item_reviews.updated_at AS review_updated_at,
                    retrain_catalog_items.catalog_status AS retrain_status,
                    retrain_catalog_items.updated_at AS retrain_updated_at
                FROM inspection_items
                INNER JOIN inspection_runs ON inspection_runs.id = inspection_items.run_id
                LEFT JOIN inspection_item_reviews ON inspection_item_reviews.item_id = inspection_items.id
                LEFT JOIN retrain_catalog_items ON retrain_catalog_items.item_id = inspection_items.id
                WHERE inspection_items.id = ?
                """,
                (item_id,),
            ).fetchone()
        if row is None:
            return None
        return self._normalize_review_item(dict(row))

    def save_review_decision(
        self,
        item_id: int,
        *,
        decision: str,
        notes: str = "",
        send_to_feedback: bool = False,
    ) -> dict[str, Any] | None:
        item = self.get_review_item(item_id)
        if item is None:
            return None

        updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
        review_status = "feedback" if send_to_feedback else "reviewed"
        feedback_status = "queued" if send_to_feedback else "none"

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO inspection_item_reviews (
                    item_id,
                    review_status,
                    decision,
                    notes,
                    feedback_status,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    review_status = excluded.review_status,
                    decision = excluded.decision,
                    notes = excluded.notes,
                    feedback_status = excluded.feedback_status,
                    updated_at = excluded.updated_at
                """,
                (
                    item_id,
                    review_status,
                    decision,
                    notes.strip(),
                    feedback_status,
                    updated_at,
                ),
            )

        return self.get_review_item(item_id)

    def export_feedback_manifest(
        self,
        *,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> dict[str, Any]:
        items = self.list_review_items(
            limit=1000,
            queue="feedback",
            decision=decision,
            mode=mode,
            keyword=keyword,
        )
        settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
        export_name = f"feedback_pool_{int(time.time() * 1000)}.csv"
        export_path = settings.artifacts_dir / export_name

        with export_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=[
                    "item_id",
                    "run_id",
                    "mode",
                    "created_at",
                    "filename",
                    "status",
                    "review_status",
                    "review_decision",
                    "feedback_status",
                    "total_detections",
                    "rotten_rate",
                    "recommendation",
                    "artifact_url",
                    "review_notes",
                    "review_updated_at",
                ],
            )
            writer.writeheader()
            for item in items:
                writer.writerow(
                    {
                        "item_id": item["item_id"],
                        "run_id": item["run_id"],
                        "mode": item["mode"],
                        "created_at": item["created_at"],
                        "filename": item["filename"],
                        "status": item["status"],
                        "review_status": item["review_status"],
                        "review_decision": item.get("review_decision") or "",
                        "feedback_status": item.get("feedback_status") or "none",
                        "total_detections": item["total_detections"],
                        "rotten_rate": item["rotten_rate"],
                        "recommendation": item.get("recommendation") or item.get("error") or "",
                        "artifact_url": item.get("artifact_url") or "",
                        "review_notes": item.get("review_notes") or "",
                        "review_updated_at": item.get("review_updated_at") or "",
                    }
                )

        count = len(items)
        return {
            "export_name": export_name,
            "export_url": f"/artifacts/{export_name}",
            "item_count": count,
            "message": "已生成回流清单。" if count else "当前没有回流样本，已生成空清单。",
        }

    def get_retrain_catalog_summary(
        self,
        *,
        status: str | None = None,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> dict[str, Any]:
        items = self._apply_retrain_filters(
            self._load_retrain_items(),
            status=status,
            decision=decision,
            mode=mode,
            keyword=keyword,
        )
        latest_updated_at = max((str(item.get("catalog_updated_at") or "") for item in items), default="") or None
        return {
            "total": len(items),
            "pending": sum(1 for item in items if item.get("catalog_status") == "pending"),
            "ready": sum(1 for item in items if item.get("catalog_status") == "ready"),
            "used": sum(1 for item in items if item.get("catalog_status") == "used"),
            "false_positive_count": sum(1 for item in items if item.get("review_decision") == "false_positive"),
            "missed_detection_count": sum(1 for item in items if item.get("review_decision") == "missed_detection"),
            "needs_feedback_count": sum(1 for item in items if item.get("review_decision") == "needs_feedback"),
            "latest_updated_at": latest_updated_at,
        }

    def get_dashboard_summary(self, *, days: int = 7) -> dict[str, Any]:
        normalized_days = max(1, min(int(days or 7), 30))
        with self._connect() as connection:
            aggregate = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(total_files), 0) AS total_samples,
                    COALESCE(SUM(successful_files), 0) AS successful_samples,
                    COALESCE(SUM(failed_files), 0) AS failed_samples,
                    COALESCE(SUM(total_detections), 0) AS total_detections,
                    MAX(created_at) AS latest_run_at
                FROM inspection_runs
                """
            ).fetchone()

            quality_rows = connection.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM inspection_items
                GROUP BY status
                """
            ).fetchall()

            mode_rows = connection.execute(
                """
                SELECT mode, COALESCE(SUM(total_files), 0) AS sample_count
                FROM inspection_runs
                GROUP BY mode
                """
            ).fetchall()

            cutoff_date = (date.today() - timedelta(days=normalized_days - 1)).strftime("%Y-%m-%d")
            run_rows = connection.execute(
                """
                SELECT
                    substr(created_at, 1, 10) AS day,
                    COUNT(*) AS run_count,
                    COALESCE(SUM(total_files), 0) AS sample_count,
                    COALESCE(SUM(total_detections), 0) AS detection_count
                FROM inspection_runs
                WHERE substr(created_at, 1, 10) >= ?
                GROUP BY day
                ORDER BY day ASC
                """,
                (cutoff_date,),
            ).fetchall()

            feedback_rows = connection.execute(
                """
                SELECT
                    substr(updated_at, 1, 10) AS day,
                    COUNT(*) AS feedback_count
                FROM inspection_item_reviews
                WHERE feedback_status = 'queued' AND substr(updated_at, 1, 10) >= ?
                GROUP BY day
                ORDER BY day ASC
                """,
                (cutoff_date,),
            ).fetchall()

            retrain_rows = connection.execute(
                """
                SELECT
                    substr(created_at, 1, 10) AS day,
                    COUNT(*) AS retrain_count
                FROM retrain_catalog_items
                WHERE substr(created_at, 1, 10) >= ?
                GROUP BY day
                ORDER BY day ASC
                """,
                (cutoff_date,),
            ).fetchall()

        total_runs = int(aggregate["total_runs"] or 0)
        total_samples = int(aggregate["total_samples"] or 0)
        successful_samples = int(aggregate["successful_samples"] or 0)
        failed_samples = int(aggregate["failed_samples"] or 0)
        total_detections = int(aggregate["total_detections"] or 0)

        quality_status_counts = {key: 0 for key in ["pass", "warning", "critical", "no_detection", "failed"]}
        for row in quality_rows:
            status = str(row["status"])
            quality_status_counts[status] = int(row["count"] or 0)

        mode_sample_counts = {key: 0 for key in ["single", "batch", "webcam"]}
        for row in mode_rows:
            mode = str(row["mode"])
            mode_sample_counts[mode] = int(row["sample_count"] or 0)

        review_summary = self.get_review_summary()
        retrain_summary = self.get_retrain_catalog_summary()

        recent_daily_stats = self._build_recent_daily_stats(
            days=normalized_days,
            run_rows=run_rows,
            feedback_rows=feedback_rows,
            retrain_rows=retrain_rows,
        )

        return {
            "total_runs": total_runs,
            "total_samples": total_samples,
            "successful_samples": successful_samples,
            "failed_samples": failed_samples,
            "success_rate": round(successful_samples / total_samples, 4) if total_samples else 0.0,
            "total_detections": total_detections,
            "avg_detections_per_run": round(total_detections / total_runs, 4) if total_runs else 0.0,
            "avg_samples_per_run": round(total_samples / total_runs, 4) if total_runs else 0.0,
            "latest_run_at": aggregate["latest_run_at"],
            "quality_status_counts": quality_status_counts,
            "mode_sample_counts": mode_sample_counts,
            "review_pending_count": int(review_summary["pending"]),
            "reviewed_count": int(review_summary["reviewed"]),
            "feedback_queued_count": int(review_summary["feedback"]),
            "retrain_pending_count": int(retrain_summary["pending"]),
            "retrain_ready_count": int(retrain_summary["ready"]),
            "retrain_used_count": int(retrain_summary["used"]),
            "recent_daily_stats": recent_daily_stats,
        }

    def list_retrain_catalog_items(
        self,
        *,
        limit: int = 50,
        status: str | None = None,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> list[dict[str, Any]]:
        items = self._apply_retrain_filters(
            self._load_retrain_items(),
            status=status,
            decision=decision,
            mode=mode,
            keyword=keyword,
        )
        return items[:limit]

    def get_retrain_catalog_item(self, item_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    retrain_catalog_items.item_id,
                    inspection_items.run_id,
                    inspection_runs.mode,
                    inspection_runs.created_at AS source_created_at,
                    inspection_runs.source_model_name,
                    inspection_runs.source_model_type,
                    inspection_items.filename,
                    inspection_items.status,
                    inspection_items.total_detections,
                    inspection_items.rotten_rate,
                    inspection_items.recommendation,
                    inspection_items.artifact_url,
                    inspection_items.error,
                    inspection_item_reviews.review_status,
                    inspection_item_reviews.decision AS review_decision,
                    inspection_item_reviews.notes AS review_notes,
                    inspection_item_reviews.feedback_status,
                    retrain_catalog_items.catalog_status,
                    retrain_catalog_items.catalog_notes,
                    retrain_catalog_items.annotation_draft,
                    retrain_catalog_items.annotation_updated_at,
                    retrain_catalog_items.created_at AS catalog_created_at,
                    retrain_catalog_items.updated_at AS catalog_updated_at,
                    retrain_batches.id AS batch_id,
                    retrain_batches.batch_name,
                    retrain_batches.batch_status,
                    retrain_batches.export_url AS batch_export_url,
                    retrain_batches.exported_at AS batch_exported_at
                FROM retrain_catalog_items
                INNER JOIN inspection_items ON inspection_items.id = retrain_catalog_items.item_id
                INNER JOIN inspection_runs ON inspection_runs.id = inspection_items.run_id
                LEFT JOIN inspection_item_reviews ON inspection_item_reviews.item_id = inspection_items.id
                LEFT JOIN retrain_batch_items ON retrain_batch_items.item_id = retrain_catalog_items.item_id
                LEFT JOIN retrain_batches ON retrain_batches.id = retrain_batch_items.batch_id
                WHERE retrain_catalog_items.item_id = ?
                """,
                (item_id,),
            ).fetchone()
        if row is None:
            return None
        return self._normalize_retrain_item(dict(row))

    def upsert_retrain_catalog_item(
        self,
        item_id: int,
        *,
        catalog_status: str = "pending",
        catalog_notes: str = "",
        annotation_draft: str | None = None,
    ) -> dict[str, Any] | None:
        detail = self.get_review_item(item_id)
        if detail is None:
            return None
        if detail.get("feedback_status") != "queued" and detail.get("retrain_status") is None:
            raise ValueError("只有已加入回流的样本才能进入复训目录。")

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        current_detail = self.get_retrain_catalog_item(item_id)
        next_annotation_draft = (
            current_detail.get("annotation_draft") if current_detail and annotation_draft is None else (annotation_draft or None)
        )
        next_annotation_updated_at = (
            current_detail.get("annotation_updated_at")
            if current_detail and annotation_draft is None
            else (now if annotation_draft is not None else None)
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO retrain_catalog_items (
                    item_id,
                    catalog_status,
                    catalog_notes,
                    annotation_draft,
                    annotation_updated_at,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    catalog_status = excluded.catalog_status,
                    catalog_notes = excluded.catalog_notes,
                    annotation_draft = excluded.annotation_draft,
                    annotation_updated_at = excluded.annotation_updated_at,
                    updated_at = excluded.updated_at
                """,
                (
                    item_id,
                    catalog_status,
                    catalog_notes.strip(),
                    next_annotation_draft,
                    next_annotation_updated_at,
                    now,
                    now,
                ),
            )
        return self.get_retrain_catalog_item(item_id)

    def get_retrain_batch_summary(self) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COALESCE(SUM(CASE WHEN batch_status = 'draft' THEN 1 ELSE 0 END), 0) AS draft,
                    COALESCE(SUM(CASE WHEN batch_status = 'exported' THEN 1 ELSE 0 END), 0) AS exported,
                    COALESCE(MAX(exported_at), '') AS latest_exported_at
                FROM retrain_batches
                """
            ).fetchone()
            item_count_row = connection.execute("SELECT COUNT(*) AS total_items FROM retrain_batch_items").fetchone()
        return {
            "total": int(row["total"] or 0),
            "draft": int(row["draft"] or 0),
            "exported": int(row["exported"] or 0),
            "total_items": int(item_count_row["total_items"] or 0),
            "latest_exported_at": str(row["latest_exported_at"] or "") or None,
        }

    def list_retrain_batches(self, *, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    retrain_batches.id AS batch_id,
                    retrain_batches.batch_name,
                    retrain_batches.batch_status,
                    retrain_batches.created_at,
                    retrain_batches.updated_at,
                    retrain_batches.exported_at,
                    retrain_batches.export_url,
                    COUNT(retrain_batch_items.item_id) AS item_count
                FROM retrain_batches
                LEFT JOIN retrain_batch_items ON retrain_batch_items.batch_id = retrain_batches.id
                GROUP BY retrain_batches.id
                ORDER BY retrain_batches.updated_at DESC, retrain_batches.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "batch_id": int(row["batch_id"]),
                "batch_name": str(row["batch_name"]),
                "batch_status": str(row["batch_status"]),
                "item_count": int(row["item_count"] or 0),
                "created_at": str(row["created_at"]),
                "updated_at": str(row["updated_at"]),
                "exported_at": str(row["exported_at"] or "") or None,
                "export_url": row["export_url"],
            }
            for row in rows
        ]

    def get_retrain_batch(self, batch_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            batch = connection.execute(
                """
                SELECT
                    retrain_batches.id AS batch_id,
                    retrain_batches.batch_name,
                    retrain_batches.batch_status,
                    retrain_batches.batch_notes,
                    retrain_batches.export_name,
                    retrain_batches.export_url,
                    retrain_batches.created_at,
                    retrain_batches.updated_at,
                    retrain_batches.exported_at,
                    COUNT(retrain_batch_items.item_id) AS item_count
                FROM retrain_batches
                LEFT JOIN retrain_batch_items ON retrain_batch_items.batch_id = retrain_batches.id
                WHERE retrain_batches.id = ?
                GROUP BY retrain_batches.id
                """,
                (batch_id,),
            ).fetchone()
        if batch is None:
            return None

        items = [
            item
            for item in self._load_retrain_items()
            if int(item.get("batch_id") or 0) == int(batch_id)
        ]
        return {
            "batch_id": int(batch["batch_id"]),
            "batch_name": str(batch["batch_name"]),
            "batch_status": str(batch["batch_status"]),
            "item_count": int(batch["item_count"] or 0),
            "created_at": str(batch["created_at"]),
            "updated_at": str(batch["updated_at"]),
            "exported_at": str(batch["exported_at"] or "") or None,
            "export_url": batch["export_url"],
            "batch_notes": batch["batch_notes"],
            "export_name": batch["export_name"],
            "items": items,
        }

    def create_retrain_batch(
        self,
        *,
        batch_name: str = "",
        batch_notes: str = "",
        item_ids: list[int],
    ) -> dict[str, Any]:
        normalized_item_ids = sorted({int(item_id) for item_id in item_ids if int(item_id) > 0})
        if not normalized_item_ids:
            raise ValueError("请至少选择一个待复训样本。")

        normalized_name = batch_name.strip() or self._generate_retrain_batch_name()
        placeholders = ", ".join("?" for _ in normalized_item_ids)
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    retrain_catalog_items.item_id,
                    retrain_catalog_items.catalog_status,
                    retrain_batch_items.batch_id,
                    retrain_batches.batch_name
                FROM retrain_catalog_items
                LEFT JOIN retrain_batch_items ON retrain_batch_items.item_id = retrain_catalog_items.item_id
                LEFT JOIN retrain_batches ON retrain_batches.id = retrain_batch_items.batch_id
                WHERE retrain_catalog_items.item_id IN ({placeholders})
                """,
                normalized_item_ids,
            ).fetchall()

            if len(rows) != len(normalized_item_ids):
                raise ValueError("所选样本中存在未进入复训目录的记录。")

            invalid_status = [int(row["item_id"]) for row in rows if str(row["catalog_status"]) != "ready"]
            if invalid_status:
                raise ValueError("只有“待复训”状态的样本才能加入训练批次。")

            occupied = [str(row["batch_name"] or row["batch_id"]) for row in rows if row["batch_id"] is not None]
            if occupied:
                raise ValueError("所选样本中存在已加入训练批次的记录。")

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO retrain_batches (
                        batch_name,
                        batch_status,
                        batch_notes,
                        created_at,
                        updated_at
                    ) VALUES (?, 'draft', ?, ?, ?)
                    """,
                    (
                        normalized_name,
                        batch_notes.strip(),
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("训练批次名称已存在，请更换后重试。") from exc

            batch_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO retrain_batch_items (
                    batch_id,
                    item_id,
                    added_at
                ) VALUES (?, ?, ?)
                """,
                [(batch_id, item_id, now) for item_id in normalized_item_ids],
            )

        return self.get_retrain_batch(batch_id) or {}

    def export_retrain_batch(
        self,
        batch_id: int,
    ) -> dict[str, Any] | None:
        detail = self.get_retrain_batch(batch_id)
        if detail is None:
            return None

        items = detail.get("items", [])
        if not items:
            raise ValueError("当前训练批次没有可导出的样本。")

        settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
        exported_at = time.strftime("%Y-%m-%d %H:%M:%S")
        export_name = f"retrain_batch_{batch_id}_{int(time.time() * 1000)}.zip"
        export_path = settings.artifacts_dir / export_name

        package_root = self._make_safe_export_name(str(detail["batch_name"]), f"retrain_batch_{batch_id}")
        manifest_rows: list[dict[str, Any]] = []
        annotation_rows: list[dict[str, Any]] = []
        image_count = 0
        label_ready_count = 0
        label_labeled_count = 0
        label_empty_count = 0
        annotation_pending_count = 0
        artifact_missing_count = 0

        with zipfile.ZipFile(export_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for item in items:
                original_name = Path(str(item.get("filename") or f"item_{item['item_id']}")).name
                original_stem = Path(original_name).stem or f"item_{item['item_id']}"
                safe_stem = self._make_safe_export_name(original_stem, f"item_{item['item_id']}")
                extension = Path(original_name).suffix or ".jpg"
                export_basename = f"{int(item['item_id']):04d}_{safe_stem}{extension}"
                label_basename = f"{Path(export_basename).stem}.txt"

                image_rel_path = ""
                image_source = "missing"
                artifact_available = False
                artifact_path = self._resolve_artifact_path(item.get("artifact_url"))
                if artifact_path is not None:
                    image_rel_path = f"images/{export_basename}"
                    bundle.write(artifact_path, arcname=f"{package_root}/{image_rel_path}")
                    image_source = "annotated_artifact"
                    artifact_available = True
                    image_count += 1
                else:
                    artifact_missing_count += 1

                review_decision = str(item.get("review_decision") or "")
                annotation_draft = str(item.get("annotation_draft") or "").strip()
                annotation_status = str(item.get("annotation_status") or self._derive_annotation_status(
                    annotation_draft=annotation_draft,
                    review_decision=review_decision,
                    status=item.get("status"),
                ))
                label_status = "needs_manual_annotation"
                label_rel_path = ""
                if annotation_draft:
                    label_rel_path = f"labels/{label_basename}"
                    bundle.writestr(f"{package_root}/{label_rel_path}", annotation_draft.encode("utf-8"))
                    label_status = "ready_labeled"
                    label_ready_count += 1
                    label_labeled_count += 1
                elif review_decision == "false_positive" or (review_decision == "confirm" and str(item.get("status") or "") == "no_detection"):
                    label_rel_path = f"labels/{label_basename}"
                    bundle.writestr(f"{package_root}/{label_rel_path}", "")
                    label_status = "ready_empty"
                    label_ready_count += 1
                    label_empty_count += 1
                else:
                    annotation_pending_count += 1
                    annotation_rows.append(
                        {
                            "item_id": item["item_id"],
                            "filename": item["filename"],
                            "review_decision": review_decision or "needs_feedback",
                            "review_notes": item.get("review_notes") or "",
                            "catalog_notes": item.get("catalog_notes") or "",
                            "source_model_name": item.get("source_model_name") or "",
                            "image_rel_path": image_rel_path,
                            "artifact_available": "yes" if artifact_available else "no",
                            "annotation_status": annotation_status,
                            "annotation_updated_at": item.get("annotation_updated_at") or "",
                        }
                    )

                manifest_rows.append(
                    {
                        "batch_id": detail["batch_id"],
                        "batch_name": detail["batch_name"],
                        "item_id": item["item_id"],
                        "run_id": item["run_id"],
                        "mode": item["mode"],
                        "source_created_at": item["source_created_at"],
                        "filename": item["filename"],
                        "status": item["status"],
                        "review_decision": review_decision,
                        "catalog_status": item["catalog_status"],
                        "source_model_name": item.get("source_model_name") or "",
                        "source_model_type": item.get("source_model_type") or "",
                        "image_rel_path": image_rel_path,
                        "image_source": image_source,
                        "artifact_available": "yes" if artifact_available else "no",
                        "label_rel_path": label_rel_path,
                        "label_status": label_status,
                        "annotation_status": annotation_status,
                        "artifact_url": item.get("artifact_url") or "",
                        "annotation_updated_at": item.get("annotation_updated_at") or "",
                        "review_notes": item.get("review_notes") or "",
                        "catalog_notes": item.get("catalog_notes") or "",
                    }
                )

            manifest_stream = StringIO()
            manifest_writer = csv.DictWriter(
                manifest_stream,
                fieldnames=[
                    "batch_id",
                    "batch_name",
                    "item_id",
                    "run_id",
                    "mode",
                    "source_created_at",
                    "filename",
                    "status",
                    "review_decision",
                    "catalog_status",
                    "source_model_name",
                    "source_model_type",
                    "image_rel_path",
                    "image_source",
                    "artifact_available",
                    "label_rel_path",
                    "label_status",
                    "annotation_status",
                    "annotation_updated_at",
                    "artifact_url",
                    "review_notes",
                    "catalog_notes",
                ],
            )
            manifest_writer.writeheader()
            manifest_writer.writerows(manifest_rows)
            bundle.writestr(f"{package_root}/manifest.csv", manifest_stream.getvalue().encode("utf-8-sig"))

            annotation_stream = StringIO()
            annotation_writer = csv.DictWriter(
                annotation_stream,
                fieldnames=[
                    "item_id",
                    "filename",
                    "review_decision",
                    "review_notes",
                    "catalog_notes",
                    "source_model_name",
                    "image_rel_path",
                    "artifact_available",
                    "annotation_status",
                    "annotation_updated_at",
                ],
            )
            annotation_writer.writeheader()
            annotation_writer.writerows(annotation_rows)
            bundle.writestr(f"{package_root}/annotation_tasks.csv", annotation_stream.getvalue().encode("utf-8-sig"))

            meta_payload = {
                "schema_version": "retrain-batch-package.v1",
                "package_type": "training_sample_bundle",
                "package_stage": "annotation_ready",
                "exported_at": exported_at,
                "batch_id": int(detail["batch_id"]),
                "batch_name": str(detail["batch_name"]),
                "batch_notes": detail.get("batch_notes") or "",
                "item_count": len(items),
                "image_count": image_count,
                "label_ready_count": label_ready_count,
                "label_labeled_count": label_labeled_count,
                "label_empty_count": label_empty_count,
                "annotation_pending_count": annotation_pending_count,
                "artifact_missing_count": artifact_missing_count,
                "image_source": "annotated_artifact",
                "notes": [
                    "当前版本导出平台中可用的图像资产、manifest 和待标注任务清单。",
                    "false_positive 样本会生成空标签文件，可直接作为负样本使用。",
                    "missed_detection / needs_feedback 样本需要补标后再进入正式训练。",
                ],
            }
            bundle.writestr(
                f"{package_root}/meta.json",
                json.dumps(meta_payload, ensure_ascii=False, indent=2).encode("utf-8"),
            )

            readme_text = "\n".join(
                [
                    f"Batch: {detail['batch_name']}",
                    f"Exported At: {exported_at}",
                    "",
                    "Package Structure:",
                    "- images/: current available image assets exported by the platform",
                    "- labels/: label files that are already train-ready",
                    "- manifest.csv: full sample manifest",
                    "- annotation_tasks.csv: samples that still need manual annotation",
                    "- meta.json: package metadata and counts",
                    "",
                    "Label Status:",
                    "- ready_labeled: YOLO label draft already included in labels/",
                    "- ready_empty: can be used as empty-label negative sample",
                    "- needs_manual_annotation: should be annotated before training",
                ]
            )
            bundle.writestr(f"{package_root}/README.txt", readme_text.encode("utf-8"))

        export_url = f"/artifacts/{export_name}"
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE retrain_batches
                SET batch_status = 'exported',
                    export_name = ?,
                    export_url = ?,
                    exported_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    export_name,
                    export_url,
                    exported_at,
                    exported_at,
                    batch_id,
                ),
            )
            connection.execute(
                """
                UPDATE retrain_catalog_items
                SET catalog_status = 'used',
                    updated_at = ?
                WHERE item_id IN (
                    SELECT item_id FROM retrain_batch_items WHERE batch_id = ?
                )
                """,
                (
                    exported_at,
                    batch_id,
                ),
            )

        return {
            "batch_id": int(detail["batch_id"]),
            "batch_name": str(detail["batch_name"]),
            "export_name": export_name,
            "export_url": export_url,
            "item_count": len(items),
            "exported_at": exported_at,
            "message": f"训练批次 {detail['batch_name']} 已导出。",
        }

    def reset_history(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM retrain_batches")
            connection.execute("DELETE FROM inspection_items")
            connection.execute("DELETE FROM inspection_runs")

    def delete_runs(self, run_ids: list[int]) -> int:
        normalized_ids = sorted({int(run_id) for run_id in run_ids if int(run_id) > 0})
        if not normalized_ids:
            return 0

        placeholders = ", ".join("?" for _ in normalized_ids)
        with self._connect() as connection:
            connection.execute(
                f"DELETE FROM inspection_items WHERE run_id IN ({placeholders})",
                normalized_ids,
            )
            cursor = connection.execute(
                f"DELETE FROM inspection_runs WHERE id IN ({placeholders})",
                normalized_ids,
            )
            self._prune_empty_retrain_batches(connection)
        return int(cursor.rowcount or 0)

    def delete_runs_by_time_range(
        self,
        *,
        created_from: str | None = None,
        created_to: str | None = None,
    ) -> int:
        if not created_from and not created_to:
            return 0

        conditions: list[str] = []
        values: list[str] = []
        if created_from:
            conditions.append("created_at >= ?")
            values.append(created_from)
        if created_to:
            conditions.append("created_at <= ?")
            values.append(created_to)

        where_clause = " AND ".join(conditions)
        with self._connect() as connection:
            run_rows = connection.execute(
                f"SELECT id FROM inspection_runs WHERE {where_clause}",
                values,
            ).fetchall()
            run_ids = [int(row["id"]) for row in run_rows]

        return self.delete_runs(run_ids)

    def _normalize_history_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        review = self._normalize_review_fields(payload)
        return {
            "id": int(payload["id"]),
            "filename": payload["filename"],
            "status": payload["status"],
            "total_detections": int(payload["total_detections"]),
            "rotten_rate": float(payload["rotten_rate"]),
            "recommendation": payload.get("recommendation"),
            "artifact_url": payload.get("artifact_url"),
            "error": payload.get("error"),
            **review,
        }

    def _normalize_review_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        review = self._normalize_review_fields(payload)
        return {
            "item_id": int(payload["item_id"]),
            "run_id": int(payload["run_id"]),
            "mode": str(payload["mode"]),
            "created_at": str(payload["created_at"]),
            "source_model_name": payload.get("source_model_name"),
            "source_model_type": payload.get("source_model_type"),
            "image_size": int(payload["image_size"]),
            "confidence_threshold": float(payload["confidence_threshold"]),
            "filename": str(payload["filename"]),
            "status": str(payload["status"]),
            "total_detections": int(payload["total_detections"]),
            "rotten_rate": float(payload["rotten_rate"]),
            "recommendation": payload.get("recommendation"),
            "artifact_url": payload.get("artifact_url"),
            "error": payload.get("error"),
            **review,
        }

    def _normalize_retrain_item(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "item_id": int(payload["item_id"]),
            "run_id": int(payload["run_id"]),
            "mode": str(payload["mode"]),
            "source_created_at": str(payload["source_created_at"]),
            "filename": str(payload["filename"]),
            "source_model_name": payload.get("source_model_name"),
            "source_model_type": payload.get("source_model_type"),
            "status": str(payload["status"]),
            "total_detections": int(payload["total_detections"]),
            "rotten_rate": float(payload["rotten_rate"]),
            "recommendation": payload.get("recommendation"),
            "artifact_url": payload.get("artifact_url"),
            "error": payload.get("error"),
            "review_status": str(payload.get("review_status") or "optional"),
            "review_decision": payload.get("review_decision"),
            "feedback_status": str(payload.get("feedback_status") or "none"),
            "review_notes": payload.get("review_notes"),
            "catalog_status": str(payload["catalog_status"]),
            "catalog_notes": payload.get("catalog_notes"),
            "catalog_created_at": str(payload["catalog_created_at"]),
            "catalog_updated_at": str(payload["catalog_updated_at"]),
            "batch_id": int(payload["batch_id"]) if payload.get("batch_id") is not None else None,
            "batch_name": payload.get("batch_name"),
            "batch_status": payload.get("batch_status"),
            "batch_export_url": payload.get("batch_export_url"),
            "batch_exported_at": payload.get("batch_exported_at"),
            "annotation_status": self._derive_annotation_status(
                annotation_draft=payload.get("annotation_draft"),
                review_decision=payload.get("review_decision"),
                status=payload.get("status"),
            ),
            "annotation_updated_at": payload.get("annotation_updated_at"),
            "annotation_draft": payload.get("annotation_draft"),
        }

    def _normalize_review_fields(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw_status = payload.get("review_status")
        feedback_status = str(payload.get("feedback_status") or "none")
        if raw_status:
            review_status = str(raw_status)
        elif str(payload.get("status") or "") in REVIEW_REQUIRED_STATUSES:
            review_status = "pending"
        else:
            review_status = "optional"
        return {
            "review_status": review_status,
            "review_decision": payload.get("review_decision"),
            "review_notes": payload.get("review_notes"),
            "feedback_status": feedback_status,
            "review_updated_at": payload.get("review_updated_at"),
            "retrain_status": payload.get("retrain_status"),
            "retrain_updated_at": payload.get("retrain_updated_at"),
        }

    def _apply_review_filters(
        self,
        items: list[dict[str, Any]],
        *,
        queue: str = "focus",
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> list[dict[str, Any]]:
        if queue == "feedback":
            filtered = [item for item in items if item["feedback_status"] == "queued"]
        elif queue == "focus":
            filtered = [item for item in items if item["review_status"] in {"pending", "feedback"}]
        elif queue == "all":
            filtered = list(items)
        else:
            raise ValueError("queue 仅支持 focus、all 或 feedback。")

        if decision and decision != "all":
            allowed_decisions = {"false_positive", "missed_detection", "needs_feedback", "confirm"}
            if decision not in allowed_decisions:
                raise ValueError("decision 仅支持 all、false_positive、missed_detection、needs_feedback 或 confirm。")
            filtered = [item for item in filtered if item.get("review_decision") == decision]

        if mode and mode != "all":
            allowed_modes = {"single", "batch", "webcam"}
            if mode not in allowed_modes:
                raise ValueError("mode 仅支持 all、single、batch 或 webcam。")
            filtered = [item for item in filtered if item.get("mode") == mode]

        keyword_text = str(keyword or "").strip().lower()
        if keyword_text:
            filtered = [
                item
                for item in filtered
                if keyword_text in str(item.get("filename") or "").lower()
                or keyword_text in str(item.get("review_notes") or "").lower()
                or keyword_text in str(item.get("recommendation") or "").lower()
                or keyword_text in str(item.get("error") or "").lower()
            ]

        return filtered

    def _apply_retrain_filters(
        self,
        items: list[dict[str, Any]],
        *,
        status: str | None = None,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> list[dict[str, Any]]:
        filtered = list(items)

        if status and status != "all":
            allowed_statuses = {"pending", "ready", "used"}
            if status not in allowed_statuses:
                raise ValueError("status 仅支持 all、pending、ready 或 used。")
            filtered = [item for item in filtered if item.get("catalog_status") == status]

        if decision and decision != "all":
            allowed_decisions = {"false_positive", "missed_detection", "needs_feedback", "confirm"}
            if decision not in allowed_decisions:
                raise ValueError("decision 仅支持 all、false_positive、missed_detection、needs_feedback 或 confirm。")
            filtered = [item for item in filtered if item.get("review_decision") == decision]

        if mode and mode != "all":
            allowed_modes = {"single", "batch", "webcam"}
            if mode not in allowed_modes:
                raise ValueError("mode 仅支持 all、single、batch 或 webcam。")
            filtered = [item for item in filtered if item.get("mode") == mode]

        keyword_text = str(keyword or "").strip().lower()
        if keyword_text:
            filtered = [
                item
                for item in filtered
                if keyword_text in str(item.get("filename") or "").lower()
                or keyword_text in str(item.get("review_notes") or "").lower()
                or keyword_text in str(item.get("catalog_notes") or "").lower()
                or keyword_text in str(item.get("recommendation") or "").lower()
                or keyword_text in str(item.get("source_model_name") or "").lower()
                or keyword_text in str(item.get("batch_name") or "").lower()
            ]

        return filtered

    def _build_recent_daily_stats(
        self,
        *,
        days: int,
        run_rows: list[sqlite3.Row],
        feedback_rows: list[sqlite3.Row],
        retrain_rows: list[sqlite3.Row],
    ) -> list[dict[str, Any]]:
        date_keys = [
            (date.today() - timedelta(days=offset)).strftime("%Y-%m-%d")
            for offset in range(days - 1, -1, -1)
        ]
        run_map = {
            str(row["day"]): {
                "run_count": int(row["run_count"] or 0),
                "sample_count": int(row["sample_count"] or 0),
                "detection_count": int(row["detection_count"] or 0),
            }
            for row in run_rows
        }
        feedback_map = {str(row["day"]): int(row["feedback_count"] or 0) for row in feedback_rows}
        retrain_map = {str(row["day"]): int(row["retrain_count"] or 0) for row in retrain_rows}

        return [
            {
                "date": day,
                "run_count": run_map.get(day, {}).get("run_count", 0),
                "sample_count": run_map.get(day, {}).get("sample_count", 0),
                "detection_count": run_map.get(day, {}).get("detection_count", 0),
                "feedback_count": feedback_map.get(day, 0),
                "retrain_count": retrain_map.get(day, 0),
            }
            for day in date_keys
        ]

    def _load_review_items(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    inspection_items.id AS item_id,
                    inspection_items.run_id,
                    inspection_runs.mode,
                    inspection_runs.created_at,
                    inspection_runs.source_model_name,
                    inspection_runs.source_model_type,
                    inspection_runs.image_size,
                    inspection_runs.confidence_threshold,
                    inspection_items.filename,
                    inspection_items.status,
                    inspection_items.total_detections,
                    inspection_items.rotten_rate,
                    inspection_items.recommendation,
                    inspection_items.artifact_url,
                    inspection_items.error,
                    inspection_item_reviews.review_status,
                    inspection_item_reviews.decision AS review_decision,
                    inspection_item_reviews.notes AS review_notes,
                    inspection_item_reviews.feedback_status,
                    inspection_item_reviews.updated_at AS review_updated_at,
                    retrain_catalog_items.catalog_status AS retrain_status,
                    retrain_catalog_items.updated_at AS retrain_updated_at
                FROM inspection_items
                INNER JOIN inspection_runs ON inspection_runs.id = inspection_items.run_id
                LEFT JOIN inspection_item_reviews ON inspection_item_reviews.item_id = inspection_items.id
                LEFT JOIN retrain_catalog_items ON retrain_catalog_items.item_id = inspection_items.id
                ORDER BY inspection_items.id DESC
                """
            ).fetchall()
        return [self._normalize_review_item(dict(row)) for row in rows]

    def _load_retrain_items(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    retrain_catalog_items.item_id,
                    inspection_items.run_id,
                    inspection_runs.mode,
                    inspection_runs.created_at AS source_created_at,
                    inspection_runs.source_model_name,
                    inspection_runs.source_model_type,
                    inspection_items.filename,
                    inspection_items.status,
                    inspection_items.total_detections,
                    inspection_items.rotten_rate,
                    inspection_items.recommendation,
                    inspection_items.artifact_url,
                    inspection_items.error,
                    inspection_item_reviews.review_status,
                    inspection_item_reviews.decision AS review_decision,
                    inspection_item_reviews.notes AS review_notes,
                    inspection_item_reviews.feedback_status,
                    retrain_catalog_items.catalog_status,
                    retrain_catalog_items.catalog_notes,
                    retrain_catalog_items.annotation_draft,
                    retrain_catalog_items.annotation_updated_at,
                    retrain_catalog_items.created_at AS catalog_created_at,
                    retrain_catalog_items.updated_at AS catalog_updated_at,
                    retrain_batches.id AS batch_id,
                    retrain_batches.batch_name,
                    retrain_batches.batch_status,
                    retrain_batches.export_url AS batch_export_url,
                    retrain_batches.exported_at AS batch_exported_at
                FROM retrain_catalog_items
                INNER JOIN inspection_items ON inspection_items.id = retrain_catalog_items.item_id
                INNER JOIN inspection_runs ON inspection_runs.id = inspection_items.run_id
                LEFT JOIN inspection_item_reviews ON inspection_item_reviews.item_id = inspection_items.id
                LEFT JOIN retrain_batch_items ON retrain_batch_items.item_id = retrain_catalog_items.item_id
                LEFT JOIN retrain_batches ON retrain_batches.id = retrain_batch_items.batch_id
                ORDER BY retrain_catalog_items.updated_at DESC, retrain_catalog_items.item_id DESC
                """
            ).fetchall()
        return [self._normalize_retrain_item(dict(row)) for row in rows]


history_service = HistoryService(settings.history_db_path)
