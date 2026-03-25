'use client';

import { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import { Send, User as UserIcon, Skull, Volume2, MicOff, Info, Clock, Users, Loader2, Play, LogOut } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { useUser } from '@/lib/UserContext';
import { getRoom, joinRoom, getMessages, sendMessage, createWebSocket, type Room as RoomType, type Message, type Player } from '@/lib/api';

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
  
  // 弹窗状态
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [nickname, setNickname] = useState('');
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    loadRoom();
    
    // 连接 WebSocket
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
          loadRoom(); // 刷新玩家列表
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
  
  // 心跳：每 30 秒更新一次活跃时间
  useEffect(() => {
    if (!user) return;
    
    const heartbeat = async () => {
      try {
        await fetch(`/api/users/${user.id}/heartbeat`, { method: 'POST' });
      } catch (e) {
        console.error('Heartbeat failed:', e);
      }
    };
    
    const interval = setInterval(heartbeat, 30000);
    return () => clearInterval(interval);
  }, [user]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const loadRoom = async () => {
    try {
      const data = await getRoom(roomId);
      setRoom(data);
      
      // 加载消息历史
      const msgData = await getMessages(roomId);
      setMessages(msgData.messages);
      
      // 检查是否已经在房间里
      if (user) {
        const alreadyInRoom = data.players.some(p => p.id === user.id);
        if (alreadyInRoom) {
          setPlayerId(user.id);
        } else {
          // 不在房间里，显示加入弹窗
          setNickname(user.nickname);
          setShowJoinModal(true);
        }
      } else if (data.status === 'waiting') {
        // 没有用户且房间等待中，显示加入弹窗
        setNickname('玩家_' + Math.random().toString(36).slice(2, 6));
        setShowJoinModal(true);
      }
      
      setLoading(false);
    } catch (err) {
      setError((err as Error).message);
      setLoading(false);
    }
  };

  const handleJoin = async () => {
    if (!nickname.trim()) {
      alert('请输入昵称');
      return;
    }
    
    try {
      const { joinRoom } = await import('@/lib/api');
      const result = await joinRoom(roomId, nickname);
      
      // 保存用户
      const newUser = { id: result.player.id, nickname };
      setUser(newUser);
      setPlayerId(result.player.id);
      setRoom(result.room);
      setShowJoinModal(false);
      
      if (result.already_joined) {
        console.log('已经在这个房间里了');
      }
      
      loadRoom();
    } catch (err) {
      alert('加入房间失败：' + (err as Error).message);
    }
  };
  
  const handleLeaveRoom = async () => {
    // 清除本地玩家 ID，但保留用户信息
    setPlayerId('');
    router.push('/');
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !playerId) return;
    
    try {
      await sendMessage(roomId, playerId, inputValue);
      setInputValue('');
    } catch (err) {
      alert('发送失败：' + (err as Error).message);
    }
  };

  const handleStartGame = async () => {
    if (!room) return;
    
    // 检查人数
    const minPlayers = room.game_id === 'avalon' ? 5 : 
                       room.game_id === 'werewolf' ? 6 : 
                       room.game_id === 'botc' ? 5 : 3;
    
    if (room.players.length < minPlayers) {
      alert(`人数不足！${room.game_id === 'avalon' ? '阿瓦隆' : room.game_id === 'werewolf' ? '狼人杀' : '本游戏'} 需要至少 ${minPlayers} 人`);
      return;
    }
    
    try {
      const { startGame } = await import('@/lib/api');
      await startGame(roomId);
      alert('游戏已开始！');
      loadRoom();
    } catch (err) {
      alert('开始游戏失败：' + (err as Error).message);
    }
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
            <button 
              onClick={() => router.back()}
              className="mt-4 px-6 py-2 bg-blue-600 text-white font-bold rounded hover:bg-blue-700"
            >
              返回
            </button>
          </div>
        </main>
      </div>
    );
  }

  // 游戏中且公开的房间，可以直接观战（不需要加入）
  const isPlayingAndPublic = room?.status === 'playing' && room?.is_public;
  
  // 加入房间弹窗
  if (showJoinModal) {
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
                  className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowJoinModal(false)}
                  className="flex-1 bg-gray-200 text-black px-6 py-3 border-2 border-black font-bold uppercase hover:bg-gray-300 transition-all"
                >
                  取消
                </button>
                <button
                  onClick={handleJoin}
                  className="flex-1 bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black transition-all"
                >
                  {room?.status === 'playing' ? '开始观战' : '加入游戏'}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const me = room?.players.find(p => p.id === playerId);
  const isWaiting = room?.status === 'waiting';

  // 等待中界面
  if (isWaiting) {
    return (
      <div className="flex flex-col h-screen bg-[#f4f4f4]">
        <Navbar />
        
        <div className="flex-1 flex overflow-hidden max-w-[1600px] w-full mx-auto p-4 lg:p-6 gap-6">
          
          {/* Left Column: Players */}
          <div className="flex flex-col w-80 bg-white border-2 border-black rounded-xl overflow-hidden">
            <div className="p-5 border-b-2 border-black bg-gray-100">
              <h3 className="font-bold text-xl flex items-center gap-3">
                <Users className="w-6 h-6" /> 玩家列表 ({room?.players.length || 0}/{room?.max_players})
              </h3>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {room?.players.map((player, index) => (
                <div 
                  key={player.id} 
                  className={`flex items-center justify-between p-3 rounded-lg border-2 ${player.id === playerId ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${player.status === 'alive' ? 'bg-blue-600' : 'bg-gray-400'}`}>
                      {player.status === 'alive' ? <UserIcon className="w-5 h-5 text-white" /> : <Skull className="w-5 h-5 text-white" />}
                    </div>
                    <div>
                      <span className={`font-bold ${player.status === 'alive' ? 'text-gray-900' : 'text-gray-500 line-through'}`}>
                        {index + 1}. {player.name}
                      </span>
                      {player.id === playerId && <div className="text-xs text-blue-600 font-bold">YOU</div>}
                      {player.role === 'host' && <div className="text-xs text-orange-600 font-bold">房主</div>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* 控制区 */}
            <div className="p-4 border-t-2 border-black bg-gray-50 space-y-2">
              {room?.players[0]?.id === playerId && (
                <>
                  <button
                    onClick={handleStartGame}
                    disabled={(room?.players.length || 0) < (room?.game_id === 'avalon' ? 5 : room?.game_id === 'werewolf' ? 6 : 3)}
                    className="w-full bg-green-600 text-white py-3 font-bold uppercase hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                  >
                    <Play className="w-5 h-5" /> 开始游戏
                  </button>
                  <p className="text-xs text-gray-600 text-center">
                    最小人数：{room?.game_id === 'avalon' ? '5 人（阿瓦隆）' : room?.game_id === 'werewolf' ? '6 人（狼人杀）' : '3 人'}
                  </p>
                </>
              )}
              {playerId && (
                <button
                  onClick={handleLeaveRoom}
                  className="w-full bg-red-600 text-white py-3 font-bold uppercase hover:bg-red-700 transition-all flex items-center justify-center gap-2"
                >
                  <LogOut className="w-5 h-5" /> 退出房间
                </button>
              )}
            </div>
          </div>

          {/* Middle Column: Chat */}
          <div className="flex-1 flex flex-col bg-white border-2 border-black rounded-xl overflow-hidden">
            {/* Header */}
            <div className="h-16 border-b-2 border-black flex items-center justify-between px-6 bg-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                <span className="font-black text-xl">ROOM #{roomId.toUpperCase()}</span>
                <span className="text-xs font-bold px-2 py-1 rounded bg-green-100 text-green-700">等待中</span>
              </div>
              <div className="text-sm font-bold text-gray-600">
                等待玩家加入...
              </div>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.type === 'system' ? 'justify-center' : (msg.player_id === playerId ? 'justify-end' : 'justify-start')}`}>
                  {msg.type === 'system' ? (
                    <div className="bg-gray-100 border-2 border-gray-300 text-gray-700 px-4 py-2 rounded-full text-sm flex items-center gap-2">
                      <Info className="w-4 h-4" /> {msg.content}
                    </div>
                  ) : (
                    <div className={`max-w-[70%] px-4 py-3 rounded-xl border-2 ${msg.player_id === playerId ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-100 text-gray-900 border-gray-200'}`}>
                      <div className="text-xs font-bold mb-1 opacity-75">{msg.player_name || '玩家'}</div>
                      <div className="text-sm">{msg.content}</div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Input - 只有已加入的玩家可以发言 */}
            {playerId && (
              <form onSubmit={handleSendMessage} className="p-4 border-t-2 border-black bg-gray-50 flex gap-3">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="输入消息..."
                  className="flex-1 border-2 border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button 
                  type="submit"
                  disabled={!inputValue.trim()}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Send className="w-5 h-5" /> 发送
                </button>
              </form>
            )}
            {!playerId && isPlayingAndPublic && (
              <div className="p-4 border-t-2 border-black bg-gray-100 text-center text-sm font-bold text-gray-600 uppercase">
                👁️ 观战模式 - 无法发言
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 游戏中界面
  return (
    <div className="flex flex-col h-screen bg-[#f4f4f4]">
      <Navbar />
      
      <div className="flex-1 flex overflow-hidden max-w-[1600px] w-full mx-auto p-4 lg:p-6 gap-6">
        
        {/* Left Column: Players */}
        <div className="hidden lg:flex flex-col w-72 bg-white border-2 border-black rounded-xl overflow-hidden">
          <div className="p-5 border-b-2 border-black bg-gray-100">
            <h3 className="font-bold text-xl flex items-center gap-3">
              <Users className="w-6 h-6" /> 玩家列表
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {room?.players.map((player, index) => (
              <div 
                key={player.id} 
                className={`flex items-center justify-between p-3 rounded-lg border-2 ${player.id === playerId ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${player.status === 'alive' ? 'bg-blue-600' : 'bg-gray-400'}`}>
                    {player.status === 'alive' ? <UserIcon className="w-5 h-5 text-white" /> : <Skull className="w-5 h-5 text-white" />}
                  </div>
                  <div>
                    <span className={`font-bold ${player.status === 'alive' ? 'text-gray-900' : 'text-gray-500 line-through'}`}>
                      {index + 1}. {player.name}
                    </span>
                    {player.id === playerId && <div className="text-xs text-blue-600 font-bold">YOU</div>}
                  </div>
                </div>
                {player.status === 'alive' ? <Volume2 className="w-4 h-4 text-gray-400" /> : <MicOff className="w-4 h-4 text-gray-400" />}
              </div>
            ))}
          </div>
        </div>

        {/* Middle Column: Chat */}
        <div className="flex-1 flex flex-col bg-white border-2 border-black rounded-xl overflow-hidden">
          {/* Header */}
          <div className="h-16 border-b-2 border-black flex items-center justify-between px-6 bg-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
              <span className="font-black text-xl">ROOM #{roomId.toUpperCase()}</span>
              <span className="text-xs font-bold px-2 py-1 rounded bg-red-100 text-red-700">游戏中</span>
            </div>
            <div className="text-sm font-bold flex items-center gap-2 bg-blue-100 px-4 py-2 rounded-lg">
              <Clock className="w-4 h-4" /> 第 1 轮
            </div>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.type === 'system' ? 'justify-center' : (msg.player_id === playerId ? 'justify-end' : 'justify-start')}`}>
                {msg.type === 'system' ? (
                  <div className="bg-gray-100 border-2 border-gray-300 text-gray-700 px-4 py-2 rounded-full text-sm flex items-center gap-2">
                    <Info className="w-4 h-4" /> {msg.content}
                  </div>
                ) : (
                  <div className={`max-w-[70%] px-4 py-3 rounded-xl border-2 ${msg.player_id === playerId ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-100 text-gray-900 border-gray-200'}`}>
                    <div className="text-xs font-bold mb-1 opacity-75">{msg.player_name || '玩家'}</div>
                    <div className="text-sm">{msg.content}</div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Input */}
          <form onSubmit={handleSendMessage} className="p-4 border-t-2 border-black bg-gray-50 flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="输入消息..."
              className="flex-1 border-2 border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              type="submit"
              disabled={!inputValue.trim()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-5 h-5" /> 发送
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
