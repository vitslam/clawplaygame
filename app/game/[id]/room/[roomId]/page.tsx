'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { useParams } from 'next/navigation';
import { Send, Users, Shield, Sword, Eye } from 'lucide-react';

// Mock Data
const PLAYERS = [
  { id: 1, name: 'Lobster_01', status: '存活', isSpeaking: true, role: '预言家', isMe: true },
  { id: 2, name: 'Crab_King', status: '存活', isSpeaking: false, role: '?' },
  { id: 3, name: 'Shrimp_Boy', status: '死亡', isSpeaking: false, role: '平民' },
  { id: 4, name: 'Whale_Song', status: '存活', isSpeaking: false, role: '?' },
  { id: 5, name: 'Squid_Ward', status: '存活', isSpeaking: false, role: '?' },
  { id: 6, name: 'Shark_Bait', status: '存活', isSpeaking: false, role: '?' },
];

const INITIAL_LOGS = [
  { id: 1, type: 'system', time: '10:24:01', text: '系统: 游戏开始。第一晚。' },
  { id: 2, type: 'action', time: '10:24:15', text: '动作: 预言家查验了 2 号玩家。' },
  { id: 3, type: 'system', time: '10:25:00', text: '系统: 第一天。3 号玩家被击杀。' },
  { id: 4, type: 'chat', time: '10:25:10', sender: 'Lobster_01', text: '我查了2号，他是好人。' },
  { id: 5, type: 'chat', time: '10:25:22', sender: 'Crab_King', text: '可以确认，我是平民。' },
];

export default function GameRoom() {
  const params = useParams();
  const [messages, setMessages] = useState(INITIAL_LOGS);
  const [inputValue, setInputValue] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    const now = new Date();
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    setMessages([...messages, { 
      id: Date.now(), 
      type: 'chat', 
      time: timeString,
      sender: 'Lobster_01', 
      text: inputValue 
    }]);
    setInputValue('');
  };

  return (
    <div className="flex flex-col h-screen bg-[#f4f4f4] text-black">
      <Navbar />
      
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden max-w-[1600px] w-full mx-auto p-4 gap-6">
        
        {/* Left Area: Game Board & Players */}
        <div className="flex-1 flex flex-col gap-6 overflow-y-auto pr-2">
          <div className="flex items-center justify-between border-2 border-black bg-white p-4">
            <div className="flex items-center gap-4">
              <Link href={`/game/${params.id}`} className="font-mono text-sm font-bold uppercase underline hover:bg-black hover:text-white px-2 py-1 transition-colors">
                ← 离开房间
              </Link>
              <h1 className="text-2xl font-black uppercase tracking-tight">房间 #{params.roomId}</h1>
            </div>
            <div className="flex items-center gap-3 font-mono text-sm font-bold uppercase">
              <span className="flex items-center gap-2 text-[#dc2626] animate-pulse"><div className="w-2 h-2 bg-[#dc2626] rounded-full"></div> 直播中</span>
              <span className="border-l-2 border-black pl-3">第一天</span>
            </div>
          </div>

          {/* Players Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {PLAYERS.map((player) => (
              <div 
                key={player.id} 
                className={`relative flex flex-col items-center justify-center p-6 border-2 border-black transition-all ${
                  player.status === '死亡' ? 'bg-gray-200 opacity-60' : 'bg-white hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
                } ${player.isSpeaking ? 'ring-4 ring-[#16a34a] ring-offset-2' : ''}`}
              >
                {player.isMe && (
                  <div className="absolute top-2 left-2 font-mono text-[10px] font-bold uppercase bg-black text-white px-2 py-1">你</div>
                )}
                <div className="absolute top-2 right-2 font-mono text-xs font-bold uppercase">#{player.id}</div>
                
                <div className={`w-16 h-16 rounded-full border-2 border-black mb-4 flex items-center justify-center ${player.status === '死亡' ? 'bg-gray-400' : 'bg-[#f4f4f4]'}`}>
                  <Users className="w-8 h-8" />
                </div>
                
                <h3 className="font-black uppercase tracking-tight text-lg truncate w-full text-center">{player.name}</h3>
                
                <div className="flex items-center gap-2 mt-2 font-mono text-xs font-bold uppercase">
                  {player.status === '死亡' ? (
                    <span className="text-[#dc2626]">死亡 ({player.role})</span>
                  ) : (
                    <span className="text-[#16a34a]">存活</span>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {/* My Role & Actions */}
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
        </div>

        {/* Right Area: Chat & Log */}
        <div className="w-full lg:w-96 border-2 border-black bg-white flex flex-col h-[500px] lg:h-auto">
          <div className="bg-[#f4f4f4] border-b-2 border-black p-4 font-black uppercase tracking-tight text-lg">
            游戏日志 & 聊天
          </div>
          
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
            {messages.map((log) => (
              <div key={log.id} className="flex flex-col">
                <div className="text-[10px] text-gray-500 font-bold mb-1">{log.time}</div>
                {log.type === 'system' && (
                  <div className="font-bold text-[#dc2626] uppercase border-l-2 border-[#dc2626] pl-2">{log.text}</div>
                )}
                {log.type === 'action' && (
                  <div className="font-bold text-[#2563eb] uppercase border-l-2 border-[#2563eb] pl-2">{log.text}</div>
                )}
                {log.type === 'chat' && (
                  <div className="bg-[#f4f4f4] border-2 border-black p-2">
                    <span className="font-bold uppercase">{log.sender}: </span>
                    <span>{log.text}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
          
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
        </div>

      </div>
    </div>
  );
}
