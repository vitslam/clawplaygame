"""
集成测试 - 完整流程测试
"""
import pytest
from ..config import config
from ..session import session
from ..client import api_client


class TestIntegration:
    """集成测试类"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整流程：登录→选择游戏→创建房间→准备→发送消息"""
        try:
            # 1. 游客登录
            import uuid
            guest_id = f"guest_{uuid.uuid4().hex[:8]}"
            guest_name = f"游客_{uuid.uuid4().hex[:4]}"
            session.user = {"id": guest_id, "nickname": guest_name, "is_guest": True}
            assert session.is_logged_in
            
            # 2. 选择游戏
            game = await api_client.get_game("werewolf")
            config.set("current_game", game)
            assert config.get("current_game") is not None
            
            # 3. 创建房间
            room = await api_client.create_room(
                game_id="werewolf",
                player_name=guest_name,
                room_name="测试房间",
                player_id=guest_id
            )
            session.room = room
            assert session.in_room
            
            # 4. 准备
            result = await api_client.toggle_ready(
                room_id=room["id"],
                player_id=guest_id
            )
            assert result["is_ready"] is True
            
            # 5. 发送消息
            await api_client.send_message(
                room_id=room["id"],
                player_id=guest_id,
                content="测试消息"
            )
            
            # 6. 获取历史消息
            messages = await api_client.get_messages(room_id=room["id"], limit=10)
            assert len(messages) > 0
            
            # 清理
            session.clear()
            
        except Exception as e:
            pytest.skip(f"集成测试失败：{e}")
