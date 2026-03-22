"""Job orchestration service."""

from __future__ import annotations

from app.models.errors import DigenError
from app.models.jobs import JobRecord
from app.models.tool_outputs import DownloadResultOutput, JobAcceptedOutput, JobStatusOutput
from app.storage.db import SQLiteJobStore
from app.storage.redis_client import RedisBackedStateStore


class JobService:
    """Coordinates provider jobs, transient state, and durable persistence."""

    def __init__(self, db: SQLiteJobStore, transient_store: RedisBackedStateStore, provider_name: str) -> None:
        self._db = db
        self._transient = transient_store
        self._provider_name = provider_name

    def record_acceptance(self, tool_name: str, payload: dict, accepted: JobAcceptedOutput) -> JobAcceptedOutput:
        record = JobRecord(
            job_id=accepted.job_id,
            tool_name=tool_name,
            provider_name=self._provider_name,
            status=accepted.status,
            progress=0,
            stage='queued',
            input_payload=payload,
            output_payload=accepted.model_dump(mode='json'),
            preview_url=accepted.preview_url,
            result_url=accepted.result_url,
            error=None,
        )
        self._db.upsert_job(record)
        self._transient.set(accepted.job_id, record.model_dump(mode='json'))
        return accepted

    def update_status(self, status: JobStatusOutput) -> JobStatusOutput:
        existing = self._db.get_job(status.job_id)
        if existing is None:
            raise DigenError('JOB_NOT_FOUND', 'No job exists for the supplied job_id.', False)
        record = existing.model_copy(update={
            'status': status.status,
            'progress': status.progress,
            'stage': status.stage,
            'preview_url': status.preview_url,
            'result_url': status.result_url,
            'error': status.error,
            'output_payload': status.model_dump(mode='json'),
        })
        self._db.upsert_job(record)
        self._transient.set(status.job_id, record.model_dump(mode='json'))
        return status

    def store_download(self, download: DownloadResultOutput) -> DownloadResultOutput:
        existing = self._db.get_job(download.job_id)
        if existing is None:
            raise DigenError('JOB_NOT_FOUND', 'No job exists for the supplied job_id.', False)
        record = existing.model_copy(update={
            'status': download.status,
            'result_url': download.result_url,
            'output_payload': download.model_dump(mode='json'),
        })
        self._db.upsert_job(record)
        self._transient.set(download.job_id, record.model_dump(mode='json'))
        return download
