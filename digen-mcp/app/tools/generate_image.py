"""generate_image MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import GenerateImageInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def generate_image(payload: GenerateImageInput) -> dict:
        """Generate an image from a text prompt."""
        from app.tools._common import execute_tool
        return execute_tool('generate_image', payload, provider.generate_image, job_service)

    return generate_image
