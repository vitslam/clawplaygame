'use client';

import { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import { Send, User as UserIcon, Skull, Volume2, MicOff, Info, Clock, Users, Loader2 } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { getRoom, joinRoom, getMessages, sendMessage, createWebSocket, type Room as RoomType, type Message, type Player } from '@/lib/api';

export default function GameRoom() {
  const params = useParams();
  const router = useRouter();
  const roomId = params.roomId as string;
  
  const [room, setRoom] = useState<RoomType | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [playerId, setPlayerId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
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
      
      setLoading(false);
    } catch (err) {
      setError((err as Error).message);
      setLoading(false);
    }
  };

  const handleJoin = async (playerName: string) => {
    try {
      const { joinRoom } = await import('@/lib/api');
      const result = await joinRoom(roomId, playerName);
      setPlayerId(result.player.id);
      setRoom(result.room);
      loadRoom();
    } catch (err) {
      alert('加入房间失败：' + (err as Error).message);
    }
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

  if (!playerId) {
    return (
      <div className="flex flex-col h-screen bg-[#f4f4f4]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white border-2 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <h2 className="text-3xl font-black uppercase mb-6 text-center">加入房间</h2>
            <p className="font-mono text-sm mb-6 text-center">房间 #{roomId}</p>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              handleJoin(formData.get('playerName') as string);
            }}>
              <input
                name="playerName"
                type="text"
                placeholder="你的昵称"
                className="w-full border-2 border-black px-4 py-3 font-mono mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <button 
                type="submit"
                className="w-full bg-black text-white py-3 font-bold uppercase hover:bg-white hover:text-black border-2 border-black transition-all"
              >
                加入游戏
              </button>
            </form>
          </div>
        </main>
      </div>
    );
  }

  const me = room?.players.find(p => p.id === playerId);

  return (
    <div className="flex flex-col h-screen bg-[#f4f4f4]">
      <Navbar />
      
      <div className="flex-1 flex overflow-hidden max-w-[1600px] w-full mx-auto p-4 lg:p-6 gap-6">
        
        {/* Left Column: Players */}
        <div className="hidden lg:flex flex-col w-72 bg-white border-2 border-black rounded-xl overflow-hidden">
          <div className="p-5 border-b-2 border-black bg-gray-100">
            <h3 className="font-bold text-xl flex items-center gap-3">
              <Users className="w-6 h-6" /> 玩家列表 ({room?.players.length || 0})
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
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
              <span className="font-black text-xl">ROOM #{roomId.toUpperCase()}</span>
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
