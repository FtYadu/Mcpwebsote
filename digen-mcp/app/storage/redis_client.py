"""Transient job-state cache backed by Redis or memory."""

from __future__ import annotations

import json
from typing import Any

try:
    import redis
except ImportError:  # pragma: no cover - optional dependency at runtime
    redis = None


class RedisBackedStateStore:
    """Use Redis when available, otherwise fall back to an in-memory dict."""

    def __init__(self, redis_url: str | None) -> None:
        self._memory: dict[str, dict[str, Any]] = {}
        self._client = None
        if redis and redis_url:
            try:
                self._client = redis.from_url(redis_url, decode_responses=True)
                self._client.ping()
            except Exception:
                self._client = None

    def set(self, key: str, value: dict[str, Any]) -> None:
        if self._client is not None:
            self._client.set(key, json.dumps(value))
            return
        self._memory[key] = value

    def get(self, key: str) -> dict[str, Any] | None:
        if self._client is not None:
            payload = self._client.get(key)
            return json.loads(payload) if payload else None
        return self._memory.get(key)
