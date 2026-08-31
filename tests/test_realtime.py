import asyncio

from backend.fraudstream_backend.realtime import ConnectionManager


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.events = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, event):
        self.events.append(event)


def test_manager_accepts_and_broadcasts_events():
    async def scenario():
        manager = ConnectionManager()
        socket = FakeWebSocket()
        await manager.connect(socket)
        await manager.broadcast({"type": "alert", "id": 1})
        return socket

    socket = asyncio.run(scenario())
    assert socket.accepted is True
    assert socket.events == [{"type": "alert", "id": 1}]


def test_manager_removes_disconnected_socket():
    manager = ConnectionManager()
    socket = FakeWebSocket()
    manager.disconnect(socket)
    assert tuple(manager.connections) == ()

