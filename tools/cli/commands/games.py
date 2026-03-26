"""
游戏命令模块 - 游戏列表、选择、查看房间
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


@app.command("list")
def list_games():
    """列出所有游戏"""
    try:
        games_list = asyncio.get_event_loop().run_until_complete(api_client.list_games())
        
        if not games_list:
            console.print("[yellow]暂无游戏[/yellow]")
            return
        
        table = Table(title="🎮 游戏列表", show_lines=True)
        table.add_column("ID", style="cyan", width=15)
        table.add_column("名称", style="green", width=20)
        table.add_column("类型", style="yellow", width=15)
        table.add_column("人数", style="blue", width=12)
        table.add_column("时长", style="magenta", width=12)
        table.add_column("状态", width=15)
        table.add_column("活跃玩家", style="red", width=15)
        
        for game in games_list:
            status_style = "green" if game["status"] == "active" else "yellow"
            status_text = "✓ 可用" if game["status"] == "active" else "🚧 开发中"
            
            active_players = f"{game.get('active_players', 0):,}"
            
            table.add_row(
                game["id"],
                game["name"],
                game["type"],
                f"{game['min_players']}-{game['max_players']}人",
                game['duration_minutes'],
                f"[{status_style}]{status_text}[/{status_style}]",
                active_players
            )
        
        console.print(table)
        console.print("\n💡 提示：使用 [bold]clawplaygame games select <game_id>[/bold] 选择游戏")
    except Exception as e:
        console.print(f"[red]✗ 获取游戏列表失败：{e}[/red]")


@app.command()
def select(game_id: str):
    """选择游戏"""
    try:
        game = asyncio.get_event_loop().run_until_complete(api_client.get_game(game_id))
        
        # 保存当前游戏
        config.set("current_game", game)
        
        console.print(f"[green]✓ 已选择游戏：{game['name']}[/green]\n")
        
        # 显示游戏详情
        status_style = "green" if game["status"] == "active" else "yellow"
        status_text = "✓ 可用" if game["status"] == "active" else "🚧 开发中"
        
        console.print(Panel(
            f"[bold]描述:[/bold] {game['description']}\n\n"
            f"[bold]最少人数:[/bold] {game['min_players']}人\n"
            f"[bold]最多人数:[/bold] {game['max_players']}人\n"
            f"[bold]游戏时长:[/bold] {game['duration_minutes']}分钟\n"
            f"[bold]类型:[/bold] {game['type']}\n"
            f"[bold]状态:[/bold] [{status_style}]{status_text}[/{status_style}]\n\n"
            f"[dim]💡 使用 clawplaygame games rooms 查看房间[/dim]",
            title=f"🎮 {game['name']}",
            border_style="blue"
        ))
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            console.print(f"[red]✗ 游戏不存在：{game_id}[/red]")
        else:
            console.print(f"[red]✗ 选择游戏失败：{error_msg}[/red]")


@app.command("rooms")
def list_rooms(game_id: str = typer.Argument(None, help="游戏 ID，不传则使用当前选择的游戏")):
    """列出游戏房间"""
    # 确定游戏 ID
    if not game_id:
        current_game = config.get("current_game")
        if not current_game:
            console.print("[yellow]⚠️  请先选择游戏：clawplaygame games select <game_id>[/yellow]")
            console.print("或者指定游戏 ID: clawplaygame games rooms <game_id>")
            return
        game_id = current_game["id"]
        game_name = current_game["name"]
    else:
        game_name = game_id
    
    try:
        rooms_list = asyncio.get_event_loop().run_until_complete(api_client.list_rooms(game_id))
        
        if not rooms_list:
            console.print(f"[yellow]🎮 {game_name} 暂无房间[/yellow]")
            console.print("\n💡 提示：使用 [bold]clawplaygame rooms create[/bold] 创建房间")
            return
        
        table = Table(title=f"🏠 {game_name} 房间列表", show_lines=True)
        table.add_column("ID", style="cyan", width=12)
        table.add_column("名称", style="green", width=25)
        table.add_column("房主", style="yellow", width=15)
        table.add_column("人数", style="blue", width=10)
        table.add_column("状态", width=12)
        table.add_column("公开", width=8)
        
        for room in rooms_list:
            player_count = f"{len(room['players'])}/{room['max_players']}"
            
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
            
            # 公开样式
            public_text = "✓" if room.get("is_public", True) else "✗"
            public_style = "green" if room.get("is_public", True) else "yellow"
            
            # 人数样式（满员红色）
            if len(room['players']) >= room['max_players']:
                player_style = "red"
            else:
                player_style = "blue"
            
            table.add_row(
                room["id"],
                room["room_name"],
                room["host_name"],
                f"[{player_style}]{player_count}[/{player_style}]",
                f"[{status_style}]{status_text}[/{status_style}]",
                f"[{public_style}]{public_text}[/{public_style}]"
            )
        
        console.print(table)
        console.print(f"\n💡 提示：使用 [bold]clawplaygame rooms join <room_id>[/bold] 加入房间")
    except Exception as e:
        console.print(f"[red]✗ 获取房间列表失败：{e}[/red]")


@app.command("info")
def game_info(game_id: str = typer.Argument(None, help="游戏 ID，不传则使用当前选择的游戏")):
    """查看游戏详情"""
    if not game_id:
        current_game = config.get("current_game")
        if not current_game:
            console.print("[yellow]⚠️  请先选择游戏：clawplaygame games select <game_id>[/yellow]")
            return
        game_id = current_game["id"]
    
    try:
        game = asyncio.get_event_loop().run_until_complete(api_client.get_game(game_id))
        
        status_style = "green" if game["status"] == "active" else "yellow"
        
        console.print(Panel(
            f"[bold]描述:[/bold] {game['description']}\n\n"
            f"[bold]ID:[/bold] {game['id']}\n"
            f"[bold]名称:[/bold] {game['name']}\n"
            f"[bold]类型:[/bold] {game['type']}\n"
            f"[bold]人数:[/bold] {game['min_players']}-{game['max_players']}人\n"
            f"[bold]时长:[/bold] {game['duration_minutes']}分钟\n"
            f"[bold]状态:[/bold] [{status_style}]{game['status']}[/{status_style}]\n"
            f"[bold]活跃房间:[/bold] {game.get('active_rooms', 0)}\n"
            f"[bold]活跃玩家:[/bold] {game.get('active_players', 0):,}",
            title=f"🎮 {game['name']} - 游戏详情",
            border_style="blue"
        ))
    except Exception as e:
        console.print(f"[red]✗ 获取游戏信息失败：{e}[/red]")
