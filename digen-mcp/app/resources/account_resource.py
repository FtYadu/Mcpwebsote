"""MCP resource for account credit metadata."""

from __future__ import annotations

from app.models.errors import DigenError


def get_account_resource(provider) -> dict:
    try:
        return provider.get_account_credits().model_dump(mode='json')
    except DigenError as exc:
        return exc.to_envelope().model_dump(mode='json')
