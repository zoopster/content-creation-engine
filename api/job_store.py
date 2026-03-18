"""
Persistent SQLite-backed job store for workflow jobs.

Provides a write-through in-memory cache so all in-flight reads/writes
are fast, while completed jobs survive server restarts.
"""

import json
import logging
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple

from api.schemas.workflow import (
    WorkflowJobStatus,
    WorkflowResultResponse,
    WorkflowStepProgress,
)

logger = logging.getLogger(__name__)


@dataclass
class FileRecord:
    """Lightweight record of a production output file."""
    file_path: str
    file_format: str


class SQLiteJobStore:
    """
    Write-through in-memory + SQLite job store.

    The in-memory cache is the primary read/write surface.
    Call save(job_id) to flush the current in-memory state to SQLite.
    On startup, _load_from_db() reloads all persisted jobs so state
    survives server restarts.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._cache: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._init_db()
        self._load_from_db()

    # ------------------------------------------------------------------
    # Dict-like interface (keeps WorkflowService unchanged)
    # ------------------------------------------------------------------

    def __contains__(self, job_id: str) -> bool:
        return job_id in self._cache

    def __getitem__(self, job_id: str) -> dict:
        return self._cache[job_id]

    def get(self, job_id: str, default: Any = None) -> Any:
        return self._cache.get(job_id, default)

    def items(self) -> Iterator[Tuple[str, dict]]:
        return self._cache.items()

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def create_job(self, job_id: str, data: dict) -> None:
        """Insert a new job into cache and SQLite."""
        self._cache[job_id] = data
        self._persist(job_id, data)

    def save(self, job_id: str) -> None:
        """Flush the current in-memory state of a job to SQLite."""
        if job_id in self._cache:
            try:
                self._persist(job_id, self._cache[job_id])
            except Exception as exc:
                logger.error(f"Failed to persist job {job_id}: {exc}")

    def list_jobs(self) -> List[dict]:
        """Return lightweight summary rows for all jobs (from SQLite)."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT job_id, status, progress, current_step, created_at "
                "FROM jobs ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Internal persistence
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id       TEXT PRIMARY KEY,
                    status       TEXT NOT NULL,
                    progress     INTEGER NOT NULL DEFAULT 0,
                    current_step TEXT,
                    steps_json   TEXT NOT NULL DEFAULT '[]',
                    result_json  TEXT,
                    error        TEXT,
                    files_json   TEXT NOT NULL DEFAULT '[]',
                    created_at   TEXT NOT NULL
                )
            """)

    def _connect(self):
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _persist(self, job_id: str, data: dict) -> None:
        status = data.get("status", WorkflowJobStatus.PENDING)
        status_str = status.value if isinstance(status, WorkflowJobStatus) else str(status)

        steps = data.get("steps_completed", [])
        steps_json = json.dumps(
            [s.model_dump() if hasattr(s, "model_dump") else s for s in steps],
            default=str,
        )

        result = data.get("result")
        result_json: Optional[str] = None
        if result is not None:
            if hasattr(result, "model_dump_json"):
                result_json = result.model_dump_json()
            else:
                result_json = json.dumps(result, default=str)

        files = data.get("files", [])
        files_list = []
        for f in files:
            if isinstance(f, dict):
                files_list.append(f)
            elif isinstance(f, FileRecord):
                files_list.append({"file_path": f.file_path, "file_format": f.file_format})
            else:
                files_list.append({
                    "file_path": getattr(f, "file_path", ""),
                    "file_format": getattr(f, "file_format", ""),
                })
        files_json = json.dumps(files_list)

        created_at = data.get("created_at", datetime.now())
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs
                    (job_id, status, progress, current_step, steps_json,
                     result_json, error, files_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    status       = excluded.status,
                    progress     = excluded.progress,
                    current_step = excluded.current_step,
                    steps_json   = excluded.steps_json,
                    result_json  = excluded.result_json,
                    error        = excluded.error,
                    files_json   = excluded.files_json
                """,
                (
                    job_id,
                    status_str,
                    data.get("progress", 0),
                    data.get("current_step", ""),
                    steps_json,
                    result_json,
                    data.get("error"),
                    files_json,
                    created_at,
                ),
            )

    def _load_from_db(self) -> None:
        """Reload all persisted jobs into in-memory cache on startup."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM jobs").fetchall()

        for row in rows:
            try:
                self._cache[row["job_id"]] = self._deserialize(dict(row))
            except Exception as exc:
                logger.warning(
                    f"Skipping corrupt job record {row['job_id']}: {exc}",
                    exc_info=True,
                )

    def _deserialize(self, row: dict) -> dict:
        job = dict(row)

        job["status"] = WorkflowJobStatus(job["status"])

        steps_data = json.loads(job.pop("steps_json", None) or "[]")
        job["steps_completed"] = [WorkflowStepProgress(**s) for s in steps_data]

        result_json = job.pop("result_json", None)
        job["result"] = (
            WorkflowResultResponse.model_validate_json(result_json)
            if result_json
            else None
        )

        files_data = json.loads(job.pop("files_json", None) or "[]")
        job["files"] = [FileRecord(**f) for f in files_data]

        if isinstance(job.get("created_at"), str):
            job["created_at"] = datetime.fromisoformat(job["created_at"])

        return job
