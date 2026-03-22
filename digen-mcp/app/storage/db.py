"""SQLite persistence for job records."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.models.jobs import JobRecord


class SQLiteJobStore:
    """Simple SQLite-backed job persistence."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    tool_name TEXT NOT NULL,
                    provider_name TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert_job(self, job: JobRecord) -> None:
        payload = job.model_dump(mode='json')
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs(job_id, tool_name, provider_name, payload)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    tool_name=excluded.tool_name,
                    provider_name=excluded.provider_name,
                    payload=excluded.payload
                """,
                (job.job_id, job.tool_name, job.provider_name, json.dumps(payload)),
            )
            conn.commit()

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT payload FROM jobs WHERE job_id = ?', (job_id,)).fetchone()
        if row is None:
            return None
        payload: dict[str, Any] = json.loads(row[0])
        return JobRecord.model_validate(payload)
