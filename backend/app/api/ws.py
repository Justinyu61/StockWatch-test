from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

# 連線管理
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, symbol: str, data: dict):
        payload = json.dumps({"symbol": symbol, **data})
        for ws in self.active:
            try:
                await ws.send_text(payload)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/stocks")
async def stock_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # 保持連線
    except WebSocketDisconnect:
        manager.disconnect(websocket)
