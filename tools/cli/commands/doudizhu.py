"""
斗地主命令模块 - 支持 WebSocket 实时监听
"""
import typer
import asyncio
import websockets
import json
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from config import config
from session import session
from client import api_client

app = typer.Typer()
console = Console()


@app.command("state")
def game_state():
    """查看游戏状态和手牌"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    try:
        player_id = session.user_id
        room_id = session.room_id
        
        state = asyncio.get_event_loop().run_until_complete(
            api_client.doudizhu_get_state(room_id, player_id)
        )
        
        display_game_state(state, player_id)
        
    except Exception as e:
        console.print(f"[red]✗ 获取游戏状态失败：{e}[/red]")


def display_game_state(state: dict, player_id: str):
    """显示游戏状态"""
    phase_names = {
        "landlord_election": "🎲 叫地主阶段",
        "landlord_reveal": "🃏 展示地主",
        "playing": "🎴 出牌阶段",
        "game_over": "🏁 游戏结束"
    }
    
    phase = state.get("phase", "unknown")
    phase_name = phase_names.get(phase, phase)
    
    console.print(Panel(
        f"[bold]游戏阶段:[/bold] {phase_name}\n"
        f"[bold]癞子牌:[/bold] {state.get('laizi_rank', 'N/A')}",
        title="🎮 游戏状态",
        border_style="blue"
    ))
    
    # 显示当前玩家手牌
    for player in state.get("players", []):
        if player["id"] == player_id:
            hand = player.get("hand", [])
            hand_str = " ".join(hand) if hand else "未发牌"
            
            landlord_mark = " 👑地主" if player.get("is_landlord") else ""
            
            console.print(Panel(
                f"[bold]手牌:[/bold] {hand_str}\n"
                f"[bold]牌数:[/bold] {player.get('card_count', 0)}张{landlord_mark}",
                title=f"🃏 {player.get('name', '你')}的手牌",
                border_style="green" if player.get("is_landlord") else "yellow"
            ))


@app.command("listen")
def listen_game():
    """监听游戏事件（WebSocket 长连接）"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    try:
        player_id = session.user_id
        room_id = session.room_id
        player_name = session.user_name
        
        console.print(f"[green]✓ 连接到房间 {room_id}[/green]")
        console.print("[dim]按 Ctrl+C 退出监听[/dim]\n")
        
        # 构建 WebSocket URL
        ws_url = config.api_url.replace("http://", "ws://")
        ws_url = f"{ws_url}/ws/rooms/{room_id}"
        
        async def listen():
            async with websockets.connect(ws_url) as websocket:
                # 发送认证
                auth_msg = {
                    "type": "auth",
                    "player_id": player_id,
                    "player_name": player_name
                }
                await websocket.send(json.dumps(auth_msg))
                
                # 等待认证响应
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "connected":
                    console.print("[green]✓ WebSocket 连接成功[/green]\n")
                else:
                    console.print(f"[red]✗ 认证失败：{data}[/red]")
                    return
                
                # 监听消息
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        msg_type = data.get("type", "unknown")
                        
                        if msg_type == "game_state":
                            # 游戏状态更新
                            event_data = data.get("data", {})
                            event_type = event_data.get("event_type", "")
                            
                            if event_type == "game_start":
                                console.print(Panel(
                                    f"[bold]游戏开始！[/bold]\n"
                                    f"癞子牌：{event_data.get('data', {}).get('laizi_rank', 'N/A')}",
                                    title="🎮 游戏开始",
                                    border_style="green"
                                ))
                                
                                # 自动显示手牌
                                state = await api_client.doudizhu_get_state(room_id, player_id)
                                display_game_state(state, player_id)
                            
                            elif event_type == "landlord_called":
                                player_name = event_data.get("player_name", "未知")
                                score = event_data.get("score", 0)
                                console.print(f"[yellow]📢 {player_name} 叫了 {score} 分[/yellow]")
                            
                            elif event_type == "landlord_revealed":
                                landlord = event_data.get("landlord", {})
                                bottom = event_data.get("bottom_cards", [])
                                console.print(Panel(
                                    f"[bold]地主:[/bold] {landlord.get('player_name', '未知')}\n"
                                    f"[bold]底牌:[/bold] {' '.join(bottom)}",
                                    title="🎉 地主揭晓",
                                    border_style="gold"
                                ))
                            
                            elif event_type == "cards_played":
                                player_name = event_data.get("player_name", "未知")
                                cards = event_data.get("cards", [])
                                console.print(f"[cyan]🎴 {player_name} 出了：{' '.join(cards)}[/cyan]")
                            
                            elif event_type == "turn":
                                current_player = event_data.get("current_player", "")
                                if current_player == player_id:
                                    console.print("\n[bold green]▶ 轮到你出牌了！[/bold green]")
                                    console.print("[dim]使用 clawplaygame doudizhu play <牌面> 出牌[/dim]")
                                else:
                                    console.print(f"[dim]等待 {current_player} 出牌...[/dim]")
                        
                        elif msg_type == "chat":
                            player_name = data.get("player_name", "未知")
                            content = data.get("content", "")
                            console.print(f"[dim]💬 {player_name}: {content}[/dim]")
                        
                        elif msg_type == "system":
                            content = data.get("content", "")
                            console.print(f"[bold yellow]⚙️ 系统：{content}[/bold yellow]")
                        
                    except websockets.exceptions.ConnectionClosed:
                        console.print("\n[yellow]⚠️  连接已断开[/yellow]")
                        break
        
        asyncio.run(listen())
        
    except Exception as e:
        console.print(f"[red]✗ 监听失败：{e}[/red]")


