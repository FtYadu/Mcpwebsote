"""text_to_video MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import TextToVideoInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def text_to_video(payload: TextToVideoInput) -> dict:
        """Generate a video from a text prompt."""
        from app.tools._common import execute_tool
        return execute_tool('text_to_video', payload, provider.text_to_video, job_service)

    return text_to_video
