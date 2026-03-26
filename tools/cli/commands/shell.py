"""
交互式 Shell 模块 - REPL 模式
"""
import typer
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from config import config
from session import session
from client import api_client

app = typer.Typer()
console = Console()


# 可用命令列表
COMMANDS = {
    "help": "显示帮助",
    "status": "查看状态",
    "games": "游戏列表",
    "select <id>": "选择游戏",
    "rooms": "房间列表",
    "create <name>": "创建房间",
    "join <id>": "加入房间",
    "info": "房间信息",
    "leave": "离开房间",
    "ready": "准备/取消准备",
    "send <msg>": "发送消息",
    "history": "历史消息",
    "host start": "开始游戏（房主）",
    "host kick <id>": "踢出玩家（房主）",
    "host dismiss": "解散房间（房主）",
    "quit": "退出",
    "exit": "退出",
}


def show_help():
    """显示帮助"""
    table = Table(title="📖 可用命令", show_lines=True)
    table.add_column("命令", style="cyan", width=20)
    table.add_column("说明", style="green")
    
    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)
    
    console.print(table)


def execute_command(cmd_line: str) -> bool:
    """执行命令，返回是否继续"""
    parts = cmd_line.strip().split()
    if not parts:
        return True
    
    cmd = parts[0].lower()
    args = parts[1:]
    
    try:
        if cmd in ["quit", "exit", "q"]:
            console.print("[yellow]再见！[/yellow]")
            return False
        
        elif cmd == "help":
            show_help()
        
        elif cmd == "status":
            if session.is_logged_in:
                console.print(f"[green]✓ 已登录：{session.user_name}[/green]")
                if session.in_room:
                    console.print(f"[green]✓ 在房间中：{session.room.get('room_name')}[/green]")
            else:
                console.print("[yellow]⚠️  未登录[/yellow]")
        
        elif cmd == "games":
            games_list = asyncio.get_event_loop().run_until_complete(api_client.list_games())
            table = Table(title="🎮 游戏列表")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("状态", style="yellow")
            for game in games_list:
                status = "✓" if game["status"] == "active" else "🚧"
                table.add_row(game["id"], game["name"], status)
            console.print(table)
        
        elif cmd == "select" and args:
            game_id = args[0]
            game = asyncio.get_event_loop().run_until_complete(api_client.get_game(game_id))
            config.set("current_game", game)
            console.print(f"[green]✓ 已选择：{game['name']}[/green]")
        
        elif cmd == "rooms":
            current_game = config.get("current_game")
            if not current_game:
                console.print("[yellow]⚠️  请先选择游戏：select <game_id>[/yellow]")
                return True
            rooms = asyncio.get_event_loop().run_until_complete(api_client.list_rooms(current_game["id"]))
            table = Table(title=f"🏠 {current_game['name']} 房间")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("人数", style="blue")
            table.add_column("状态", style="yellow")
            for room in rooms:
                status = "⏳" if room["status"] == "waiting" else "🎮"
                table.add_row(
                    room["id"],
                    room["room_name"],
                    f"{len(room['players'])}/{room['max_players']}",
                    status
                )
            console.print(table)
        
        elif cmd == "create" and args:
            if not session.is_logged_in:
                console.print("[yellow]⚠️  请先登录[/yellow]")
                return True
            current_game = config.get("current_game")
            if not current_game:
                console.print("[yellow]⚠️  请先选择游戏[/yellow]")
                return True
            name = " ".join(args)
            room = api_client.create_room(
                game_id=current_game["id"],
                player_name=session.user_name,
                room_name=name,
                player_id=session.user_id
            )
            session.room = room
            console.print(f"[green]✓ 房间创建成功：{name}[/green]")
        
        elif cmd == "join" and args:
            if not session.is_logged_in:
                console.print("[yellow]⚠️  请先登录[/yellow]")
                return True
            room_id = args[0]
            result = api_client.join_room(
                room_id=room_id,
                player_name=session.user_name,
                player_id=session.user_id
            )
            session.room = result["room"]
            console.print(f"[green]✓ 已加入房间[/green]")
        
        elif cmd == "info":
            if not session.in_room:
                console.print("[yellow]⚠️  不在房间中[/yellow]")
                return True
            room = session.room
            console.print(f"[bold]房间:[/bold] {room['room_name']}")
            console.print(f"[bold]人数:[/bold] {len(room['players'])}/{room['max_players']}")
            for i, p in enumerate(room.get("players", []), 1):
                ready = "✓" if p.get("is_ready", 0) == 1 else " "
                host = "👑" if p.get("role") == "host" else " "
                me = " (我)" if p.get("player_id") == session.user_id else ""
                console.print(f"  {i}. {ready} {host} {p['player_name']}{me}")
        
        elif cmd == "leave":
            session.room = None
            console.print("[green]✓ 已离开房间[/green]")
        
        elif cmd == "ready":
            if not session.in_room:
                console.print("[yellow]⚠️  不在房间中[/yellow]")
                return True
            result = api_client.toggle_ready(
                room_id=session.room_id,
                player_id=session.user_id
            )
            status = "已准备" if result["is_ready"] else "已取消准备"
            console.print(f"[green]✓ {status}[/green]")
            session.room = asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id))
        
        elif cmd == "send" and args:
            if not session.in_room:
                console.print("[yellow]⚠️  不在房间中[/yellow]")
                return True
            message = " ".join(args)
            api_client.send_message(
                room_id=session.room_id,
                player_id=session.user_id,
                content=message
            )
            console.print(f"[green]✓ 已发送[/green]")
        
        elif cmd == "history":
            if not session.in_room:
                console.print("[yellow]⚠️  不在房间中[/yellow]")
                return True
            messages = asyncio.get_event_loop().run_until_complete(api_client.get_messages(room_id=session.room_id, limit=20))
            for msg in messages:
                ts = msg.get("timestamp", "")[:19]
                if msg["type"] == "chat":
                    console.print(f"[{ts}] [bold]{msg['player_name']}:[/bold] {msg['content']}")
                elif msg["type"] == "system":
                    console.print(f"[{ts}] [red]系统:[/red] {msg['content']}")
                elif msg["type"] == "action":
                    console.print(f"[{ts}] [blue]动作:[/blue] {msg['content']}")
        
        elif cmd == "host" and args:
            if not session.is_host():
                console.print("[red]✗ 只有房主有此权限[/red]")
                return True
            
            subcmd = args[0]
            if subcmd == "start":
                asyncio.get_event_loop().run_until_complete(api_client.start_game(session.room_id))
                console.print("[green]✓ 游戏已开始[/green]")
            elif subcmd == "kick" and len(args) > 1:
                player_id = args[1]
                api_client.kick_player(
                    room_id=session.room_id,
                    player_id=player_id,
                    host_id=session.user_id
                )
                console.print("[green]✓ 玩家已踢出[/green]")
            elif subcmd == "dismiss":
                api_client.delete_room(
                    room_id=session.room_id,
                    host_id=session.user_id
                )
                console.print("[green]✓ 房间已解散[/green]")
                session.room = None
            else:
                console.print("[yellow]用法：host start | kick <id> | dismiss[/yellow]")
        
        else:
            console.print(f"[yellow]⚠️  未知命令：{cmd}[/yellow]")
            console.print("输入 [bold]help[/bold] 查看可用命令")
    
    except Exception as e:
        console.print(f"[red]✗ 错误：{e}[/red]")
    
    return True


