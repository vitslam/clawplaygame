#!/usr/bin/env python3
"""Phase 2 集成测试：API + WebSocket 广播"""

import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8001"

async def test_player(player_id: str, player_name: str, room_id: str, duration: int = 15):
    """模拟玩家连接 WebSocket"""
    uri = f"{WS_URL}/ws/rooms/{room_id}"
    print(f"[{player_name}] 连接 WebSocket...")
    
    events = []
    try:
        async with websockets.connect(uri) as ws:
            # 认证
            await ws.send(json.dumps({
                "type": "auth",
                "player_id": player_id,
                "player_name": player_name
            }))
            
            # 接收连接确认
            response = await ws.recv()
            print(f"[{player_name}] ✓ 已连接")
            
            # 监听事件
            end_time = asyncio.get_event_loop().time() + duration
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(msg)
                    event_type = data.get('type', 'unknown')
                    events.append(event_type)
                    print(f"[{player_name}] ← [{event_type}] {data.get('data', {})}")
                except asyncio.TimeoutError:
                    pass
            
            print(f"[{player_name}] 收到事件：{events}")
            return events
            
    except Exception as e:
        print(f"[{player_name}] ✗ 错误：{e}")
        return []


def test_api():
    """测试房间 API"""
    room_id = "test-phase2"
    player1_id = "p1"
    player2_id = "p2"
    
    print("\n" + "="*60)
    print("Phase 2 集成测试：API 触发 WebSocket 广播")
    print("="*60)
    
    # 1. 加入房间 - 玩家 1
    print("\n[API] 玩家 1 加入房间...")
    r = requests.post(f"{BASE_URL}/api/rooms/{room_id}/join", json={
        "player_name": "玩家 A",
        "player_id": player1_id
    })
    print(f"[API] 响应：{r.status_code}")
    
    # 2. 加入房间 - 玩家 2
    print("\n[API] 玩家 2 加入房间...")
    r = requests.post(f"{BASE_URL}/api/rooms/{room_id}/join", json={
        "player_name": "玩家 B",
        "player_id": player2_id
    })
    print(f"[API] 响应：{r.status_code}")
    
    # 3. 发送消息
    print("\n[API] 玩家 1 发送消息...")
    r = requests.post(f"{BASE_URL}/api/rooms/{room_id}/messages", json={
        "player_id": player1_id,
        "content": "大家好！",
        "message_type": "chat"
    })
    print(f"[API] 响应：{r.status_code}")
    
    # 4. 切换准备状态
    print("\n[API] 玩家 1 准备...")
    r = requests.post(f"{BASE_URL}/api/rooms/{room_id}/toggle-ready", json={
        "player_id": player1_id
    })
    print(f"[API] 响应：{r.status_code}")
    
    # 5. 玩家 2 准备
    print("\n[API] 玩家 2 准备...")
    r = requests.post(f"{BASE_URL}/api/rooms/{room_id}/toggle-ready", json={
        "player_id": player2_id
    })
    print(f"[API] 响应：{r.status_code}")
    
    # 6. 玩家 2 离开
    print("\n[API] 玩家 2 离开房间...")
    r = requests.post(f"{BASE_URL}/api/rooms/{room_id}/leave", params={
        "player_id": player2_id
    })
    print(f"[API] 响应：{r.status_code}")
    
    print("\n[API] 测试完成！")


async def main():
    # 先启动 WebSocket 监听
    p1 = asyncio.create_task(test_player("p1", "玩家 A", "test-phase2", duration=20))
    await asyncio.sleep(1)
    p2 = asyncio.create_task(test_player("p2", "玩家 B", "test-phase2", duration=18))
    
    await asyncio.sleep(2)
    
    # 执行 API 调用（在主线程）
    await asyncio.get_event_loop().run_in_executor(None, test_api)
    
    # 等待玩家完成
    await asyncio.gather(p1, p2)
    
    print("\n" + "="*60)
    print("Phase 2 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
