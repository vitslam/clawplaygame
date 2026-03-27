#!/bin/bash
# Phase 2 集成测试：API 触发 WebSocket 广播

BASE_URL="http://localhost:8001"
ROOM_ID="9b6b3577"
P1_ID="p1"
P2_ID="p2"

echo "============================================================"
echo "Phase 2 集成测试：API 触发 WebSocket 广播"
echo "============================================================"
echo ""

# 1. 玩家 1 加入
echo "[API] 玩家 1 加入房间..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d "{\"player_name\": \"玩家 A\", \"player_id\": \"$P1_ID\"}" | head -c 200
echo ""

# 2. 玩家 2 加入
echo "[API] 玩家 2 加入房间..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d "{\"player_name\": \"玩家 B\", \"player_id\": \"$P2_ID\"}" | head -c 200
echo ""

# 3. 发送消息
echo "[API] 玩家 1 发送消息..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/messages" \
  -H "Content-Type: application/json" \
  -d "{\"player_id\": \"$P1_ID\", \"content\": \"大家好！\", \"message_type\": \"chat\"}"
echo ""

# 4. 玩家 1 准备
echo "[API] 玩家 1 准备..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/toggle-ready" \
  -H "Content-Type: application/json" \
  -d "{\"player_id\": \"$P1_ID\"}"
echo ""

# 5. 玩家 2 准备
echo "[API] 玩家 2 准备..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/toggle-ready" \
  -H "Content-Type: application/json" \
  -d "{\"player_id\": \"$P2_ID\"}"
echo ""

# 6. 玩家 2 离开
echo "[API] 玩家 2 离开房间..."
curl -s -X POST "$BASE_URL/api/rooms/$ROOM_ID/leave?player_id=$P2_ID"
echo ""

echo ""
echo "============================================================"
echo "API 测试完成！"
echo "============================================================"
