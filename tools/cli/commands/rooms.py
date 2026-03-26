"""
房间命令模块 - 创建、加入、离开、查看房间
"""
import typer
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import config
from session import session
from client import api_client

app = typer.Typer()
console = Console()


@app.command()
def create(
    name: str = typer.Argument(..., help="房间名称"),
    max_players: int = typer.Option(10, "--max", "-m", help="最大人数"),
    public: bool = typer.Option(True, "--public/--private", help="是否公开")
):
    """创建房间"""
    # 检查是否已选择游戏
    current_game = config.get("current_game")
    if not current_game:
        console.print("[yellow]⚠️  请先选择游戏：clawplaygame games select <game_id>[/yellow]")
        return
    
    # 检查是否已登录
    if not session.is_logged_in:
        console.print("[yellow]⚠️  请先登录：clawplaygame auth guest[/yellow]")
        return
    
    player_name = session.user_name
    
    try:
        console.print(f"[bold]正在创建房间...[/bold]\n")
        console.print(f"游戏：{current_game['name']}")
        console.print(f"名称：{name}")
        console.print(f"人数：{max_players}人")
        console.print(f"公开：{'是' if public else '否'}\n")
        
        room = asyncio.get_event_loop().run_until_complete(api_client.create_room(
            game_id=current_game["id"],
            player_name=player_name,
            room_name=name,
            max_players=max_players,
            is_public=public,
            player_id=session.user_id
        ))
        
        # 保存房间信息
        session.room = room
        
        # 显示成功消息
        console.print(Panel(
            f"[bold]房间名称:[/bold] {room['room_name']}\n"
            f"[bold]房间 ID:[/bold] {room['id']}\n"
            f"[bold]游戏:[/bold] {current_game['name']}\n"
            f"[bold]人数:[/bold] 1/{room['max_players']}\n"
            f"[bold]状态:[/bold] 等待中\n\n"
            f"[dim]💡 使用 clawplaygame rooms info 查看房间详情[/dim]",
            title="✅ 房间创建成功",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[red]✗ 创建房间失败：{e}[/red]")


@app.command()
def join(room_id: str):
    """加入房间"""
    if not session.is_logged_in:
        console.print("[yellow]⚠️  请先登录：clawplaygame auth guest[/yellow]")
        return
    
    player_name = session.user_name
    
    try:
        console.print(f"[bold]正在加入房间 {room_id}...[/bold]\n")
        
        result = asyncio.get_event_loop().run_until_complete(api_client.join_room(
            room_id=room_id,
            player_name=player_name,
            player_id=session.user_id
        ))
        
        # 保存房间信息
        session.room = result["room"]
        
        # 显示房间信息
        room = result["room"]
        
        # 玩家列表
        players_text = ""
        for i, player in enumerate(room.get("players", []), 1):
            is_host = player.get("role") == "host"
            is_me = player.get("player_id") == session.user_id
            host_mark = "👑 " if is_host else ""
            me_mark = " (我)" if is_me else ""
            players_text += f"  {i}. {host_mark}{player['player_name']}{me_mark}\n"
        
        console.print(Panel(
            f"[bold]房间名称:[/bold] {room['room_name']}\n"
            f"[bold]房主:[/bold] {room['host_name']}\n"
            f"[bold]人数:[/bold] {len(room['players'])}/{room['max_players']}\n"
            f"[bold]状态:[/bold] {room['status']}\n\n"
            f"[bold]玩家列表:[/bold]\n{players_text}" if players_text else "",
            title=f"✅ 加入房间成功 #{room_id}",
            border_style="green"
        ))
    except Exception as e:
        error_msg = str(e)
        if "房间已满" in error_msg:
            console.print("[red]✗ 房间已满[/red]")
        elif "游戏已开始" in error_msg:
            console.print("[red]✗ 游戏已开始，无法加入[/red]")
        else:
            console.print(f"[red]✗ 加入房间失败：{error_msg}[/red]")


@app.command()
def leave():
    """离开房间"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    room_name = session.room.get("room_name", "房间")
    room_id = session.room_id
    
    try:
        # 调用 API 离开房间
        import httpx
        api_url = config.api_url
        response = httpx.post(f"{api_url}/api/rooms/{room_id}/leave", params={"player_id": session.user_id})
        response.raise_for_status()
        
        session.room = None
        
        console.print(Panel(
            f"你已离开 [bold]{room_name}[/bold]\n\n"
            f"[dim]💡 使用 clawplaygame games rooms 查看其他房间[/dim]",
            title="✅ 已离开房间",
            border_style="blue"
        ))
    except Exception as e:
        console.print(f"[red]✗ 离开房间失败：{e}[/red]")


@app.command()
def info():
    """查看房间信息"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        console.print("\n💡 提示：使用 [bold]clawplaygame rooms join <room_id>[/bold] 加入房间")
        return
    
    room = session.room
    
    # 是否是房主
    is_host = session.is_host()
    host_text = "👑 你是房主" if is_host else ""
    
    # 玩家列表
    players_text = ""
    for i, player in enumerate(room.get("players", []), 1):
        is_host_player = player.get("role") == "host"
        is_me = player.get("player_id") == session.user_id
        is_ready = player.get("is_ready", 0) == 1
        
        host_mark = "👑 " if is_host_player else ""
        me_mark = " (我)" if is_me else ""
        ready_mark = "✓ " if is_ready else "  "
        
        players_text += f"  {i}. {ready_mark}{host_mark}{player['player_name']}{me_mark}\n"
    
    # 状态样式
    if room["status"] == "waiting":
        status_style = "green"
        status_text = "⏳ 等待中"
    elif room["status"] == "playing":
        status_style = "red"
        status_text = "🎮 游戏中"
    else:
        status_style = "gray"
        status_text = "已结束"
    
    console.print(Panel(
        f"[bold]房间 ID:[/bold] {room['id']}\n"
        f"[bold]房间名称:[/bold] {room['room_name']}\n"
        f"[bold]游戏:[/bold] {room['game_id']}\n"
        f"[bold]房主:[/bold] {room['host_name']}\n"
        f"[bold]人数:[/bold] {len(room['players'])}/{room['max_players']}\n"
        f"[bold]状态:[/bold] [{status_style}]{status_text}[/{status_style}]\n"
        f"[bold]公开:[/bold] {'✓ 是' if room.get('is_public', True) else '✗ 否'}\n"
        f"{host_text}\n\n"
        f"[bold]玩家列表:[/bold]\n{players_text}" if players_text else "",
        title=f"🏠 房间信息 #{room['id']}",
        border_style="blue"
    ))
    
    # 房主提示
    if is_host and room["status"] == "waiting":
        console.print("\n[yellow]💡 房主可用命令:[/yellow]")
        console.print("  [bold]clawplaygame host start[/bold] - 开始游戏")
        console.print("  [bold]clawplaygame host kick <player_id>[/bold] - 踢出玩家")
        console.print("  [bold]clawplaygame host dismiss[/bold] - 解散房间")


@app.command("list")
def list_all():
    """列出所有房间（所有游戏）"""
    try:
        games_list = asyncio.get_event_loop().run_until_complete(api_client.list_games())
        
        if not games_list:
            console.print("[yellow]暂无游戏[/yellow]")
            return
        
        total_rooms = 0
        total_players = 0
        
        for game in games_list:
            if game["status"] != "active":
                continue
            
            rooms = asyncio.get_event_loop().run_until_complete(api_client.list_rooms(game["id"]))
            if rooms:
                total_rooms += len(rooms)
                for room in rooms:
                    total_players += len(room.get("players", []))
        
        console.print(Panel(
            f"[bold]总房间数:[/bold] {total_rooms}\n"
            f"[bold]总玩家数:[/bold] {total_players:,}\n\n"
            f"[dim]💡 使用 clawplaygame games rooms <game_id> 查看具体游戏的房间[/dim]",
            title="🏠 所有房间统计",
            border_style="blue"
        ))
    except Exception as e:
        console.print(f"[red]✗ 获取房间列表失败：{e}[/red]")
