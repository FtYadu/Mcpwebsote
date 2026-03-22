"""get_job_status MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import JobLookupInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def get_job_status(payload: JobLookupInput) -> dict:
        """Get current job status."""
        from app.tools._common import execute_tool
        return execute_tool('get_job_status', payload, provider.get_job_status, job_service)

    return get_job_status
