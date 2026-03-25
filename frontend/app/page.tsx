'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { Users, Clock, Tag, Play, Activity, Loader2 } from 'lucide-react';
import { listGames, type Game } from '@/lib/api';

const GAME_COLORS: Record<string, string> = {
  werewolf: 'bg-blue-600',
  avalon: 'bg-red-600',
  botc: 'bg-purple-600',
  spyfall: 'bg-green-600',
};

const STATUS_MAP: Record<string, { text: string; className: string }> = {
  active: { text: '活跃', className: 'bg-[#16a34a] text-white' },
  beta: { text: '测试中', className: 'bg-gray-200 text-black' },
  maintenance: { text: '维护中', className: 'bg-orange-400 text-white' },
};

export default function Home() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listGames()
      .then(setGames)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

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

  if (error) {
    return (
      <div className="flex flex-col min-h-screen bg-[#f4f4f4]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-black text-red-600 mb-2">加载失败</h2>
            <p className="text-gray-600">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-6 py-2 bg-blue-600 text-white font-bold rounded hover:bg-blue-700"
            >
              重新加载
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#f4f4f4]">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 py-12 w-full flex-1">
        <div className="mb-12">
          <h1 className="text-5xl font-black uppercase tracking-tight mb-4">游戏大厅</h1>
          <p className="text-lg font-mono uppercase text-gray-600">选择一个游戏加入或创建房间。</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {games.map((game) => {
            const color = GAME_COLORS[game.id] || 'bg-gray-600';
            const status = STATUS_MAP[game.status] || STATUS_MAP.maintenance;
            
            return (
              <Link 
                href={`/game/${game.id}`} 
                key={game.id} 
                className="group flex flex-col border-2 border-black bg-white p-6 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all"
              >
                <div className="flex justify-between items-start mb-6">
                  <div className={`w-12 h-12 border-2 border-black ${color} flex items-center justify-center`}>
                    <Play className="w-6 h-6 text-white ml-1" />
                  </div>
                  <span className={`font-mono text-xs font-bold uppercase px-2 py-1 border-2 border-black ${status.className}`}>
                    {status.text}
                  </span>
                </div>
                
                <h2 className="text-3xl font-black uppercase tracking-tight mb-4 group-hover:underline decoration-4 underline-offset-4">{game.name}</h2>
                
                <div className="space-y-3 font-mono text-sm font-bold uppercase mt-auto">
                  <div className="flex items-center gap-3">
                    <Users className="w-5 h-5" />
                    <span>{game.min_players}-{game.max_players} 人</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5" />
                    <span>{game.duration_minutes}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Tag className="w-5 h-5" />
                    <span>{game.type}</span>
                  </div>
                  <div className="flex items-center gap-3 pt-4 mt-4 border-t-2 border-black">
                    <Activity className="w-5 h-5" />
                    <span>{game.active_players.toLocaleString()} 人正在游玩</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </main>
    </div>
  );
}
