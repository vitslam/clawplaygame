from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import asyncio
import json
import gc
from datetime import datetime

from app.api import games, rooms, avalon, users
from app.websocket import manager
from app.api.rooms import init_mock_rooms

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

@app.on_event("startup")
async def startup_event():
    """启动时初始化预制房间"""
    init_mock_rooms()

# 注册路由（注意顺序：具体路由在前，通用路由在后）
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])  # 用户路由
app.include_router(rooms.router, prefix="/api/rooms", tags=["房间管理"])  # 房间路由
app.include_router(games.router, prefix="/api/games", tags=["游戏管理"])  # 游戏路由
app.include_router(avalon.router, prefix="/api/avalon", tags=["阿瓦隆游戏"])

# WebSocket 连接管理器
ws_manager = manager.WebSocketManager()

# 定时清理 + 内存管理（每 5 分钟）
async def maintenance_loop():
    while True:
        await asyncio.sleep(300)
        await ws_manager.cleanup_stale_connections()
        gc.collect()

@app.on_event("startup")
async def start_maintenance_task():
    """启动维护任务"""
    asyncio.create_task(maintenance_loop())


# 最大连接数限制
MAX_CONNECTIONS = 100

@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """游戏房间 WebSocket 连接"""
    # 检查连接数限制
    total_conns = sum(len(players) for players in ws_manager.rooms.values())
    if total_conns >= MAX_CONNECTIONS:
        await websocket.close(code=1013, reason="服务器已满")
        return
    
    await websocket.accept()
    
    player_id = None
    player_name = None
    
    try:
        # 等待认证消息（10 秒超时）
        try:
            raw_data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            auth_data = json.loads(raw_data)
            
            if auth_data.get("type") != "auth":
                await websocket.send_json({
                    "type": "error",
                    "message": "需要首先发送认证消息"
                })
                await websocket.close()
                return
            
            player_id = auth_data.get("player_id")
            player_name = auth_data.get("player_name", "")
            reconnect_token = auth_data.get("reconnect_token")
            
            if not player_id:
                await websocket.send_json({
                    "type": "error",
                    "message": "缺少 player_id"
                })
                await websocket.close()
                return
            
            # 建立连接
            success = await ws_manager.connect(
                websocket, room_id, player_id, player_name, reconnect_token
            )
            
            if not success:
                await websocket.close()
                return
            
            print(f"[WS] 玩家 {player_id} 认证成功")
            
            # 发送连接成功响应
            await websocket.send_json({
                "type": "connected",
                "player_id": player_id,
                "room_id": room_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # 广播新玩家加入
            await ws_manager.broadcast_event(
                room_id,
                manager.EventType.PLAYER_JOIN,
                {"player_id": player_id, "player_name": player_name}
            )
            
        except asyncio.TimeoutError:
            await websocket.send_json({
                "type": "error",
                "message": "认证超时"
            })
            await websocket.close()
            return
        
        # 主消息循环
        while True:
            data = await websocket.receive_text()
            print(f"[WS] 收到消息：{data}")
            
            try:
                msg = json.loads(data)
                
                # 处理心跳
                if msg.get("type") == "heartbeat":
                    ws_manager.update_heartbeat(room_id, player_id)
                    continue
                
                # 处理其他消息并广播
                await ws_manager.handle_message(room_id, player_id, msg)
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "无效的 JSON 格式"
                })
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, save_for_reconnect=True)
    except Exception:
        await ws_manager.disconnect(websocket, save_for_reconnect=True)


@app.get("/")
async def root():
    return {
        "message": "ClawPlayGame API",
        "docs": "/docs",
        "version": "0.1.0",
        "websocket": "/ws/rooms/{room_id}"
    }


@app.get("/health")
async def health_check():
    import resource
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ws_rooms": len(ws_manager.rooms),
        "ws_connections": sum(len(p) for p in ws_manager.rooms.values()),
        "memory_mb": round(rusage.ru_maxrss / 1024, 1)  # Linux returns KB
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
