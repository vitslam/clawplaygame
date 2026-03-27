#!/usr/bin/env python3
"""WebSocket 调试测试 - 详细日志"""

import asyncio
import websockets
import json
import sys

async def test():
    uri = "ws://localhost:8001/ws/rooms/test-room"
    print(f"连接 {uri}...", file=sys.stderr)
    
    try:
        async with websockets.connect(uri) as ws:
            print("✓ 连接成功", file=sys.stderr)
            
            # 发送认证 - 用不同方式
            auth_msg = '{"type": "auth", "player_id": "test1", "player_name": "测试玩家"}'
            print(f"发送认证：{auth_msg}", file=sys.stderr)
            await ws.send(auth_msg)
            print("✓ 已发送认证", file=sys.stderr)
            
            # 等待一小会儿
            await asyncio.sleep(0.5)
            
            # 接收响应
            print("等待响应...", file=sys.stderr)
            response = await ws.recv()
            print(f"✓ 收到响应：{response}", file=sys.stderr)
            
            print("测试通过！", file=sys.stderr)
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"✗ 连接关闭：code={e.code}, reason={e.reason}", file=sys.stderr)
        print(f"  rcvd={e.rcvd_then_sent}", file=sys.stderr)
    except Exception as e:
        print(f"✗ 错误：{e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
