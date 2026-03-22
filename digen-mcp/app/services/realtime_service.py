"""Realtime fan-out for websocket job notifications."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class RealtimeNotifier:
    """Tracks websocket subscribers per job identifier."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[job_id].append(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        if websocket in self._connections.get(job_id, []):
            self._connections[job_id].remove(websocket)
        if not self._connections.get(job_id):
            self._connections.pop(job_id, None)

    async def publish(self, job_id: str, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for websocket in list(self._connections.get(job_id, [])):
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(job_id, websocket)
