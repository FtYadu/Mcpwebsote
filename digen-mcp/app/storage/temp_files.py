"""Temporary file helpers."""

from __future__ import annotations

from pathlib import Path


class TempFileStore:
    """Manage local temp directories for provider artifacts."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def ensure_job_dir(self, job_id: str) -> Path:
        path = self.base_dir / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path
