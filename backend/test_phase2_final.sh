#!/bin/bash
# Phase 2 最终测试

BASE_URL="http://localhost:8001"

echo "============================================================"
echo "Phase 2 最终测试：API + WebSocket 集成"
echo "============================================================"
echo ""

# 创建房间
echo "[1] 创建房间..."
ROOM_DATA=$(curl -s -X POST "$BASE_URL/api/rooms/werewolf/rooms" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "房主", "room_name": "Phase2 测试", "max_players": 10}')

ROOM_ID=$(echo $ROOM_DATA | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "    房间 ID: $ROOM_ID"
echo ""

# 玩家 1 加入
echo "[2] 玩家 1 加入..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 A", "player_id": "p1"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('    成功' if d.get('success') else d.get('detail','error'))"
echo ""

# 玩家 2 加入
echo "[3] 玩家 2 加入..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 B", "player_id": "p2"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('    成功' if d.get('success') else d.get('detail','error'))"
echo ""

# 发送消息
echo "[4] 发送消息..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "p1", "content": "大家好！", "message_type": "chat"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('    成功' if d.get('success') else 'error')"
echo ""

# 玩家 1 准备
echo "[5] 玩家 1 准备..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/toggle-ready" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "p1"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('    成功' if d.get('success') else d.get('detail','error'))"
echo ""

# 玩家 2 准备
echo "[6] 玩家 2 准备..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/toggle-ready" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "p2"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('    成功' if d.get('success') else d.get('detail','error'))"
echo ""

# 玩家 2 离开
echo "[7] 玩家 2 离开..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/leave?player_id=p2" | python3 -c "import sys,json; d=json.load(sys.stdin); print('    成功' if d.get('success') else d.get('detail','error'))"
echo ""

echo "============================================================"
echo "测试完成！"
echo "============================================================"
