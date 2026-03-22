"""Shared tool execution helpers."""

from __future__ import annotations

import logging
from collections.abc import Callable

from app.models.errors import DigenError
from app.services.job_service import JobService

LOGGER = logging.getLogger(__name__)


def execute_tool(tool_name: str, payload, handler: Callable, job_service: JobService | None = None) -> dict:
    """Execute a provider-backed tool and normalize the JSON response."""

    try:
        output = handler(payload) if payload is not None else handler()
        if job_service and hasattr(output, 'job_id'):
            if tool_name == 'get_job_status':
                output = job_service.update_status(output)
            elif tool_name == 'download_result':
                output = job_service.store_download(output)
            else:
                output = job_service.record_acceptance(tool_name, payload.model_dump(mode='json'), output)
        return output.model_dump(mode='json')
    except DigenError as exc:
        LOGGER.warning('tool=%s error=%s', tool_name, exc.detail.code)
        return exc.to_envelope().model_dump(mode='json')
    except Exception:
        LOGGER.exception('tool=%s unexpected error', tool_name)
        return DigenError('INTERNAL_ERROR', 'An unexpected internal error occurred.', False).to_envelope().model_dump(mode='json')
