"""upscale_image MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import UpscaleImageInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def upscale_image(payload: UpscaleImageInput) -> dict:
        """Upscale an image."""
        from app.tools._common import execute_tool
        return execute_tool('upscale_image', payload, provider.upscale_image, job_service)

    return upscale_image
