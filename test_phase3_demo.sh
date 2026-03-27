#!/bin/bash
# Phase 3 完整演示

echo "============================================================"
echo "Phase 3 演示：CLI WebSocket 实时监听"
echo "============================================================"
echo ""

# 1. 创建房间
echo "[1] 创建房间..."
ROOM_DATA=$(curl -s -X POST "http://localhost:8001/api/rooms/werewolf/rooms" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "房主", "room_name": "Phase3 演示", "max_players": 10}')

ROOM_ID=$(echo $ROOM_DATA | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "    房间 ID: $ROOM_ID"
echo ""

# 2. 启动 WebSocket 监听（后台）
echo "[2] 启动 CLI WebSocket 监听（后台）..."
cd /home/admin/.openclaw/workspace/clawplaygame/tools/cli
nohup python3 test_ws_listen.py > /tmp/ws_listen.log 2>&1 &
LISTEN_PID=$!
echo "    监听进程 PID: $LISTEN_PID"
sleep 2
echo ""

# 3. 模拟玩家加入
echo "[3] 模拟玩家 A 加入..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 A", "player_id": "player_a"}' > /dev/null
sleep 1
echo ""

# 4. 模拟玩家 B 加入
echo "[4] 模拟玩家 B 加入..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 B", "player_id": "player_b"}' > /dev/null
sleep 1
echo ""

# 5. 发送聊天消息
echo "[5] 发送聊天消息..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player_a", "content": "大家好啊！", "message_type": "chat"}' > /dev/null
sleep 1
echo ""

# 6. 玩家 A 准备
echo "[6] 玩家 A 准备..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/toggle-ready" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player_a"}' > /dev/null
sleep 1
echo ""

# 7. 玩家 B 离开
echo "[7] 玩家 B 离开..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/leave?player_id=player_b" > /dev/null
sleep 2
echo ""

# 8. 显示监听日志
echo "[8] CLI 监听日志:"
echo "------------------------------------------------------------"
cat /tmp/ws_listen.log | grep -E "(💬|👤|👋|✓|✗|🚫)" || echo "暂无事件"
echo "------------------------------------------------------------"
echo ""

# 清理
kill $LISTEN_PID 2>/dev/null

echo "============================================================"
echo "演示完成！"
echo "============================================================"
