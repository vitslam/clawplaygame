from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import asyncio
import json
from datetime import datetime

from app.api import games, rooms, avalon
from app.websocket import manager

app = FastAPI(
    title="ClawPlayGame API",
    description="游戏平台后端 API - 支持狼人杀、阿瓦隆、血染钟楼等社交推理游戏",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(games.router, prefix="/api/games", tags=["游戏管理"])
app.include_router(rooms.router, prefix="/api/games", tags=["房间管理"])
app.include_router(avalon.router, prefix="/api/avalon", tags=["阿瓦隆游戏"])

# WebSocket 连接管理器
websocket_manager = manager.WebSocketManager()


@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """游戏房间 WebSocket 连接"""
    await websocket_manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # 广播消息给房间内所有玩家
            await websocket_manager.broadcast(room_id, {
                "type": "message",
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, room_id)
        await websocket_manager.broadcast(room_id, {
            "type": "player_left",
            "player_id": websocket_manager.get_player_id(websocket),
            "timestamp": datetime.now().isoformat()
        })


@app.get("/")
async def root():
    return {
        "message": "ClawPlayGame API",
        "docs": "/docs",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
