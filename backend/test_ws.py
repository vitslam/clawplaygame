#!/usr/bin/env python3
"""
WebSocket 测试脚本 - 验证 Phase 1 功能
用法：python test_ws.py
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_player(player_id: str, player_name: str, room_id: str = "test-room", duration: int = 10):
    """模拟一个玩家连接"""
    uri = f"ws://localhost:8000/ws/rooms/{room_id}"
    
    print(f"[{player_name}] 正在连接...")
    
    try:
        async with websockets.connect(uri) as ws:
            # 发送认证消息
            auth_msg = {
                "type": "auth",
                "player_id": player_id,
                "player_name": player_name
            }
            await ws.send(json.dumps(auth_msg))
            print(f"[{player_name}] 已发送认证")
            
            # 接收连接确认
            response = await ws.recv()
            data = json.loads(response)
            print(f"[{player_name}] 连接成功：{data.get('type')}")
            
            # 监听消息
            end_time = asyncio.get_event_loop().time() + duration
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(msg)
                    event_type = data.get('type', 'unknown')
                    event_data = data.get('data', {})
                    print(f"[{player_name}] ← [{event_type}] {event_data}")
                except asyncio.TimeoutError:
                    pass
            
            # 发送聊天消息
            chat_msg = {
                "type": "chat",
                "data": {
                    "content": f"{player_name} 说：大家好！时间：{datetime.now().strftime('%H:%M:%S')}"
                }
            }
            await ws.send(json.dumps(chat_msg))
            print(f"[{player_name}] → [chat] 发送了聊天消息")
            
            # 继续监听 3 秒
            end_time = asyncio.get_event_loop().time() + 3
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    data = json.loads(msg)
                    event_type = data.get('type', 'unknown')
                    event_data = data.get('data', {})
                    print(f"[{player_name}] ← [{event_type}] {event_data}")
                except asyncio.TimeoutError:
                    pass
            
            # 发送准备消息
            ready_msg = {
                "type": "ready",
                "data": {}
            }
            await ws.send(json.dumps(ready_msg))
            print(f"[{player_name}] → [ready] 发送了准备消息")
            
            # 最后监听 3 秒
            end_time = asyncio.get_event_loop().time() + 3
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    data = json.loads(msg)
                    event_type = data.get('type', 'unknown')
                    event_data = data.get('data', {})
                    print(f"[{player_name}] ← [{event_type}] {event_data}")
                except asyncio.TimeoutError:
                    pass
            
            print(f"[{player_name}] 测试完成")
            
    except Exception as e:
        print(f"[{player_name}] 错误：{e}")


async def main():
    print("=" * 60)
    print("ClawPlayGame WebSocket Phase 1 测试")
    print("=" * 60)
    print()
    
    # 启动两个玩家
    player1 = asyncio.create_task(test_player("p1", "玩家 A", duration=15))
    await asyncio.sleep(2)  # 错开连接时间
    player2 = asyncio.create_task(test_player("p2", "玩家 B", duration=12))
    
    await asyncio.gather(player1, player2)
    
    print()
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试中断")
    except Exception as e:
        print(f"\n测试失败：{e}")
        print("请确保后端服务已启动：cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
