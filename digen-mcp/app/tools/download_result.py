"""download_result MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import JobLookupInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def download_result(payload: JobLookupInput) -> dict:
        """Get result download metadata for a completed job."""
        from app.tools._common import execute_tool
        return execute_tool('download_result', payload, provider.download_result, job_service)

    return download_result
