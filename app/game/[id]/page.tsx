import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { Users, Lock, Unlock, Play } from 'lucide-react';

const ROOMS = [
  { id: '1001', name: '新手欢迎', host: 'Lobster_01', players: 8, max: 12, status: '等待中', isPrivate: false },
  { id: '1002', name: '仅限高手', host: 'Crab_King', players: 12, max: 12, status: '游戏中', isPrivate: true },
  { id: '1003', name: '休闲局', host: 'Shrimp_Boy', players: 4, max: 8, status: '等待中', isPrivate: false },
  { id: '1004', name: '仅限语音', host: 'Whale_Song', players: 10, max: 10, status: '游戏中', isPrivate: false },
  { id: '1005', name: '深夜修仙', host: 'Squid_Ward', players: 1, max: 6, status: '等待中', isPrivate: true },
];

const GAME_NAMES: Record<string, string> = {
  'WEREWOLF': '狼人杀',
  'AVALON': '阿瓦隆',
  'BOTC': '血染钟楼',
  'SPYFALL': '间谍危机',
};

export default async function RoomList({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params;
  const gameId = resolvedParams.id.toUpperCase();
  const gameName = GAME_NAMES[gameId] || gameId;

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
          <Link 
            href={`/game/${resolvedParams.id}/room/new`}
            className="bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all whitespace-nowrap text-center"
          >
            + 创建房间
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ROOMS.map((room) => (
            <Link 
              href={`/game/${resolvedParams.id}/room/${room.id}`} 
              key={room.id} 
              className="group flex flex-col border-2 border-black bg-white p-6 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all"
            >
              <div className="flex justify-between items-start mb-4">
                <span className="font-mono text-sm font-bold uppercase">#{room.id}</span>
                <span className={`font-mono text-xs font-bold uppercase px-2 py-1 border-2 border-black ${room.status === '等待中' ? 'bg-[#16a34a] text-white' : 'bg-gray-200 text-black'}`}>
                  {room.status}
                </span>
              </div>
              
              <h2 className="text-2xl font-black uppercase tracking-tight mb-2 group-hover:underline decoration-4 underline-offset-4 truncate">{room.name}</h2>
              <p className="font-mono text-sm uppercase text-gray-600 mb-6">房主: {room.host}</p>
              
              <div className="flex items-center justify-between font-mono text-sm font-bold uppercase mt-auto pt-4 border-t-2 border-black">
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  <span className={room.players === room.max ? 'text-[#dc2626]' : ''}>
                    {room.players} / {room.max}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {room.isPrivate ? <Lock className="w-5 h-5" /> : <Unlock className="w-5 h-5" />}
                  <span>{room.isPrivate ? '私密' : '公开'}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
