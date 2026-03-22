"""upscale_video MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import UpscaleVideoInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def upscale_video(payload: UpscaleVideoInput) -> dict:
        """Upscale a video."""
        from app.tools._common import execute_tool
        return execute_tool('upscale_video', payload, provider.upscale_video, job_service)

    return upscale_video
