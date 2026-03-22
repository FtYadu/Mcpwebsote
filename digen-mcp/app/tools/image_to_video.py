"""image_to_video MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import ImageToVideoInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def image_to_video(payload: ImageToVideoInput) -> dict:
        """Animate an image into a video."""
        from app.tools._common import execute_tool
        return execute_tool('image_to_video', payload, provider.image_to_video, job_service)

    return image_to_video
