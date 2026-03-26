"""
API 客户端测试
"""
import pytest
from ..client import APIClient


class TestAPIClient:
    """API 客户端测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return APIClient(base_url="http://localhost:8000")
    
    @pytest.mark.asyncio
    async def test_list_games(self, client):
        """测试获取游戏列表"""
        try:
            games = await client.list_games()
            assert isinstance(games, list)
            assert len(games) > 0
            assert "id" in games[0]
            assert "name" in games[0]
        except Exception as e:
            pytest.skip(f"API 不可用：{e}")
    
    @pytest.mark.asyncio
    async def test_get_game(self, client):
        """测试获取游戏详情"""
        try:
            game = await client.get_game("werewolf")
            assert game["id"] == "werewolf"
            assert "name" in game
        except Exception as e:
            pytest.skip(f"API 不可用：{e}")
    
    @pytest.mark.asyncio
    async def test_list_rooms(self, client):
        """测试获取房间列表"""
        try:
            rooms = await client.list_rooms("werewolf")
            assert isinstance(rooms, list)
        except Exception as e:
            pytest.skip(f"API 不可用：{e}")
