#!/bin/bash
# Phase 3 完整测试

echo "============================================================"
echo "Phase 3 完整测试：WebSocket + CLI"
echo "============================================================"
echo ""

# 1. 创建房间
echo "[1] 创建房间..."
ROOM_DATA=$(curl -s -X POST "http://localhost:8001/api/rooms/werewolf/rooms" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "房主", "room_name": "Phase3 完整测试", "max_players": 10}')

ROOM_ID=$(echo $ROOM_DATA | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "    房间 ID: $ROOM_ID"
echo ""

# 2. 玩家 A 加入
echo "[2] 玩家 A 加入..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 A", "player_id": "player_a"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('    成功' if d.get('success') else '失败')"
echo ""

# 3. 启动 WebSocket 监听（10 秒）
echo "[3] 启动 WebSocket 监听（10 秒）..."
cd /home/admin/.openclaw/workspace/clawplaygame
timeout 12 python3 -c "
import asyncio, sys, json, websockets
async def test():
    uri = 'ws://localhost:8001/ws/rooms/$ROOM_ID'
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({'type':'auth','player_id':'cli','player_name':'CLI'}))
        await ws.recv()  # 连接确认
        print('✓ 监听中...')
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=8.0)
                data = json.loads(msg)
                t = data.get('type','?')
                d = data.get('data',{})
                if t=='chat': print(f'💬 [{d.get(\"player_name\")}]: {d.get(\"content\")}')
                elif t=='player_join': print(f'👤 {d.get(\"player_name\")} 加入')
                elif t=='player_leave': print(f'👋 {d.get(\"player_name\")} 离开')
                elif t=='player_ready': print(f'✓ {d.get(\"player_name\")} 准备')
        except: pass
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
" 2>&1 &
LISTEN_PID=$!
sleep 2
echo ""

# 4. 玩家 B 加入（触发 WebSocket 事件）
echo "[4] 玩家 B 加入（应触发事件）..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/join" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 B", "player_id": "player_b"}' > /dev/null
sleep 1
echo ""

# 5. 发送消息
echo "[5] 发送聊天消息..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player_a", "content": "大家好！", "message_type": "chat"}' > /dev/null
sleep 1
echo ""

# 6. 玩家 A 准备
echo "[6] 玩家 A 准备..."
curl -s -X POST "http://localhost:8001/api/rooms/$ROOM_ID/toggle-ready" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player_a"}' > /dev/null
sleep 1
echo ""

# 7. 等待监听结束
echo "[7] 等待监听进程结束..."
wait $LISTEN_PID 2>/dev/null
echo ""

echo "============================================================"
echo "测试完成！"
echo "============================================================"
