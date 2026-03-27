#!/bin/bash
# 生产环境 WebSocket 测试

echo "============================================================"
echo "生产环境测试：clawplaygame.com"
echo "============================================================"
echo ""

# 1. 通过 API 创建房间
echo "[1] 创建房间..."
ROOM_DATA=$(curl -s -X POST "https://clawplaygame.com/api/rooms/werewolf/rooms" \
  -H "Content-Type: application/json" \
  -k \
  -d '{"player_name": "测试房主", "room_name": "生产环境测试", "max_players": 10}')

ROOM_ID=$(echo $ROOM_DATA | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "    房间 ID: $ROOM_ID"
echo "    访问地址：https://clawplaygame.com/room/$ROOM_ID"
echo ""

# 2. 启动 WebSocket 监听（后端直连）
echo "[2] WebSocket 监听测试（直连后端）..."
cd /home/admin/.openclaw/workspace/clawplaygame/backend && source .venv/bin/activate && timeout 10 python3 -c "
import asyncio, json, websockets
async def test():
    uri = 'ws://localhost:8001/ws/rooms/$ROOM_ID'
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({'type':'auth','player_id':'prod_test','player_name':'生产测试'}))
        await ws.recv()
        print('✓ WebSocket 已连接')
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=8.0)
                data = json.loads(msg)
                print(f'事件：{data.get(\"type\")} - {data.get(\"data\")}')
        except: pass
asyncio.run(test())
" 2>&1 &
WS_PID=$!
sleep 2
echo ""

# 3. 通过 API 发送消息
echo "[3] 发送消息..."
curl -s -X POST "https://clawplaygame.com/api/rooms/$ROOM_ID/messages" \
  -H "Content-Type: application/json" \
  -k \
  -d '{"player_id": "web_user", "content": "生产环境测试消息！", "message_type": "chat"}' | python3 -m json.tool
echo ""

# 4. 等待并显示 WebSocket 接收
echo "[4] 等待 WebSocket 接收..."
sleep 3
kill $WS_PID 2>/dev/null

echo ""
echo "============================================================"
echo "测试完成！"
echo "============================================================"
echo ""
echo "请打开浏览器访问："
echo "  https://clawplaygame.com/room/$ROOM_ID"
echo ""
echo "然后用 CLI 或 API 发送消息，前端应该能实时收到！"
