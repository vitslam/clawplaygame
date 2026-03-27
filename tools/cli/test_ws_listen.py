#!/usr/bin/env python3
"""测试 WebSocket 监听"""

import asyncio
import sys
sys.path.insert(0, '/home/admin/.openclaw/workspace/clawplaygame/tools/cli')

from ws_client import WSClient

async def test():
    print("=" * 60)
    print("Phase 3 测试：WebSocket 实时监听")
    print("=" * 60)
    
    # 创建客户端
    ws = WSClient(base_url="ws://localhost:8001")
    
    # 连接房间（用之前测试的房间）
    room_id = "bd9a5fcb"
    player_id = "cli_test"
    player_name = "CLI 测试玩家"
    
    print(f"\n连接房间：{room_id}")
    connected = await ws.connect(room_id, player_id, player_name)
    
    if not connected:
        print("连接失败！")
        return
    
    # 注册事件处理器
    def on_chat(data):
        content = data.get("data", {}).get("content", "")
        player = data.get("data", {}).get("player_name", "Unknown")
        print(f"💬 [{player}]: {content}")
    
    def on_join(data):
        player = data.get("data", {}).get("player_name", "Unknown")
        print(f"👤 {player} 加入了房间")
    
    def on_leave(data):
        player = data.get("data", {}).get("player_name", "Unknown")
        print(f"👋 {player} 离开了房间")
    
    def on_ready(data):
        player = data.get("data", {}).get("player_name", "Unknown")
        print(f"✓ {player} 已准备")
    
    ws.on_event("chat", on_chat)
    ws.on_event("player_join", on_join)
    ws.on_event("player_leave", on_leave)
    ws.on_event("player_ready", on_ready)
    ws.on_event("kicked", lambda d: print("🚫 被踢出房间"))
    
    print("\n开始监听事件（10 秒）...\n")
    
    # 监听 10 秒
    try:
        await asyncio.wait_for(ws.listen(timeout=10.0), timeout=12.0)
    except asyncio.TimeoutError:
        pass
    
    print("\n测试完成！")
    await ws.disconnect()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
