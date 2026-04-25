from __future__ import annotations

import json
import sqlite3
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import Any, Callable

from backend.app.core.errors import AppError


TaskRunner = Callable[["TaskReporter"], dict[str, Any] | list[Any] | None]


class TaskReporter:
    def __init__(self, task_service: "TaskService", task_id: str) -> None:
        self.task_service = task_service
        self.task_id = task_id

    def running(self, message: str) -> None:
        self.task_service.mark_running(self.task_id, message=message)

    def progress(self, value: float, *, message: str | None = None) -> None:
        self.task_service.update_progress(self.task_id, value=value, message=message)

    def done(self, result: dict[str, Any] | list[Any] | None, *, message: str | None = None) -> None:
        self.task_service.mark_succeeded(self.task_id, result=result, message=message)

    def fail(self, *, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        self.task_service.mark_failed(self.task_id, code=code, message=message, details=details)


class TaskService:
    def __init__(self, db_path: Path, *, max_workers: int = 2) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._executor = ThreadPoolExecutor(max_workers=max(1, max_workers), thread_name_prefix="fruit-task")
        self._lock = Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS async_tasks (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    message TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    error_code TEXT,
                    error_message TEXT,
                    error_details TEXT,
                    request_payload TEXT,
                    result_payload TEXT
                )
                """
            )

    def submit(
        self,
        *,
        kind: str,
        runner: TaskRunner,
        request_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        task_id = uuid.uuid4().hex
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO async_tasks (
                    id,
                    kind,
                    status,
                    progress,
                    message,
                    created_at,
                    request_payload,
                    result_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    kind,
                    "queued",
                    0.0,
                    "任务已创建，等待执行。",
                    created_at,
                    self._dump_json(request_payload),
                    None,
                ),
            )

        self._executor.submit(self._run_task, task_id, runner)
        return self.get_task(task_id)

    def list_tasks(self, *, limit: int = 20, kind: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM async_tasks"
        conditions: list[str] = []
        values: list[Any] = []

        if kind:
            conditions.append("kind = ?")
            values.append(kind)
        if status:
            conditions.append("status = ?")
            values.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT ?"
        values.append(limit)

        with self._connect() as connection:
            rows = connection.execute(query, values).fetchall()
        return [self._row_to_payload(row) for row in rows]

    def get_task(self, task_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM async_tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise AppError(status_code=404, code="task_not_found", message="未找到对应任务。")
        return self._row_to_payload(row)

    def mark_running(self, task_id: str, *, message: str | None = None) -> None:
        self._update_task(
            task_id,
            status="running",
            started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            message=message or "任务执行中。",
        )

    def update_progress(self, task_id: str, *, value: float, message: str | None = None) -> None:
        self._update_task(task_id, progress=max(0.0, min(100.0, round(value, 2))), message=message)

    def mark_succeeded(
        self,
        task_id: str,
        *,
        result: dict[str, Any] | list[Any] | None,
        message: str | None = None,
    ) -> None:
        self._update_task(
            task_id,
            status="succeeded",
            progress=100.0,
            finished_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            message=message or "任务执行完成。",
            result_payload=self._dump_json(result),
            error_code=None,
            error_message=None,
            error_details=None,
        )

    def mark_failed(
        self,
        task_id: str,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self._update_task(
            task_id,
            status="failed",
            finished_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            message=message,
            error_code=code,
            error_message=message,
            error_details=self._dump_json(details),
        )

    def _run_task(self, task_id: str, runner: TaskRunner) -> None:
        reporter = TaskReporter(self, task_id)
        try:
            reporter.running("任务开始执行。")
            result = runner(reporter)
            current = self.get_task(task_id)
            if current["status"] != "failed":
                reporter.done(result, message="任务执行完成。")
        except AppError as exc:
            reporter.fail(code=exc.code, message=exc.message, details={"status_code": exc.status_code, "details": exc.details})
        except Exception as exc:
            reporter.fail(
                code="task_execution_failed",
                message=f"任务执行失败：{exc}",
                details={"traceback": traceback.format_exc()},
            )

    def _update_task(self, task_id: str, **fields: Any) -> None:
        if not fields:
            return

        with self._lock:
            assignments = ", ".join(f"{key} = ?" for key in fields)
            values = list(fields.values()) + [task_id]
            with self._connect() as connection:
                connection.execute(f"UPDATE async_tasks SET {assignments} WHERE id = ?", values)

    def _row_to_payload(self, row: sqlite3.Row) -> dict[str, Any]:
        payload = dict(row)
        payload["request_payload"] = self._load_json(payload.get("request_payload"))
        payload["result_payload"] = self._load_json(payload.get("result_payload"))
        payload["error_details"] = self._load_json(payload.get("error_details"))
        return payload

    def _dump_json(self, value: dict[str, Any] | list[Any] | None) -> str | None:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    def _load_json(self, value: str | None) -> dict[str, Any] | list[Any] | None:
        if not value:
            return None
        return json.loads(value)
