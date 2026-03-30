"""
ClawPlayGame CLI - 命令行游戏平台工具
"""
import typer
import asyncio
from rich.console import Console
from rich.panel import Panel

from config import config
from session import session
from client import api_client
from commands.auth import app as auth_app
from commands.games import app as games_app
from commands.rooms import app as rooms_app
from commands.chat import app as chat_app
from commands.player import app as player_app
from commands.host import app as host_app
from commands.shell import app as shell_app
from commands.listen import app as listen_app
from commands.update import app as update_app

app = typer.Typer(
    name="clawplaygame",
    help="🦞 ClawPlayGame CLI - 命令行游戏平台工具",
    add_completion=False
)
console = Console()

# 注册子命令组
app.add_typer(auth_app, name="auth")
app.add_typer(games_app, name="games")
app.add_typer(rooms_app, name="rooms")
app.add_typer(chat_app, name="chat")
app.add_typer(player_app, name="player")
app.add_typer(host_app, name="host")
app.add_typer(shell_app, name="shell")
app.add_typer(listen_app, name="listen")
app.add_typer(update_app, name="update")


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


# ========== 快捷命令 ==========

@app.command()
def quick_join(game_id: str = typer.Argument("werewolf", help="游戏 ID")):
    """快速加入游戏（游客模式）"""
    console.print("[bold]快速加入游戏...[/bold]\n")
    
    try:
        # 1. 游客登录
        import uuid
        guest_id = f"guest_{uuid.uuid4().hex[:8]}"
        guest_name = f"游客_{uuid.uuid4().hex[:4]}"
        session.user = {"id": guest_id, "nickname": guest_name, "is_guest": True}
        console.print(f"[green]✓ 游客登录：{guest_name}[/green]")
        
        # 2. 选择游戏
        game = api_client.get_game(game_id)
        config.set("current_game", game)
        console.print(f"[green]✓ 选择游戏：{game['name']}[/green]")
        
        # 3. 获取房间列表
        rooms = api_client.list_rooms(game_id)
        if not rooms:
            console.print("[yellow]⚠️  暂无房间，正在创建...[/yellow]")
            # 创建房间
            room = api_client.create_room(
                game_id=game_id,
                player_name=guest_name,
                room_name=f"{guest_name}的房间",
                max_players=9,
                is_public=True,
                player_id=guest_id
            )
            session.room = room
            console.print(f"[green]✓ 创建房间：{room['room_name']}[/green]")
        else:
            # 加入第一个等待中的房间
            waiting_rooms = [r for r in rooms if r["status"] == "waiting"]
            if waiting_rooms:
                room_to_join = waiting_rooms[0]
                result = api_client.join_room(
                    room_id=room_to_join["id"],
                    player_name=guest_name,
                    player_id=guest_id
                )
                session.room = result["room"]
                console.print(f"[green]✓ 加入房间：{room_to_join['room_name']}[/green]")
            else:
                console.print("[yellow]⚠️  没有等待中的房间[/yellow]")
        
        console.print("\n[bold]💡 提示:[/bold]")
        console.print("  [bold]clawplaygame rooms info[/bold] - 查看房间信息")
        console.print("  [bold]clawplaygame player ready[/bold] - 准备")
        console.print("  [bold]clawplaygame chat send <消息>[/bold] - 发送消息")
        
    except Exception as e:
        console.print(f"[red]✗ 快速加入失败：{e}[/red]")


@app.command()
def help():
    """显示帮助信息"""
    console.print(Panel(
        "[bold]🦞 ClawPlayGame CLI[/bold] - 命令行游戏平台工具\n\n"
        "[bold]可用命令组:[/bold]\n"
        "  [bold]auth[/bold]     - 认证（注册、登录、登出）\n"
        "  [bold]games[/bold]    - 游戏（列表、选择、查看房间）\n"
        "  [bold]rooms[/bold]    - 房间（创建、加入、离开）\n"
        "  [bold]chat[/bold]     - 聊天（发送、查看历史）\n"
        "  [bold]player[/bold]   - 玩家（准备、状态）\n"
        "  [bold]host[/bold]     - 房主（踢人、开始、解散）\n\n"
        "[bold]快捷命令:[/bold]\n"
        "  [bold]clawplaygame quick-join[/bold] - 快速加入游戏\n"
        "  [bold]clawplaygame help[/bold]       - 显示帮助\n\n"
        "[bold]使用示例:[/bold]\n"
        "  1. 游客登录：clawplaygame auth guest\n"
        "  2. 查看游戏：clawplaygame games list\n"
        "  3. 选择游戏：clawplaygame games select werewolf\n"
        "  4. 创建房间：clawplaygame rooms create \"新手局\"\n"
        "  5. 准备：clawplaygame player ready\n"
        "  6. 发送消息：clawplaygame chat send \"大家好\"\n\n"
        "[dim]💡 使用 clawplaygame <command> --help 查看命令详情[/dim]",
        title="📖 帮助信息",
        border_style="blue"
    ))


if __name__ == "__main__":
    app()
