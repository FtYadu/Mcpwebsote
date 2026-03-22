"""get_account_credits MCP tool."""

from __future__ import annotations


def register(mcp, provider, job_service):
    @mcp.tool()
    def get_account_credits() -> dict:
        """Get account credit information when the provider supports it."""
        from app.models.errors import DigenError
        try:
            return provider.get_account_credits().model_dump(mode='json')
        except DigenError as exc:
            return exc.to_envelope().model_dump(mode='json')

    return get_account_credits
