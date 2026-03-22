"""MCP resource for models metadata."""

from __future__ import annotations


def get_models_resource(provider) -> dict:
    """Return structured models resource content."""

    return provider.list_models().model_dump(mode='json')
