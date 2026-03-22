"""list_models MCP tool."""

from __future__ import annotations


def register(mcp, provider, job_service):
    @mcp.tool()
    def list_models() -> dict:
        """List provider models."""
        from app.models.errors import DigenError
        try:
            return provider.list_models().model_dump(mode='json')
        except DigenError as exc:
            return exc.to_envelope().model_dump(mode='json')

    return list_models
