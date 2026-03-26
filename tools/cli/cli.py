"""
ClawPlayGame CLI - 命令行游戏平台工具
"""
import typer
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import config
from .session import session
from .client import api_client

app = typer.Typer(
    name="clawplaygame",
    help="🦞 ClawPlayGame CLI - 命令行游戏平台工具",
    add_completion=False
)
console = Console()


def version_callback(value: bool):
    """显示版本"""
    if value:
        console.print("[bold blue]ClawPlayGame CLI[/bold blue] version 0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        help="显示版本"
    )
):
    """ClawPlayGame CLI 主入口"""
    pass


# ========== 认证命令 ==========

@app.group()
def auth():
    """认证相关命令"""
    pass


@auth.command()
def login(username: str, password: str):
    """登录（开发中）"""
    console.print("[yellow]⚠️  登录功能开发中...[/yellow]")
    console.print("当前仅支持游客模式")


@auth.command()
def guest():
    """以游客身份登录"""
    console.print("[green]✓ 游客登录成功[/green]")
    console.print(f"API 地址：{config.api_url}")


@auth.command()
def logout():
    """登出"""
    session.clear()
    console.print("[green]✓ 已登出[/green]")


@auth.command()
def status():
    """查看登录状态"""
    if session.is_logged_in:
        console.print(Panel(
            f"[bold]用户:[/bold] {session.user_name}\n"
            f"[bold]ID:[/bold] {session.user_id}\n"
            f"[bold]API:[/bold] {config.api_url}",
            title="👤 已登录",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[yellow]未登录[/yellow]\n"
            "使用 [bold]clawplaygame auth guest[/bold] 以游客身份登录",
            title="⚠️  未登录",
            border_style="yellow"
        ))


# ========== 游戏命令 ==========

@app.group()
def games():
    """游戏相关命令"""
    pass


