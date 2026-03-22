"""edit_image MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import EditImageInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def edit_image(payload: EditImageInput) -> dict:
        """Edit an image from a source image URL and prompt."""
        from app.tools._common import execute_tool
        return execute_tool('edit_image', payload, provider.edit_image, job_service)

    return edit_image
