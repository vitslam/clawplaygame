"""
斗地主命令模块
"""
import typer
import asyncio
from rich.console import Console
from rich.panel import Panel

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
        
        # 显示游戏信息
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
            f"[bold]癞子牌:[/bold] {state.get('laizi_rank', 'N/A')}\n"
            f"[bold]底牌数:[/bold] {state.get('bottom_count', 3)}",
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
                
                # 如果是叫地主阶段且是当前玩家
                if phase == "landlord_election" and state.get("current_player") == player_id:
                    console.print("\n[yellow]💡 轮到你叫地主！使用 clawplaygame doudizhu call <分数>[/yellow]")
                
                # 如果是出牌阶段且是当前玩家
                elif phase == "playing" and state.get("current_player") == player_id:
                    console.print("\n[yellow]💡 轮到你出牌！使用 clawplaygame doudizhu play <牌面>[/yellow]")
                    console.print("[yellow]或者过牌：clawplaygame doudizhu pass[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ 获取游戏状态失败：{e}[/red]")


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
        
        # 简单解析牌面（后续可以改进）
        card_list = cards.split()
        
        result = asyncio.get_event_loop().run_until_complete(
            api_client.doudizhu_play_cards(room_id, player_id, card_list)
        )
        
        console.print(f"[green]✓ 出牌成功：{cards}[/green]")
        
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
