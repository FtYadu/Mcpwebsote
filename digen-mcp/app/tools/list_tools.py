"""list_tools MCP tool."""

from __future__ import annotations


def register(mcp, provider, job_service):
    @mcp.tool()
    def list_tools() -> dict:
        """List provider tool support."""
        from app.models.errors import DigenError
        try:
            return provider.list_tools().model_dump(mode='json')
        except DigenError as exc:
            return exc.to_envelope().model_dump(mode='json')

    return list_tools
