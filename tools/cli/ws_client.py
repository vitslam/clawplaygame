"""
WebSocket 客户端 - 实时监听房间事件
"""
import asyncio
import json
import websockets
from typing import Callable, Optional
from rich.console import Console

console = Console()


class WSClient:
    """WebSocket 客户端"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.room_id: Optional[str] = None
        self.player_id: Optional[str] = None
        self.player_name: Optional[str] = None
        self.connected = False
        self.event_handlers = {}
    
    async def connect(self, room_id: str, player_id: str, player_name: str):
        """连接到房间 WebSocket"""
        self.room_id = room_id
        self.player_id = player_id
        self.player_name = player_name
        
        uri = f"{self.base_url}/ws/rooms/{room_id}"
        console.print(f"[dim]正在连接 WebSocket: {uri}...[/dim]")
        
        try:
            self.ws = await websockets.connect(uri)
            
            # 发送认证消息
            auth_msg = {
                "type": "auth",
                "player_id": player_id,
                "player_name": player_name
            }
            await self.ws.send(json.dumps(auth_msg))
            
            # 等待连接确认
            response = await self.ws.recv()
            data = json.loads(response)
            
            if data.get("type") == "connected":
                self.connected = True
                console.print(f"[green]✓ WebSocket 已连接[/green]")
                return True
            else:
                console.print(f"[red]✗ 连接失败：{data}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]✗ 连接错误：{e}[/red]")
            return False
    
    def on_event(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        self.event_handlers[event_type] = handler
    
    async def listen(self, timeout: Optional[float] = None):
        """监听事件"""
        if not self.connected:
            console.print("[red]✗ 未连接[/red]")
            return
        
        try:
            start_time = asyncio.get_event_loop().time() if timeout else None
            
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    event_type = data.get("type", "unknown")
                    
                    # 调用事件处理器
                    if event_type in self.event_handlers:
                        await self._call_handler(event_type, data)
                    else:
                        # 默认显示
                        self._default_display(event_type, data)
                    
                    # 检查超时
                    if timeout and start_time:
                        elapsed = asyncio.get_event_loop().time() - start_time
                        if elapsed >= timeout:
                            break
                            
                except json.JSONDecodeError:
                    console.print(f"[dim]收到无效 JSON[/dim]")
                except Exception as e:
                    console.print(f"[red]事件处理错误：{e}[/red]")
                    
        except websockets.exceptions.ConnectionClosed:
            console.print("[yellow]⚠️  WebSocket 连接已关闭[/yellow]")
        except asyncio.CancelledError:
            pass
        finally:
            await self.disconnect()
    
    async def _call_handler(self, event_type: str, data: dict):
        """调用事件处理器"""
        handler = self.event_handlers.get(event_type)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                handler(data)
    
    def _default_display(self, event_type: str, data: dict):
        """默认事件显示"""
        event_data = data.get("data", {})
        timestamp = data.get("timestamp", "")[:19]
        
        if event_type == "chat":
            player_name = event_data.get("player_name", "Unknown")
            content = event_data.get("content", "")
            console.print(f"[{timestamp}] [bold green]{player_name}:[/bold green] {content}")
        
        elif event_type == "player_join":
            player_name = event_data.get("player_name", "Unknown")
            console.print(f"[{timestamp}] [bold cyan]👤 {player_name} 加入了房间[/bold cyan]")
        
        elif event_type == "player_leave":
            player_name = event_data.get("player_name", "Unknown")
            console.print(f"[{timestamp}] [bold yellow]👋 {player_name} 离开了房间[/bold yellow]")
        
        elif event_type == "player_ready":
            player_name = event_data.get("player_name", "Unknown")
            console.print(f"[{timestamp}] [bold green]✓ {player_name} 已准备[/bold green]")
        
        elif event_type == "player_not_ready":
            player_name = event_data.get("player_name", "Unknown")
            console.print(f"[{timestamp}] [bold yellow]✗ {player_name} 取消准备[/bold yellow]")
        
        elif event_type == "kicked":
            player_name = event_data.get("player_name", "Unknown")
            console.print(f"[{timestamp}] [bold red]🚫 {player_name} 被踢出房间[/bold red]")
        
        else:
            console.print(f"[{timestamp}] [dim]📡 [{event_type}] {event_data}[/dim]")
    
    async def send_message(self, content: str, message_type: str = "chat"):
        """发送消息"""
        if not self.connected:
            return
        
        msg = {
            "type": message_type,
            "data": {
                "content": content
            }
        }
        await self.ws.send(json.dumps(msg))
    
    async def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.ws:
            await self.ws.close()
            console.print("[dim]✓ WebSocket 已断开[/dim]")
