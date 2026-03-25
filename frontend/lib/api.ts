// API 客户端 - 调用后端 FastAPI 服务

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Game {
  id: string;
  name: string;
  description: string;
  min_players: number;
  max_players: number;
  duration_minutes: string;
  type: string;
  status: string;
  active_rooms: number;
  active_players: number;
}

export interface Player {
  id: string;
  name: string;
  role: string;
  status: string;
  joined_at: string;
}

export interface Room {
  id: string;
  game_id: string;
  room_name: string;
  host_name: string;
  players: Player[];
  status: string;
  created_at: string;
  max_players: number;
  is_public: boolean;
  current_session_id?: string;  // 当前对局 ID
}

export interface Message {
  id: string;
  player_id?: string;
  player_name?: string;
  type: string;
  content: string;
  timestamp: string;
}

// 游戏 API
export async function listGames(): Promise<Game[]> {
  const res = await fetch(`${API_BASE_URL}/api/games`);
  if (!res.ok) throw new Error('获取游戏列表失败');
  return res.json();
}

export async function getGame(gameId: string): Promise<Game> {
  const res = await fetch(`${API_BASE_URL}/api/games/${gameId}`);
  if (!res.ok) throw new Error('获取游戏详情失败');
  return res.json();
}

export async function listRooms(gameId: string): Promise<Room[]> {
  const res = await fetch(`${API_BASE_URL}/api/games/${gameId}/rooms`);
  if (!res.ok) throw new Error('获取房间列表失败');
  return res.json();
}

// 房间 API
export async function createRoom(
  gameId: string,
  playerName: string,
  roomName: string,
  maxPlayers: number = 10,
  isPublic: boolean = true
): Promise<Room> {
  const res = await fetch(`${API_BASE_URL}/api/games/${gameId}/rooms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      player_name: playerName, 
      room_name: roomName,
      max_players: maxPlayers,
      is_public: isPublic 
    }),
  });
  if (!res.ok) throw new Error('创建房间失败');
  return res.json();
}

export async function getRoom(roomId: string): Promise<Room> {
  const res = await fetch(`${API_BASE_URL}/api/rooms/${roomId}`);
  if (!res.ok) throw new Error('获取房间信息失败');
  return res.json();
}

export async function joinRoom(roomId: string, playerName: string): Promise<{ success: boolean; player: Player; room: Room }> {
  const res = await fetch(`${API_BASE_URL}/api/games/${roomId}/join`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_name: playerName }),
  });
  if (!res.ok) throw new Error('加入房间失败');
  return res.json();
}

export async function sendMessage(
  roomId: string,
  playerId: string,
  content: string,
  messageType = 'chat'
): Promise<{ success: boolean; message: Message }> {
  const res = await fetch(`${API_BASE_URL}/api/games/${roomId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId, content, message_type: messageType }),
  });
  if (!res.ok) throw new Error('发送消息失败');
  return res.json();
}

export async function getMessages(roomId: string, limit = 50): Promise<{ messages: Message[] }> {
  const res = await fetch(`${API_BASE_URL}/api/games/${roomId}/messages?limit=${limit}`);
  if (!res.ok) throw new Error('获取消息失败');
  return res.json();
}

export async function startGame(roomId: string): Promise<{ success: boolean; room: Room }> {
  const res = await fetch(`${API_BASE_URL}/api/games/${roomId}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('开始游戏失败');
  return res.json();
}

export async function deleteRoom(roomId: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE_URL}/api/rooms/${roomId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('删除房间失败');
  return res.json();
}

// WebSocket 连接
export function createWebSocket(roomId: string): WebSocket {
  const wsUrl = `ws://localhost:8000/ws/rooms/${roomId}`;
  return new WebSocket(wsUrl);
}
