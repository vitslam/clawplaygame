#!/usr/bin/env python3
"""Phase 3 简单测试"""

import asyncio
import sys
import json
import websockets

BASE_URL = "ws://localhost:8001"
ROOM_ID = "4e32fcea"

async def test():
    print("=" * 60)
    print("Phase 3 测试：WebSocket 实时事件")
    print("=" * 60)
    
    uri = f"{BASE_URL}/ws/rooms/{ROOM_ID}"
    print(f"\n连接：{uri}")
    
    async with websockets.connect(uri) as ws:
        # 认证
        await ws.send(json.dumps({
            "type": "auth",
            "player_id": "phase3_test",
            "player_name": "Phase3 测试"
        }))
        
        # 等待确认
        response = await ws.recv()
        print(f"连接响应：{json.loads(response).get('type')}")
        
        # 监听 15 秒
        print("\n开始监听事件...\n")
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=15.0)
                data = json.loads(msg)
                event_type = data.get("type", "unknown")
                event_data = data.get("data", {})
                
                if event_type == "chat":
                    print(f"💬 [{event_data.get('player_name')}]: {event_data.get('content')}")
                elif event_type == "player_join":
                    print(f"👤 {event_data.get('player_name')} 加入")
                elif event_type == "player_leave":
                    print(f"👋 {event_data.get('player_name')} 离开")
                elif event_type == "player_ready":
                    print(f"✓ {event_data.get('player_name')} 准备")
                else:
                    print(f"📡 [{event_type}] {event_data}")
                    
        except asyncio.TimeoutError:
            print("\n监听超时")
    
    print("\n测试完成！")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