@games.command("list")
def list_games():
    """列出所有游戏"""
    try:
        games_list = asyncio.run(api_client.list_games())
        
        table = Table(title="🎮 游戏列表")
        table.add_column("ID", style="cyan")
        table.add_column("名称", style="green")
        table.add_column("类型", style="yellow")
        table.add_column("人数", style="blue")
        table.add_column("状态", style="magenta")
        
        for game in games_list:
            status_style = "green" if game["status"] == "active" else "yellow"
            table.add_row(
                game["id"],
                game["name"],
                game["type"],
                f"{game['min_players']}-{game['max_players']}人",
                f"[{status_style}]{game['status']}[/{status_style}]"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ 获取游戏列表失败：{e}[/red]")


@games.command()
def select(game_id: str):
    """选择游戏"""
    try:
        game = asyncio.run(api_client.get_game(game_id))
        config.set("current_game", game)
        console.print(f"[green]✓ 已选择游戏：{game['name']}[/green]")
        
        # 显示游戏详情
        console.print(Panel(
            f"[bold]描述:[/bold] {game['description']}\n"
            f"[bold]人数:[/bold] {game['min_players']}-{game['max_players']}人\n"
            f"[bold]时长:[/bold] {game['duration_minutes']}分钟",
            title=f"🎮 {game['name']}",
            border_style="blue"
        ))
    except Exception as e:
        console.print(f"[red]✗ 选择游戏失败：{e}[/red]")


@games.command()
def rooms():
    """列出当前游戏的房间"""
    current_game = config.get("current_game")
    if not current_game:
        console.print("[yellow]⚠️  请先选择游戏：clawplaygame games select <game_id>[/yellow]")
        return
    
    try:
        rooms_list = asyncio.run(api_client.list_rooms(current_game["id"]))
        
        if not rooms_list:
            console.print("[yellow]暂无房间[/yellow]")
            return
        
        table = Table(title=f"🏠 {current_game['name']} 房间列表")
        table.add_column("ID", style="cyan")
        table.add_column("名称", style="green")
        table.add_column("房主", style="yellow")
        table.add_column("人数", style="blue")
        table.add_column("状态", style="magenta")
        
        for room in rooms_list:
            player_count = f"{len(room['players'])}/{room['max_players']}"
            status_style = "green" if room["status"] == "waiting" else "yellow"
            table.add_row(
                room["id"],
                room["room_name"],
                room["host_name"],
                player_count,
                f"[{status_style}]{room['status']}[/{status_style}]"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ 获取房间列表失败：{e}[/red]")


# ========== 房间命令 ==========

@app.group()
def rooms():
    """房间相关命令"""
    pass


@rooms.command()
def create(name: str, max_players: int = 10, public: bool = True):
    """创建房间"""
    current_game = config.get("current_game")
    if not current_game:
        console.print("[yellow]⚠️  请先选择游戏：clawplaygame games select <game_id>[/yellow]")
        return
    
    player_name = session.user_name or "游客"
    
    try:
        room = asyncio.run(api_client.create_room(
            game_id=current_game["id"],
            player_name=player_name,
            room_name=name,
            max_players=max_players,
            is_public=public,
            player_id=session.user_id
        ))
        
        session.room = room
        console.print(f"[green]✓ 房间创建成功：{name}[/green]")
        console.print(f"房间 ID: [cyan]{room['id']}[/cyan]")
    except Exception as e:
        console.print(f"[red]✗ 创建房间失败：{e}[/red]")


@rooms.command()
def join(room_id: str):
    """加入房间"""
    player_name = session.user_name or "游客"
    
    try:
        result = asyncio.run(api_client.join_room(
            room_id=room_id,
            player_name=player_name,
            player_id=session.user_id
        ))
        
        session.room = result["room"]
        console.print(f"[green]✓ 加入房间成功[/green]")
        
        # 显示房间信息
        room = result["room"]
        console.print(Panel(
            f"[bold]名称:[/bold] {room['room_name']}\n"
            f"[bold]房主:[/bold] {room['host_name']}\n"
            f"[bold]人数:[/bold] {len(room['players'])}/{room['max_players']}",
            title=f"🏠 房间 #{room_id}",
            border_style="blue"
        ))
    except Exception as e:
        console.print(f"[red]✗ 加入房间失败：{e}[/red]")


@rooms.command()
def leave():
    """离开房间"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    session.room = None
    console.print("[green]✓ 已离开房间[/green]")


@rooms.command()
def info():
    """查看房间信息"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    room = session.room
    console.print(Panel(
        f"[bold]名称:[/bold] {room['room_name']}\n"
        f"[bold]ID:[/bold] {room['id']}\n"
        f"[bold]房主:[/bold] {room['host_name']}\n"
        f"[bold]人数:[/bold] {len(room['players'])}/{room['max_players']}\n"
        f"[bold]状态:[/bold] {room['status']}\n"
        f"[bold]公开:[/bold] {'是' if room['is_public'] else '否'}",
        title=f"🏠 房间信息",
        border_style="blue"
    ))
    
    # 显示玩家列表
    if room.get("players"):
        console.print("\n[bold]玩家列表:[/bold]")
        for i, player in enumerate(room["players"], 1):
            is_host = player.get("role") == "host"
            is_ready = player.get("is_ready", 0) == 1
            status = "✓" if is_ready else " "
            host_mark = "👑" if is_host else " "
            console.print(f"  {i}. {status} {host_mark} {player['player_name']}")


# ========== 聊天命令 ==========

@app.group()
def chat():
    """聊天相关命令"""
    pass


@chat.command()
def send(message: str):
    """发送消息"""
    if not session.in_room:
        console.print("[yellow]⚠️  请先加入房间[/yellow]")
        return
    
    try:
        asyncio.run(api_client.send_message(
            room_id=session.room_id,
            player_id=session.user_id,
            content=message
        ))
        console.print(f"[green]✓ 消息已发送[/green]")
    except Exception as e:
        console.print(f"[red]✗ 发送消息失败：{e}[/red]")


@chat.command()
def history(limit: int = 20):
    """查看历史消息"""
    if not session.in_room:
        console.print("[yellow]⚠️  请先加入房间[/yellow]")
        return
    
    try:
        messages = asyncio.run(api_client.get_messages(
            room_id=session.room_id,
            limit=limit
        ))
        
        if not messages:
            console.print("[yellow]暂无消息[/yellow]")
            return
        
        console.print(f"\n[bold]最近 {len(messages)} 条消息:[/bold]\n")
        for msg in messages:
            timestamp = msg.get("timestamp", "")[:19]  # 截取日期部分
            if msg["type"] == "chat":
                console.print(f"[{timestamp}] [bold]{msg['player_name']}:[/bold] {msg['content']}")
            elif msg["type"] == "system":
                console.print(f"[{timestamp}] [red]系统:[/red] {msg['content']}")
            elif msg["type"] == "action":
                console.print(f"[{timestamp}] [blue]动作:[/blue] {msg['content']}")
    except Exception as e:
        console.print(f"[red]✗ 获取消息失败：{e}[/red]")


# ========== 玩家命令 ==========

@app.group()
def player():
    """玩家相关命令"""
    pass


@player.command()
def ready():
    """准备"""
    if not session.in_room:
        console.print("[yellow]⚠️  请先加入房间[/yellow]")
        return
    
    try:
        result = asyncio.run(api_client.toggle_ready(
            room_id=session.room_id,
            player_id=session.user_id
        ))
        
        status = "已准备" if result["is_ready"] else "已取消准备"
        console.print(f"[green]✓ {status}[/green]")
        
        # 刷新房间信息
        session.room = asyncio.run(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 操作失败：{e}[/red]")


# ========== 房主命令 ==========

@app.group()
def host():
    """房主相关命令"""
    pass


@host.command()
def kick(player_id: str):
    """踢出玩家"""
    if not session.in_room or not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.run(api_client.kick_player(
            room_id=session.room_id,
            player_id=player_id,
            host_id=session.user_id
        ))
        console.print(f"[green]✓ 玩家已踢出[/green]")
        
        # 刷新房间信息
        session.room = asyncio.run(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 踢出失败：{e}[/red]")


@host.command()
def start():
    """开始游戏"""
    if not session.in_room or not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.run(api_client.start_game(session.room_id))
        console.print("[green]✓ 游戏已开始[/green]")
        
        # 刷新房间信息
        session.room = asyncio.run(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 开始游戏失败：{e}[/red]")


@host.command()
def dismiss():
    """解散房间"""
    if not session.in_room or not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.run(api_client.delete_room(
            room_id=session.room_id,
            host_id=session.user_id
        ))
        console.print("[green]✓ 房间已解散[/green]")
        session.room = None
    except Exception as e:
        console.print(f"[red]✗ 解散失败：{e}[/red]")


if __name__ == "__main__":
    app()
