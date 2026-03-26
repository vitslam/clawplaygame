'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { useParams, useRouter } from 'next/navigation';
import { Send, Users, Shield, Sword, Eye, Volume2, MicOff, Play, LogOut, Loader2 } from 'lucide-react';
import { useUser } from '@/lib/UserContext';
import { getRoom, joinRoom, getMessages, sendMessage, createWebSocket, type Room as RoomType, type Message } from '@/lib/api';

export default function GameRoom() {
  const params = useParams();
  const router = useRouter();
  const roomId = params.roomId as string;
  const { user, setUser } = useUser();
  
  const [room, setRoom] = useState<RoomType | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [playerId, setPlayerId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [nickname, setNickname] = useState('');
  
  // 房主功能状态
  const [showHostMenu, setShowHostMenu] = useState(false); // 房主菜单
  const [selectedPlayer, setSelectedPlayer] = useState<any>(null); // 选中的玩家
  const [isEditingName, setIsEditingName] = useState(false); // 是否正在编辑房间名
  const [editingRoomName, setEditingRoomName] = useState(''); // 编辑中的房间名
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // 初始化：加载房间和 WebSocket
  useEffect(() => {
    loadRoom();
    
    try {
      const ws = createWebSocket(roomId);
      ws.onopen = () => console.log('WebSocket connected');
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
          setMessages(prev => [...prev, data.data]);
        } else if (data.type === 'player_joined' || data.type === 'player_left') {
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            type: 'system',
            content: data.type === 'player_joined' ? '玩家加入' : '玩家离开',
            timestamp: data.timestamp
          }]);
          loadRoom();
        }
      };
      ws.onclose = () => console.log('WebSocket disconnected');
      wsRef.current = ws;
    } catch (err) {
      console.error('WebSocket connection failed:', err);
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [roomId]);
  
  // 当 user 加载完成后，检查是否需要恢复 playerId
  useEffect(() => {
    if (user && room && !playerId) {
      const playerInRoom = room.players.find((p: any) => (p.id || p.player_id) === user.id);
      if (playerInRoom) {
        setPlayerId((playerInRoom as any).player_id || (playerInRoom as any).id || user.id);
      }
    }
  }, [user, room, playerId]);
  
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const loadRoom = async () => {
    try {
      const data = await getRoom(roomId);
      setRoom(data);
      const msgData = await getMessages(roomId);
      setMessages(msgData.messages);
      
      if (user) {
        // 已登录用户：检查是否已在房间
        const playerInRoom = data.players.find((p: any) => (p.id || p.player_id) === user.id);
        if (playerInRoom) {
          // 使用实际的 player_id（可能是 player_id 或 id）
          setPlayerId((playerInRoom as any).player_id || (playerInRoom as any).id || user.id);
        } else if (data.status === 'waiting') {
          // 等待中的房间，已登录用户直接加入
          await handleAutoJoin(user.nickname);
          return; // handleAutoJoin 会调用 loadRoom，所以这里直接返回
        }
        // 游戏中的房间，已登录用户可以观战（不加入）
      }
      // 未登录用户：不弹窗，只能观战（如果是游戏中）
      
      setLoading(false);
    } catch (err) {
      setError((err as Error).message);
      setLoading(false);
    }
  };

  // 自动加入（已登录用户）
  const handleAutoJoin = async (nickname: string) => {
    try {
      const { joinRoom } = await import('@/lib/api');
      const result = await joinRoom(roomId, nickname, user?.id);
      const newUser = { id: result.player.id || result.player.player_id || user?.id || '', nickname };
      setUser(newUser);
      setPlayerId(result.player.id || result.player.player_id || user?.id || '');
      setRoom(result.room);
      // 不调用 loadRoom，避免无限循环
      setLoading(false);
    } catch (err) {
      alert('加入房间失败：' + (err as Error).message);
      setLoading(false);
    }
  };

  // 手动加入（弹窗）
  const handleJoin = async () => {
    if (!nickname.trim()) {
      alert('请输入昵称');
      return;
    }
    try {
      const { joinRoom } = await import('@/lib/api');
      const result = await joinRoom(roomId, nickname);
      const newUser = { id: result.player.id || result.player.player_id || '', nickname };
      setUser(newUser);
      setPlayerId(result.player.id || result.player.player_id || '');
      setRoom(result.room);
      setShowJoinModal(false);
      loadRoom();
    } catch (err) {
      alert('加入房间失败：' + (err as Error).message);
    }
  };
  
  const handleLeaveRoom = () => {
    setPlayerId('');
    // 返回房间列表页（游戏详情页）- 从房间数据获取 game_id
    if (room?.game_id) {
      router.push(`/game/${room.game_id}`);
    } else {
      router.push('/');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !playerId) return;
    
    const now = new Date();
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    // 先添加到本地消息列表（立即显示）
    const newMessage = {
      id: Date.now().toString(),
      player_id: playerId,
      player_name: (me as any)?.player_name || user?.nickname || '我',
      type: 'chat',
      content: inputValue,
      timestamp: now.toISOString()
    };
    setMessages([...messages, newMessage]);
    setInputValue('');
    
    // 发送到服务器
    try {
      await sendMessage(roomId, playerId, inputValue);
    } catch (err) {
      alert('发送失败：' + (err as Error).message);
      // 发送失败则移除刚添加的消息
      setMessages(messages);
    }
  };

  const handleStartGame = async () => {
    if (!room) return;
    const minPlayers = room.game_id === 'avalon' ? 5 : room.game_id === 'werewolf' ? 6 : 3;
    if (room.players.length < minPlayers) {
      alert(`人数不足！需要至少 ${minPlayers} 人`);
      return;
    }
    try {
      const { startGame } = await import('@/lib/api');
      await startGame(roomId);
      loadRoom();
    } catch (err) {
      alert('开始游戏失败：' + (err as Error).message);
    }
  };

  // 房主功能：踢出玩家
  const handleKickPlayer = async (playerId: string) => {
    if (!confirm(`确定要将 ${selectedPlayer?.player_name} 移出房间吗？`)) return;
    try {
      const { kickPlayer } = await import('@/lib/api');
      await kickPlayer(roomId, playerId, selectedPlayer.player_id);
      setSelectedPlayer(null);
      setShowHostMenu(false);
      loadRoom();
    } catch (err) {
      alert('踢出玩家失败：' + (err as Error).message);
    }
  };

  // 房主功能：移交房主
  const handleTransferHost = async (newHostId: string) => {
    if (!confirm(`确定要将房主权限移交给 ${selectedPlayer?.player_name} 吗？`)) return;
    try {
      const { transferHost } = await import('@/lib/api');
      await transferHost(roomId, playerId, newHostId);
      setPlayerId(''); // 移交后自己不再是房主
      setSelectedPlayer(null);
      setShowHostMenu(false);
      loadRoom();
    } catch (err) {
      alert('移交房主失败：' + (err as Error).message);
    }
  };

  // 房主功能：解散房间
  const handleDeleteRoom = async () => {
    if (!confirm('确定要解散房间吗？此操作不可恢复！')) return;
    try {
      const { deleteRoom } = await import('@/lib/api');
      await deleteRoom(roomId, playerId);
      router.push(`/game/${room?.game_id || 'werewolf'}`);
    } catch (err) {
      alert('解散房间失败：' + (err as Error).message);
    }
  };

  // 格式化时间戳（支持多种格式：ISO、数字时间戳、SQLite 格式）
  const formatTime = (ts: string) => {
    if (!ts) return '00:00:00';
    
    let date: Date;
    
    // 数字时间戳
    if (typeof ts === 'string' && /^\d+$/.test(ts)) {
      date = new Date(parseInt(ts));
    }
    // SQLite 格式：YYYY-MM-DD HH:MM:SS
    else if (typeof ts === 'string' && /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/.test(ts)) {
      date = new Date(ts.replace(' ', 'T')); // 转为 ISO 格式
    }
    // ISO 格式或其他
    else {
      date = new Date(ts);
    }
    
    // 检查是否有效
    if (isNaN(date.getTime())) {
      console.error('Invalid timestamp:', ts);
      return '00:00:00';
    }
    
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  if (loading) {
    return (
      <div className="flex flex-col h-screen bg-[#f4f4f4]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-screen bg-[#f4f4f4]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-black text-red-600 mb-2">加载失败</h2>
            <p className="text-gray-600">{error}</p>
            <button onClick={() => router.back()} className="mt-4 px-6 py-2 bg-black text-white font-bold uppercase border-2 border-black hover:bg-white hover:text-black">
              返回
            </button>
          </div>
        </main>
      </div>
    );
  }

  const isPlayingAndPublic = room?.status === 'playing' && room?.is_public;
  const isWaiting = room?.status === 'waiting';
  const me = room?.players.find((p: any) => (p.player_id || p.id) === playerId);
  const isHost = room && playerId && room.host_id === playerId;

  if (showJoinModal) {
    // 未登录用户不能加入，直接显示观战提示
    if (!user) {
      return (
        <div className="flex flex-col h-screen bg-[#f4f4f4]">
          <Navbar />
          <main className="flex-1 flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white border-2 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] text-center">
              <h2 className="text-2xl font-black uppercase mb-4">需要登录</h2>
              <p className="text-gray-600 mb-6">登录后才能加入房间，当前只能观战。</p>
              <button onClick={() => setShowJoinModal(false)} className="bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black">
                继续观战
              </button>
            </div>
          </main>
        </div>
      );
    }
    
    // 已登录用户显示加入弹窗
    return (
      <div className="flex flex-col h-screen bg-[#f4f4f4]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white border-2 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <h2 className="text-3xl font-black uppercase mb-6 text-center">
              {room?.status === 'playing' ? '加入观战' : '加入房间'}
            </h2>
            <p className="font-mono text-sm mb-6 text-center">房间 #{roomId}</p>
            <div className="space-y-4">
              <div>
                <label className="block font-bold uppercase mb-2 text-sm">你的昵称</label>
                <input
                  type="text"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  placeholder="输入昵称"
                  className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                />
              </div>
              <div className="flex gap-3">
                <button onClick={() => setShowJoinModal(false)} className="flex-1 bg-gray-200 text-black px-6 py-3 border-2 border-black font-bold uppercase hover:bg-gray-300">
                  取消
                </button>
                <button onClick={handleJoin} className="flex-1 bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black">
                  {room?.status === 'playing' ? '开始观战' : '加入游戏'}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-[#f4f4f4] text-black">
      <Navbar />
      
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden max-w-[1600px] w-full mx-auto p-4 gap-6">
        
        {/* 左侧：游戏区域 */}
        <div className="flex-1 flex flex-col gap-6 overflow-y-auto pr-2">
          
          {/* 顶部房间信息 */}
          <div className="flex items-center justify-between border-2 border-black bg-white p-4">
            <div className="flex items-center gap-4">
              <button
                onClick={handleLeaveRoom}
                className="font-mono text-sm font-bold uppercase underline hover:bg-black hover:text-white px-2 py-1 transition-colors"
              >
                ← 离开房间
              </button>
              {isWaiting && isHost ? (
                <div className="flex items-center gap-2">
                  {isEditingName ? (
                    <input
                      type="text"
                      value={editingRoomName}
                      onChange={(e) => setEditingRoomName(e.target.value)}
                      onBlur={async () => {
                        setIsEditingName(false);
                        if (editingRoomName && editingRoomName !== room.room_name) {
                          try {
                            const { updateRoom } = await import('@/lib/api');
                            const updated = await updateRoom(roomId, playerId, editingRoomName, room.is_public);
                            setRoom(updated);
                          } catch (err) {
                            alert('修改房间名称失败');
                          }
                        }
                      }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          (e.target as HTMLInputElement).blur();
                        }
                      }}
                      autoFocus
                      className="border-2 border-black px-2 py-1 font-mono text-sm focus:outline-none"
                    />
                  ) : (
                    <h1 
                      onClick={() => { setEditingRoomName(room.room_name); setIsEditingName(true); }}
                      className="text-2xl font-black uppercase tracking-tight cursor-pointer hover:bg-black hover:text-white px-2 py-1 transition-colors"
                    >
                      {room?.room_name || `房间 #${roomId}`}
                    </h1>
                  )}
                  <button
                    onClick={async () => {
                      const newIsPublic = !room.is_public;
                      try {
                        const { updateRoom } = await import('@/lib/api');
                        const updated = await updateRoom(roomId, playerId, room.room_name, newIsPublic);
                        setRoom(updated);
                      } catch (err) {
                        alert('修改房间设置失败');
                      }
                    }}
                    className="text-xs bg-gray-100 border-2 border-black px-3 py-1 hover:bg-black hover:text-white transition-colors"
                  >
                    {room?.is_public ? '公开' : '私有'}
                  </button>
                </div>
              ) : (
                <h1 className="text-2xl font-black uppercase tracking-tight">{room?.room_name || `房间 #${roomId}`}</h1>
              )}
            </div>
            <div className="flex items-center gap-3 font-mono text-sm font-bold uppercase">
              {room?.status === 'playing' && (
                <>
                  <span className="flex items-center gap-2 text-[#dc2626]">
                    <div className="w-2 h-2 bg-[#dc2626] rounded-full animate-pulse"></div> 直播中
                  </span>
                  <span className="border-l-2 border-black pl-3">第 1 天</span>
                </>
              )}
              {room?.status === 'waiting' && (
                <span className="text-blue-600">等待中</span>
              )}
            </div>
          </div>

          {/* 玩家卡片网格 */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {room?.players.map((player: any, index) => {
              const isMe = (player.player_id || player.id) === playerId;
              const isAlive = player.status === 'alive';
              const isHost = player.role === 'host' || (room as any).host_id === player.player_id;
              
              return (
                <div 
                  key={player.player_id || player.id} 
                  onClick={() => {
                    if (isWaiting && isHost && !isMe) {
                      setSelectedPlayer(player);
                      setShowHostMenu(true);
                    }
                  }}
                  className={`relative flex flex-col items-center justify-center p-6 border-2 border-black transition-all cursor-${isWaiting && isHost && !isMe ? 'pointer' : 'default'} ${
                    isAlive ? 'bg-white hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-gray-200 opacity-60'
                  } ${isMe ? 'ring-4 ring-[#16a34a] ring-offset-2' : ''}`}
                >
                  {isMe && (
                    <div className="absolute top-2 left-2 font-mono text-[10px] font-bold uppercase bg-black text-white px-2 py-1">你</div>
                  )}
                  {isHost && (
                    <div className="absolute top-2 left-2 font-mono text-[10px] font-bold uppercase bg-orange-500 text-white px-2 py-1">房主</div>
                  )}
                  <div className="absolute top-2 right-2 font-mono text-xs font-bold uppercase">#{index + 1}</div>
                  
                  <div className={`w-16 h-16 rounded-full border-2 border-black mb-4 flex items-center justify-center ${isAlive ? 'bg-[#f4f4f4]' : 'bg-gray-400'}`}>
                    <Users className="w-8 h-8" />
                  </div>
                  
                  <h3 className="font-black uppercase tracking-tight text-lg truncate w-full text-center">{player.player_name || player.name}</h3>
                  
                  <div className="flex items-center gap-2 mt-2 font-mono text-xs font-bold uppercase">
                    {isAlive ? (
                      <span className="text-[#16a34a]">存活</span>
                    ) : (
                      <span className="text-[#dc2626]">死亡 ({player.role || '?'})</span>
                    )}
                  </div>
                </div>
              );
            })}
            
            {/* 空位 */}
            {room && Array.from({ length: room.max_players - room.players.length }).map((_, i) => (
              <div 
                key={`empty-${i}`}
                className="relative flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-400 bg-gray-100"
              >
                <div className="absolute top-2 right-2 font-mono text-xs font-bold uppercase text-gray-400">#{room.players.length + i + 1}</div>
                <div className="w-16 h-16 rounded-full border-2 border-dashed border-gray-400 mb-4 flex items-center justify-center">
                  <Users className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="font-mono text-sm font-bold uppercase text-gray-400">等待玩家</h3>
              </div>
            ))}
          </div>
          
          {/* 身份&行动区域 */}
          {me && room?.status === 'playing' && (
            <div className="mt-auto border-2 border-black bg-white p-6 flex flex-col md:flex-row gap-6 items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 border-2 border-black bg-[#2563eb] flex items-center justify-center text-white">
                  <Eye className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="font-mono text-sm font-bold uppercase text-gray-600 mb-1">你的身份</h3>
                  <div className="text-4xl font-black uppercase tracking-tight text-[#2563eb]">预言家</div>
                  <p className="font-mono text-xs font-bold uppercase mt-1">好人阵营。每晚可以查验一名玩家的身份。</p>
                </div>
              </div>
              
              <div className="flex flex-col gap-2 w-full md:w-auto">
                <button className="w-full md:w-48 border-2 border-black bg-black text-white px-4 py-3 font-bold uppercase hover:bg-white hover:text-black transition-colors flex items-center justify-center gap-2">
                  <Sword className="w-4 h-4" /> 投票放逐
                </button>
                <button className="w-full md:w-48 border-2 border-gray-300 bg-gray-50 text-gray-400 px-4 py-3 font-bold uppercase cursor-not-allowed flex items-center justify-center gap-2">
                  <Eye className="w-4 h-4" /> 查验身份
                </button>
              </div>
            </div>
          )}
          
          {/* 房主开始按钮 */}
          {isWaiting && room?.players[0]?.id === playerId && (
            <div className="mt-auto border-2 border-black bg-white p-6">
              <button
                onClick={handleStartGame}
                disabled={(room?.players.length || 0) < 3}
                className="w-full border-2 border-black bg-[#16a34a] text-white px-4 py-4 font-bold uppercase hover:bg-[#15803d] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 text-lg"
              >
                <Play className="w-6 h-6" /> 开始游戏
              </button>
              <p className="font-mono text-xs text-gray-600 text-center mt-2">
                最小人数：3 人
              </p>
            </div>
          )}
        </div>

        {/* 右侧：聊天&日志 */}
        <div className="w-full lg:w-96 border-2 border-black bg-white flex flex-col h-[500px] lg:h-auto">
          <div className="bg-[#f4f4f4] border-b-2 border-black p-4 font-black uppercase tracking-tight text-lg">
            游戏日志 & 聊天
          </div>
          
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
            {messages.map((msg) => {
              const time = formatTime(msg.timestamp);
              
              if (msg.type === 'system') {
                return (
                  <div key={msg.id} className="flex flex-col">
                    <div className="text-[10px] text-gray-500 font-bold mb-1">{time}</div>
                    <div className="font-bold text-[#dc2626] uppercase border-l-2 border-[#dc2626] pl-2">
                      系统：{msg.content}
                    </div>
                  </div>
                );
              }
              
              if (msg.content.includes('查验了') || msg.content.includes('使用')) {
                return (
                  <div key={msg.id} className="flex flex-col">
                    <div className="text-[10px] text-gray-500 font-bold mb-1">{time}</div>
                    <div className="font-bold text-[#2563eb] uppercase border-l-2 border-[#2563eb] pl-2">
                      动作：{msg.player_name} {msg.content}
                    </div>
                  </div>
                );
              }
              
              return (
                <div key={msg.id} className="flex flex-col">
                  <div className="text-[10px] text-gray-500 font-bold mb-1">{time}</div>
                  <div className="bg-[#f4f4f4] border-2 border-black p-2">
                    <span className="font-bold uppercase">{(msg as any).player_name || '玩家'}: </span>
                    <span>{msg.content}</span>
                  </div>
                </div>
              );
            })}
          </div>
          
          {playerId && (
            <div className="border-t-2 border-black p-4 bg-[#f4f4f4]">
              <form onSubmit={handleSendMessage} className="flex gap-2">
                <input 
                  type="text" 
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="输入消息..." 
                  className="flex-1 border-2 border-black bg-white px-3 py-2 outline-none font-mono text-sm placeholder:text-gray-400 focus:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-shadow"
                />
                <button 
                  type="submit"
                  disabled={!inputValue.trim()}
                  className="border-2 border-black bg-black text-white w-10 flex items-center justify-center hover:bg-white hover:text-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          )}
          {!playerId && isPlayingAndPublic && (
            <div className="border-t-2 border-black p-4 bg-gray-100 text-center text-sm font-bold text-gray-600 uppercase">
              👁️ 观战模式 - 无法发言
            </div>
          )}
        </div>

      </div>
      
      {/* 房主操作弹窗 */}
      {showHostMenu && selectedPlayer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white border-2 border-black p-6 max-w-sm w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <h3 className="text-xl font-black uppercase mb-4">玩家：{selectedPlayer.player_name}</h3>
            <div className="space-y-3">
              <button
                onClick={() => handleKickPlayer(selectedPlayer.player_id)}
                className="w-full bg-red-600 text-white py-3 border-2 border-red-700 font-bold uppercase hover:bg-red-700 transition-colors"
              >
                移出房间
              </button>
              <button
                onClick={() => handleTransferHost(selectedPlayer.player_id)}
                className="w-full bg-orange-500 text-white py-3 border-2 border-orange-600 font-bold uppercase hover:bg-orange-600 transition-colors"
              >
                移交房主
              </button>
              <button
                onClick={() => { setSelectedPlayer(null); setShowHostMenu(false); }}
                className="w-full bg-gray-200 text-black py-3 border-2 border-black font-bold uppercase hover:bg-gray-300 transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* 房主操作弹窗 */}
      {showHostMenu && selectedPlayer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white border-2 border-black p-6 max-w-sm w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <h3 className="text-xl font-black uppercase mb-4">玩家：{selectedPlayer.player_name}</h3>
            <div className="space-y-3">
              <button
                onClick={() => handleKickPlayer(selectedPlayer.player_id)}
                className="w-full bg-red-600 text-white py-3 border-2 border-red-700 font-bold uppercase hover:bg-red-700 transition-colors"
              >
                移出房间
              </button>
              <button
                onClick={() => handleTransferHost(selectedPlayer.player_id)}
                className="w-full bg-orange-500 text-white py-3 border-2 border-orange-600 font-bold uppercase hover:bg-orange-600 transition-colors"
              >
                移交房主
              </button>
              <button
                onClick={() => { setSelectedPlayer(null); setShowHostMenu(false); }}
                className="w-full bg-gray-200 text-black py-3 border-2 border-black font-bold uppercase hover:bg-gray-300 transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* 解散房间按钮（房主专用） */}
      {isWaiting && isHost && (
        <div className="fixed bottom-4 right-4">
          <button
            onClick={handleDeleteRoom}
            className="bg-red-600 text-white px-4 py-2 border-2 border-red-700 font-bold uppercase hover:bg-red-700 transition-colors shadow-lg"
          >
            解散房间
          </button>
        </div>
      )}
    </div>
  );
}
