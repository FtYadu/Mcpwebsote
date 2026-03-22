"""MCP resource for tools metadata."""

from __future__ import annotations


def get_tools_resource(provider) -> dict:
    return provider.list_tools().model_dump(mode='json')