@app.command("call")
def call_landlord(score: int = typer.Argument(..., help="叫分：0=不叫，1=1 分，2=2 分，3=3 分")):
    """叫地主"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    if score not in [0, 1, 2, 3]:
        console.print("[red]✗ 叫分必须是 0、1、2 或 3[/red]")
        return
    
    try:
        player_id = session.user_id
        room_id = session.room_id
        
        result = asyncio.get_event_loop().run_until_complete(
            api_client.doudizhu_call_landlord(room_id, player_id, score)
        )
        
        if score == 0:
            console.print(f"[yellow]✓ 你选择不叫[/yellow]")
        else:
            console.print(f"[green]✓ 你叫了 {score} 分[/green]")
        
        # 显示结果
        game_state_data = result.get("game_state", {})
        if game_state_data.get("landlord"):
            landlord = game_state_data["landlord"]
            console.print(Panel(
                f"[bold]地主:[/bold] {landlord['player_name']}\n"
                f"[bold]底牌:[/bold] {' '.join(game_state_data.get('bottom_cards', []))}",
                title="🎉 地主已确定",
                border_style="green"
            ))
        
    except Exception as e:
        console.print(f"[red]✗ 叫地主失败：{e}[/red]")


@app.command("play")
def play_cards(cards: str = typer.Argument(..., help="牌面，如：'3 4 5' 或 'A A A'")):
    """出牌"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    try:
        player_id = session.user_id
        room_id = session.room_id
        
        # 解析牌面
        card_list = cards.split()
        
        result = asyncio.get_event_loop().run_until_complete(
            api_client.doudizhu_play_cards(room_id, player_id, card_list)
        )
        
        console.print(f"[green]✓ 出牌成功：{cards}[/green]")
        
        # 显示新状态
        state = asyncio.get_event_loop().run_until_complete(
            api_client.doudizhu_get_state(room_id, player_id)
        )
        display_game_state(state, player_id)
        
    except Exception as e:
        console.print(f"[red]✗ 出牌失败：{e}[/red]")


@app.command("pass")
def pass_turn():
    """过牌"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    try:
        player_id = session.user_id
        room_id = session.room_id
        
        result = asyncio.get_event_loop().run_until_complete(
            api_client.doudizhu_pass_turn(room_id, player_id)
        )
        
        console.print(f"[yellow]✓ 过牌[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ 过牌失败：{e}[/red]")
