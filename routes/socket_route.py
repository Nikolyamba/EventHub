from typing import List

import jwt
from jwt import PyJWTError
from fastapi import WebSocket, APIRouter, WebSocketDisconnect

from routes.jwt_auth import SECRET_KEY, ALGORITHM

ws_router = APIRouter()

class WebChat:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, event_id: int, websocket: WebSocket):
        await websocket.accept()
        if not event_id in self.active_connections:
            self.active_connections[event_id] = []
        self.active_connections[event_id].append(websocket)

    async def disconnect(self, event_id: int, websocket: WebSocket):
        self.active_connections[event_id].remove(websocket)

    async def send_message(self, event_id: int, message: str):
        if event_id in self.active_connections:
            for connection in self.active_connections[event_id]:
                await connection.send_text(message)

chat = WebChat()

@ws_router.websocket("/ws/event/{event_id}")
async def websocket_chat(event_id: int, websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")
    except PyJWTError:
        await websocket.close()
        return

    await chat.connect(event_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await chat.send_message(event_id, f"{login}: {data}")
    except WebSocketDisconnect:
        await chat.disconnect(event_id, websocket)
        await chat.send_message(event_id, f"{login} покинул чат")
