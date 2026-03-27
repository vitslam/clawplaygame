#!/bin/bash
# 端到端测试：CLI 发送消息 → 前端实时接收

echo "============================================================"
echo "端到端测试：CLI → WebSocket → 前端"
echo "============================================================"
echo ""

# 1. 创建房间
echo "[1] 创建房间..."
ROOM_DATA=$(curl -s -X POST "http://localhost:8001/api/rooms/werewolf/rooms" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "测试房主", "room_name": "E2E 测试", "max_players": 10}')

ROOM_ID=$(echo $ROOM_DATA | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "    房间 ID: $ROOM_ID"
echo ""

# 2. 前端页面加入房间（模拟）
echo "[2] 请在浏览器打开："
echo "    http://localhost:3003/room/$ROOM_ID"
echo ""
echo "    然后加入房间..."
echo ""
sleep 2

# 3. CLI 发送消息
echo "[3] CLI 发送消息..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "cli_test", "content": "前端能收到这条消息吗？", "message_type": "chat"}' | python3 -m json.tool
echo ""

# 4. CLI 发送第二条消息
echo "[4] CLI 发送第二条消息..."
sleep 2
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "cli_test", "content": "这是第二条测试消息！", "message_type": "chat"}' | python3 -m json.tool
echo ""

# 5. 玩家准备
echo "[5] 模拟玩家准备..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/toggle-ready" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "cli_test"}' | python3 -m json.tool
echo ""

echo "============================================================"
echo "测试完成！"
echo "============================================================"
echo ""
echo "请检查前端页面是否实时收到："
echo "  1. 'cli_test: 前端能收到这条消息吗？'"
echo "  2. 'cli_test: 这是第二条测试消息！'"
echo "  3. 'cli_test 已准备'"
echo ""
