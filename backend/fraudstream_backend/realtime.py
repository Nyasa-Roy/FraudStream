from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class ConnectionManager:
    """Track WebSocket subscribers and broadcast JSON-compatible events."""

    def __init__(self) -> None:
        self._connections: set[Any] = set()

    async def connect(self, websocket: Any) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: Any) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, event: dict[str, Any]) -> None:
        stale: list[Any] = []
        for websocket in tuple(self._connections):
            try:
                await websocket.send_json(event)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)

    @property
    def connections(self) -> Iterable[Any]:
        return tuple(self._connections)

