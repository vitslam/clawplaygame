#!/usr/bin/env python3
"""简单的 WebSocket 测试"""

import asyncio
import websockets
import json

async def test_player(player_id: str, player_name: str, duration: int = 8):
    uri = "ws://localhost:8001/ws/rooms/test-room"
    print(f"[{player_name}] 连接中...")
    
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
            print(f"[{player_name}] ✓ 连接成功")
            
            # 监听消息
            end_time = asyncio.get_event_loop().time() + duration
            while asyncio.get_event_loop().time() < end_time:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(msg)
                    print(f"[{player_name}] ← [{data.get('type')}] {data.get('data', {})}")
                except asyncio.TimeoutError:
                    pass
            
            # 发送聊天
            await ws.send(json.dumps({
                "type": "chat",
                "data": {"content": f"{player_name} 大家好！"}
            }))
            print(f"[{player_name}] → 发送聊天")
            
            # 再监听一会儿
            await asyncio.sleep(2)
            print(f"[{player_name}] 测试完成")
            
    except Exception as e:
        print(f"[{player_name}] ✗ 错误：{e}")

async def main():
    print("=" * 50)
    print("WebSocket Phase 1 多玩家测试")
    print("=" * 50)
    
    # 启动两个玩家
    p1 = asyncio.create_task(test_player("p1", "玩家 A", duration=10))
    await asyncio.sleep(1)
    p2 = asyncio.create_task(test_player("p2", "玩家 B", duration=8))
    
    await asyncio.gather(p1, p2)
    
    print()
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