@app.command()
def start():
    """启动交互式 Shell"""
    console.print(Panel(
        "[bold]🦞 ClawPlayGame Shell[/bold]\n"
        "输入 [bold]help[/bold] 查看可用命令\n"
        "输入 [bold]quit[/bold] 或 [bold]exit[/bold] 退出\n"
        "\n[dim]💡 提示：先使用 auth guest 或 auth login 登录[/dim]",
        title="欢迎",
        border_style="blue"
    ))
    
    # 检查登录状态
    if not session.is_logged_in:
        console.print("\n[yellow]⚠️  未登录，建议先登录：[/yellow]")
        console.print("  [bold]auth guest[/bold] - 游客登录")
        console.print("  [bold]auth login <用户名>[/bold] - 用户登录")
    
    # 主循环
    while True:
        try:
            # 显示提示符
            if session.in_room:
                prompt = f"[green]🏠 {session.room.get('room_name', 'room')}[/green] > "
            elif session.is_logged_in:
                prompt = f"[blue]👤 {session.user_name}[/blue] > "
            else:
                prompt = "[yellow]🦞 clawplaygame[/yellow] > "
            
            cmd_line = Prompt.ask(prompt.rstrip(" > "), default="")
            
            if not cmd_line:
                continue
            
            # 执行命令
            if not execute_command(cmd_line):
                break
        
        except KeyboardInterrupt:
            console.print("\n[yellow]使用 quit 或 exit 退出[/yellow]")
        except EOFError:
            break
    
    console.print("[blue]再见！[/blue]")
