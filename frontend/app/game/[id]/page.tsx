'use client';

import { useState, useEffect, useMemo } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { Users, Lock, Unlock, Loader2, Plus, Search, LogIn } from 'lucide-react';
import { getGame, listRooms, type Game } from '@/lib/api';
import { useUser } from '@/lib/UserContext';

interface Room {
  id: string;
  game_id: string;
  room_name: string;
  host_name: string;
  players: any[];
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
  const { user } = useUser();
  
  const [game, setGame] = useState<Game | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // 创建房间表单状态
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [roomName, setRoomName] = useState('');
  const [maxPlayers, setMaxPlayers] = useState(10);
  const [isPublic, setIsPublic] = useState(true);

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

  // 过滤后的房间列表（根据搜索关键字）
  const filteredRooms = useMemo(() => {
    if (!searchQuery.trim()) return rooms;
    
    const query = searchQuery.toLowerCase();
    return rooms.filter(room => 
      room.room_name.toLowerCase().includes(query) ||
      room.id.toLowerCase().includes(query) ||
      room.host_name.toLowerCase().includes(query)
    );
  }, [rooms, searchQuery]);

  const handleCreateRoom = async () => {
    if (!user) {
      setShowLoginModal(true);
      return;
    }
    if (!roomName.trim()) {
      alert('请输入房间名称');
      return;
    }
    
    try {
      const { createRoom } = await import('@/lib/api');
      const room = await createRoom(gameId, user.nickname, roomName, maxPlayers, isPublic, user.id);
      router.push(`/room/${room.id}`);
    } catch (err) {
      alert('创建房间失败：' + (err as Error).message);
    }
  };

  const openCreateModal = () => {
    if (!user) {
      setShowLoginModal(true);
      return;
    }
    setRoomName(`${user.nickname} 的房间`);
    setMaxPlayers(10);
    setIsPublic(true);
    setShowCreateModal(true);
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
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="搜索房间..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full border-2 border-black pl-10 pr-4 py-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button 
              onClick={openCreateModal}
              className="bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all whitespace-nowrap flex items-center gap-2"
            >
              <Plus className="w-5 h-5" /> 创建房间
            </button>
          </div>
        </div>

        {filteredRooms.length === 0 ? (
          <div className="text-center py-20">
            <Search className="w-24 h-24 mx-auto text-gray-300 mb-4" />
            <h3 className="text-2xl font-bold text-gray-400 mb-2">
              {searchQuery ? `没有找到匹配"${searchQuery}"的房间` : '暂无房间'}
            </h3>
            <p className="text-gray-500 mb-6">
              {searchQuery ? '试试其他关键词' : '创建第一个房间开始游戏吧！'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRooms.map((room) => (
              <Link 
                href={`/room/${room.id}`} 
                key={room.id} 
                className="group flex flex-col border-2 border-black bg-white p-6 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all"
              >
                <div className="flex justify-between items-start mb-4">
                  <span className="font-mono text-sm font-bold uppercase">#{room.id}</span>
                  <span className={`font-mono text-xs font-bold uppercase px-2 py-1 border-2 border-black ${
                    room.status === 'waiting' ? 'bg-blue-500 text-white' : 
                    room.status === 'playing' ? 'bg-[#16a34a] text-white' : 
                    'bg-gray-400 text-white'
                  }`}>
                    {room.status === 'waiting' ? '等待中' : room.status === 'playing' ? '游戏中' : '已结束'}
                  </span>
                </div>
                
                <h2 className="text-2xl font-black uppercase tracking-tight mb-2 group-hover:underline decoration-4 underline-offset-4 truncate">
                  {room.room_name}
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

      {/* 未登录提示弹窗 */}
      {showLoginModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white border-2 border-black p-8 max-w-sm w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] text-center">
            <LogIn className="w-16 h-16 mx-auto mb-4 text-blue-600" />
            <h3 className="text-2xl font-black uppercase mb-4">需要登录</h3>
            <p className="text-gray-600 mb-6">创建房间需要先登录账号。</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowLoginModal(false)}
                className="flex-1 bg-gray-200 text-black px-6 py-3 border-2 border-black font-bold uppercase hover:bg-gray-300"
              >
                取消
              </button>
              <Link
                href="/"
                className="flex-1 bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black inline-block text-center"
              >
                去登录
              </Link>
            </div>
          </div>
        </div>
      )}
      
      {/* 创建房间模态框 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white border-2 border-black p-8 max-w-md w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <h2 className="text-3xl font-black uppercase mb-6">创建房间</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block font-bold uppercase mb-2 text-sm">房间名称</label>
                <input
                  type="text"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  placeholder="例如：新手局、高手场"
                  className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block font-bold uppercase mb-2 text-sm">人数上限：{maxPlayers}人</label>
                <input
                  type="range"
                  min="5"
                  max="12"
                  value={maxPlayers}
                  onChange={(e) => setMaxPlayers(Number(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs font-mono mt-1">
                  <span>5</span>
                  <span>12</span>
                </div>
              </div>

              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    className="w-5 h-5 border-2 border-black"
                  />
                  <span className="font-bold uppercase text-sm">公开房间（其他人可见）</span>
                </label>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-200 text-black px-6 py-3 border-2 border-black font-bold uppercase hover:bg-gray-300 transition-all"
                >
                  取消
                </button>
                <button
                  onClick={handleCreateRoom}
                  className="flex-1 bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black transition-all"
                >
                  创建
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
