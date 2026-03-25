import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { Users, Clock, Tag, Play, Activity } from 'lucide-react';

const GAMES = [
  {
    id: 'werewolf',
    name: '狼人杀',
    players: '6-12',
    time: '30-60分钟',
    type: '社交推理',
    status: '活跃',
    color: 'bg-blue-600',
    activePlayers: 10730,
  },
  {
    id: 'avalon',
    name: '阿瓦隆',
    players: '5-10',
    time: '30-45分钟',
    type: '社交推理',
    status: '活跃',
    color: 'bg-red-600',
    activePlayers: 8955,
  },
  {
    id: 'botc',
    name: '血染钟楼',
    players: '5-20',
    time: '60-120分钟',
    type: '社交推理',
    status: '测试中',
    color: 'bg-purple-600',
    activePlayers: 5101,
  },
  {
    id: 'spyfall',
    name: '间谍危机',
    players: '3-8',
    time: '15-30分钟',
    type: '派对游戏',
    status: '活跃',
    color: 'bg-green-600',
    activePlayers: 8748,
  },
];

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#f4f4f4]">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 py-12 w-full flex-1">
        <div className="mb-12">
          <h1 className="text-5xl font-black uppercase tracking-tight mb-4">游戏大厅</h1>
          <p className="text-lg font-mono uppercase text-gray-600">选择一个游戏加入或创建房间。</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {GAMES.map((game) => (
            <Link 
              href={`/game/${game.id}`} 
              key={game.id} 
              className="group flex flex-col border-2 border-black bg-white p-6 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all"
            >
              <div className="flex justify-between items-start mb-6">
                <div className={`w-12 h-12 border-2 border-black ${game.color} flex items-center justify-center`}>
                  <Play className="w-6 h-6 text-white ml-1" />
                </div>
                <span className={`font-mono text-xs font-bold uppercase px-2 py-1 border-2 border-black ${game.status === '活跃' ? 'bg-[#16a34a] text-white' : 'bg-gray-200 text-black'}`}>
                  {game.status}
                </span>
              </div>
              
              <h2 className="text-3xl font-black uppercase tracking-tight mb-4 group-hover:underline decoration-4 underline-offset-4">{game.name}</h2>
              
              <div className="space-y-3 font-mono text-sm font-bold uppercase mt-auto">
                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5" />
                  <span>{game.players} 人</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5" />
                  <span>{game.time}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Tag className="w-5 h-5" />
                  <span>{game.type}</span>
                </div>
                <div className="flex items-center gap-3 pt-4 mt-4 border-t-2 border-black">
                  <Activity className="w-5 h-5" />
                  <span>{game.activePlayers.toLocaleString()} 人正在游玩</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
