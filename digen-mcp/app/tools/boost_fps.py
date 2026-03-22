"""boost_fps MCP tool."""

from __future__ import annotations

from app.models.tool_inputs import BoostFpsInput
from app.services.job_service import JobService


def register(mcp, provider, job_service: JobService):
    @mcp.tool()
    def boost_fps(payload: BoostFpsInput) -> dict:
        """Boost video FPS."""
        from app.tools._common import execute_tool
        return execute_tool('boost_fps', payload, provider.boost_fps, job_service)

    return boost_fps
