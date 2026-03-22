"""Database-backed persistence for job records."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Protocol

from app.models.jobs import JobRecord

try:  # pragma: no cover - optional dependency
    import psycopg
    from psycopg.rows import tuple_row
except ImportError:  # pragma: no cover
    psycopg = None
    tuple_row = None


class JobStore(Protocol):
    def upsert_job(self, job: JobRecord) -> None: ...
    def get_job(self, job_id: str) -> JobRecord | None: ...
    def ping(self) -> dict[str, Any]: ...


class SQLiteJobStore:
    """SQLite-backed job persistence for local development."""

    backend = 'sqlite'

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

    def ping(self) -> dict[str, Any]:
        try:
            with self._connect() as conn:
                conn.execute('SELECT 1').fetchone()
            return {'ok': True, 'backend': self.backend, 'database': str(self._db_path)}
        except Exception as exc:  # pragma: no cover - defensive
            return {'ok': False, 'backend': self.backend, 'error': str(exc), 'database': str(self._db_path)}


class PostgresJobStore:
    """PostgreSQL-backed job persistence for concurrent production workloads."""

    backend = 'postgresql'

    def __init__(self, dsn: str) -> None:
        if psycopg is None:
            raise RuntimeError('psycopg is required to use the PostgreSQL job store')
        self._dsn = dsn
        self._initialize()

    def _connect(self):  # pragma: no cover - exercised in environments with postgres available
        return psycopg.connect(self._dsn, row_factory=tuple_row)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    tool_name TEXT NOT NULL,
                    provider_name TEXT NOT NULL,
                    payload JSONB NOT NULL
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
                VALUES(%s, %s, %s, %s::jsonb)
                ON CONFLICT(job_id) DO UPDATE SET
                    tool_name=EXCLUDED.tool_name,
                    provider_name=EXCLUDED.provider_name,
                    payload=EXCLUDED.payload
                """,
                (job.job_id, job.tool_name, job.provider_name, json.dumps(payload)),
            )
            conn.commit()

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT payload FROM jobs WHERE job_id = %s', (job_id,)).fetchone()
        if row is None:
            return None
        payload: dict[str, Any] = row[0]
        return JobRecord.model_validate(payload)

    def ping(self) -> dict[str, Any]:
        try:
            with self._connect() as conn:
                conn.execute('SELECT 1').fetchone()
            return {'ok': True, 'backend': self.backend, 'database_url': self._dsn}
        except Exception as exc:  # pragma: no cover - defensive
            return {'ok': False, 'backend': self.backend, 'database_url': self._dsn, 'error': str(exc)}


def create_job_store(database_url: str | None, sqlite_path: Path) -> JobStore:
    """Create the appropriate job store for the configured runtime."""

    if database_url:
        return PostgresJobStore(database_url)
    return SQLiteJobStore(sqlite_path)
