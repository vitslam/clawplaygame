'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { Users, Lock, Unlock, Loader2, Plus } from 'lucide-react';
import { getGame, listRooms, type Game } from '@/lib/api';

interface Room {
  id: string;
  game_id: string;
  host_name: string;
  players: Array<{ id: string; name: string }>;
  status: string;
  max_players: number;
}

const GAME_NAMES: Record<string, string> = {
  werewolf: '狼人杀',
  avalon: '阿瓦隆',
  botc: '血染钟楼',
  spyfall: '间谍危机',
};

export default function RoomList() {
  const params = useParams();
  const router = useRouter();
  const gameId = params.id as string;
  
  const [game, setGame] = useState<Game | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [playerName, setPlayerName] = useState('');

  useEffect(() => {
    Promise.all([
      getGame(gameId),
      listRooms(gameId)
    ])
      .then(([gameData, roomsData]) => {
        setGame(gameData);
        setRooms(roomsData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [gameId]);

  const handleCreateRoom = async () => {
    if (!playerName.trim()) {
      alert('请输入你的昵称');
      return;
    }
    
    try {
      const { createRoom } = await import('@/lib/api');
      const room = await createRoom(gameId, playerName, true);
      router.push(`/game/${gameId}/room/${room.id}`);
    } catch (err) {
      alert('创建房间失败：' + (err as Error).message);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col min-h-screen bg-[#f4f4f4]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
        </main>
      </div>
    );
  }

  const gameName = game ? GAME_NAMES[game.id] || game.name : gameId;

  return (
    <div className="flex flex-col min-h-screen bg-[#f4f4f4]">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 py-12 w-full flex-1">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
          <div>
            <Link href="/" className="font-mono text-sm font-bold uppercase underline hover:bg-black hover:text-white px-2 py-1 -ml-2 transition-colors mb-4 inline-block">
              ← 返回大厅
            </Link>
            <h1 className="text-5xl font-black uppercase tracking-tight">{gameName} 房间</h1>
          </div>
          
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="你的昵称"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              className="border-2 border-black px-4 py-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              onClick={handleCreateRoom}
              className="bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all whitespace-nowrap flex items-center gap-2"
            >
              <Plus className="w-5 h-5" /> 创建房间
            </button>
          </div>
        </div>

        {rooms.length === 0 ? (
          <div className="text-center py-20">
            <Users className="w-24 h-24 mx-auto text-gray-300 mb-4" />
            <h3 className="text-2xl font-bold text-gray-400 mb-2">暂无房间</h3>
            <p className="text-gray-500 mb-6">创建第一个房间开始游戏吧！</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {rooms.map((room) => (
              <Link 
                href={`/game/${gameId}/room/${room.id}`} 
                key={room.id} 
                className="group flex flex-col border-2 border-black bg-white p-6 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all"
              >
                <div className="flex justify-between items-start mb-4">
                  <span className="font-mono text-sm font-bold uppercase">#{room.id}</span>
                  <span className={`font-mono text-xs font-bold uppercase px-2 py-1 border-2 border-black ${room.status === 'waiting' ? 'bg-[#16a34a] text-white' : 'bg-gray-200 text-black'}`}>
                    {room.status === 'waiting' ? '等待中' : room.status === 'playing' ? '游戏中' : '已结束'}
                  </span>
                </div>
                
                <h2 className="text-2xl font-black uppercase tracking-tight mb-2 group-hover:underline decoration-4 underline-offset-4 truncate">
                  {room.host_name} 的房间
                </h2>
                <p className="font-mono text-sm uppercase text-gray-600 mb-6">房主：{room.host_name}</p>
                
                <div className="flex items-center justify-between font-mono text-sm font-bold uppercase mt-auto pt-4 border-t-2 border-black">
                  <div className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    <span className={room.players.length === room.max_players ? 'text-[#dc2626]' : ''}>
                      {room.players.length} / {room.max_players}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Unlock className="w-5 h-5" />
                    <span>公开</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
