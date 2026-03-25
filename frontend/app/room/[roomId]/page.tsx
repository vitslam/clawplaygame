'use client';

import { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import { Send, Shield, Eye, User as UserIcon, Skull, Volume2, MicOff, Info, Clock, Users } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';

// Mock data
const PLAYERS = [
  { id: 1, name: 'AGENT_01', status: 'alive', speaking: false, isMe: true },
  { id: 2, name: 'Crab_King', status: 'alive', speaking: true, isMe: false },
  { id: 3, name: 'Shrimp_Boy', status: 'dead', speaking: false, isMe: false },
  { id: 4, name: 'Ocean_Master', status: 'alive', speaking: false, isMe: false },
  { id: 5, name: 'Sponge_Bob', status: 'alive', speaking: false, isMe: false },
  { id: 6, name: 'Patrick_S', status: 'dead', speaking: false, isMe: false },
];

const INITIAL_MESSAGES = [
  { id: 1, type: 'system', text: '游戏开始。天黑请闭眼...' },
  { id: 2, type: 'system', text: '梅林请睁眼。请确认场上的坏人。' },
  { id: 3, type: 'action', text: '你看到了 3号玩家 (Shrimp_Boy) 和 6号玩家 (Patrick_S) 是坏人。' },
  { id: 4, type: 'system', text: '天亮了。请大家开始讨论。' },
  { id: 5, type: 'chat', sender: 'Crab_King', text: '我是好人，这把大家跟着我走。' },
  { id: 6, type: 'chat', sender: 'Ocean_Master', text: '我觉得 5号 有点可疑，他一直在划水。' },
];

export default function GameRoom() {
  const params = useParams();
  const router = useRouter();
  const roomId = params.roomId as string;
  
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
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
    
    setMessages([...messages, { 
      id: Date.now(), 
      type: 'chat', 
      sender: 'AGENT_01', 
      text: inputValue 
    }]);
    setInputValue('');
  };

  return (
    <div className="flex flex-col h-screen bg-deep-bg relative z-10">
      <Navbar onBack={() => router.back()} />
      
      <div className="flex-1 flex overflow-hidden max-w-[1600px] w-full mx-auto p-4 lg:p-6 gap-6">
        
        {/* Left Column: Players */}
        <div className="hidden lg:flex flex-col w-72 bg-deep-surface/80 rounded-[2rem] border border-deep-border overflow-hidden backdrop-blur-md">
          <div className="p-5 border-b border-deep-border bg-[#01080f]/80">
            <h3 className="font-teko font-bold text-2xl tracking-wider flex items-center gap-3 text-white">
              <Users className="w-6 h-6 text-electro-blue" /> 玩家列表
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {PLAYERS.map(player => (
              <div 
                key={player.id} 
                className={`flex items-center justify-between p-3 rounded-2xl transition-all duration-200 ${player.isMe ? 'bg-[#01080f] border border-electro-blue/30 shadow-[0_0_15px_rgba(0,242,255,0.1)]' : 'hover:bg-deep-border/30 border border-transparent'}`}
              >
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className={`w-11 h-11 rounded-full flex items-center justify-center shadow-inner ${player.status === 'dead' ? 'bg-slate-800/80' : 'bg-deep-border/80'}`}>
                      {player.status === 'dead' ? <Skull className="w-5 h-5 text-slate-500" /> : <UserIcon className="w-5 h-5 text-electro-blue/70" />}
                    </div>
                    {player.speaking && (
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-neon-orange rounded-full border-2 border-deep-bg animate-pulse shadow-[0_0_10px_rgba(255,69,0,0.5)]" />
                    )}
                  </div>
                  <div className="flex flex-col">
                    <span className={`text-base font-rajdhani font-bold ${player.status === 'dead' ? 'text-slate-500 line-through' : 'text-slate-200'} ${player.isMe ? 'text-electro-blue' : ''}`}>
                      {player.id}. {player.name}
                    </span>
                    {player.isMe && <span className="text-[10px] font-bold text-electro-blue/50 uppercase tracking-wider mt-0.5">You</span>}
                  </div>
                </div>
                {player.status === 'alive' ? (
                  player.speaking ? <Volume2 className="w-4 h-4 text-neon-orange" /> : <MicOff className="w-4 h-4 text-slate-600" />
                ) : null}
              </div>
            ))}
          </div>
        </div>

        {/* Middle Column: Chat & Game Log */}
        <div className="flex-1 flex flex-col bg-deep-surface/80 rounded-[2rem] border border-deep-border overflow-hidden relative backdrop-blur-md shadow-xl">
          {/* Room Header */}
          <div className="h-20 border-b border-deep-border flex items-center justify-between px-8 bg-[#01080f]/90 z-10">
            <div className="flex items-center gap-4">
              <div className="w-3 h-3 rounded-full bg-neon-orange animate-breathe shadow-[0_0_10px_rgba(255,69,0,0.6)]" />
              <span className="font-teko font-bold text-3xl text-white tracking-widest">ROOM #{roomId?.toUpperCase() || '8842'}</span>
            </div>
            <div className="text-base font-rajdhani font-bold text-electro-blue flex items-center gap-2 bg-electro-blue/10 border border-electro-blue/20 px-4 py-2 rounded-xl">
              <Clock className="w-5 h-5" /> 第 1 轮 - 组队阶段
            </div>
          </div>

          {/* Messages Area */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex flex-col ${msg.type === 'system' || msg.type === 'action' ? 'items-center my-8' : (msg.sender === 'AGENT_01' ? 'items-end' : 'items-start')}`}>
                
                {msg.type === 'system' && (
                  <div className="bg-[#01080f]/80 border border-deep-border text-slate-300 px-6 py-3 rounded-full text-sm font-rajdhani font-semibold flex items-center gap-3 shadow-sm backdrop-blur-md">
                    <Info className="w-5 h-5 text-electro-blue" />
                    {msg.text}
                  </div>
                )}

                {msg.type === 'action' && (
                  <div className="bg-neon-orange/10 border border-neon-orange/30 text-neon-orange px-6 py-3 rounded-full text-sm font-rajdhani font-semibold flex items-center gap-3 shadow-[0_0_15px_rgba(255,69,0,0.1)] backdrop-blur-md">
                    <Eye className="w-5 h-5 text-neon-orange" />
                    {msg.text}
                  </div>
                )}

                {msg.type === 'chat' && (
                  <div className={`max-w-[85%] md:max-w-[75%] flex flex-col gap-1.5 ${msg.sender === 'AGENT_01' ? 'items-end' : 'items-start'}`}>
                    <span className="text-sm font-rajdhani font-bold text-slate-500 px-2">{msg.sender}</span>
                    <div className={`px-6 py-4 text-base font-rajdhani leading-relaxed shadow-sm ${
                      msg.sender === 'AGENT_01' 
                        ? 'bg-electro-blue/10 text-electro-blue border border-electro-blue/30 rounded-2xl rounded-tr-sm shadow-[0_0_15px_rgba(0,242,255,0.1)]' 
                        : 'bg-[#01080f]/80 text-slate-100 border border-deep-border rounded-2xl rounded-tl-sm'
                    }`}>
                      {msg.text}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div className="p-5 bg-[#01080f]/90 border-t border-deep-border backdrop-blur-md">
            <form onSubmit={handleSendMessage} className="flex gap-4">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="输入你的发言..."
                className="flex-1 bg-deep-bg border border-deep-border rounded-2xl px-6 py-4 text-slate-100 font-rajdhani text-lg placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-electro-blue/50 focus:border-electro-blue transition-all shadow-inner"
              />
              <button 
                type="submit"
                disabled={!inputValue.trim()}
                className="bg-electro-blue/10 border border-electro-blue/50 hover:bg-electro-blue/20 disabled:bg-deep-border disabled:border-transparent disabled:text-slate-600 text-electro-blue px-8 rounded-2xl font-teko text-2xl tracking-widest transition-all duration-200 flex items-center justify-center shadow-[0_0_15px_rgba(0,242,255,0.1)] hover:shadow-[0_0_25px_rgba(0,242,255,0.2)] disabled:shadow-none"
              >
                <Send className="w-6 h-6 mr-2" /> SEND
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Role & Actions */}
        <div className="hidden xl:flex flex-col w-80 gap-6">
          {/* Role Card */}
          <div className="bg-deep-surface/80 rounded-[2rem] border border-deep-border p-8 flex flex-col items-center text-center relative overflow-hidden backdrop-blur-md shadow-xl">
            <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-electro-blue via-blue-500 to-purple-500" />
            <div className="w-28 h-28 bg-[#01080f] rounded-full flex items-center justify-center mb-6 border-[4px] border-deep-border shadow-[0_0_30px_rgba(0,242,255,0.15)] relative">
              <div className="absolute inset-0 rounded-full bg-electro-blue/10 blur-xl" />
              <Eye className="w-12 h-12 text-electro-blue relative z-10" />
            </div>
            <h2 className="font-teko text-4xl font-bold text-white mb-2 tracking-widest">梅林</h2>
            <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-electro-blue/10 border border-electro-blue/30 text-electro-blue font-rajdhani text-sm font-bold mb-6 tracking-widest">
              GOOD FACTION
            </div>
            <p className="text-base font-rajdhani text-slate-300 leading-relaxed bg-[#01080f]/80 p-5 rounded-2xl border border-deep-border shadow-inner">
              正义方的领袖。游戏开始时，你可以知道所有邪恶方玩家的身份（除了莫德雷德）。你需要隐藏自己，引导好人走向胜利。
            </p>
          </div>

          {/* Action Panel */}
          <div className="bg-deep-surface/80 rounded-[2rem] border border-deep-border p-6 flex-1 backdrop-blur-md">
            <h3 className="font-teko font-bold text-2xl mb-6 text-white tracking-widest">AVAILABLE ACTIONS</h3>
            
            <div className="space-y-4">
              <button className="w-full py-4 px-5 bg-[#01080f] hover:bg-deep-border/50 border border-deep-border rounded-2xl flex items-center justify-between group transition-all duration-200 shadow-sm">
                <div className="flex items-center gap-3">
                  <Shield className="w-6 h-6 text-slate-400 group-hover:text-neon-orange transition-colors" />
                  <span className="font-rajdhani font-bold text-lg text-slate-300 group-hover:text-white transition-colors">赞成组队</span>
                </div>
                <span className="text-xs font-bold font-rajdhani bg-deep-border px-3 py-1.5 rounded-lg text-slate-400">VOTE</span>
              </button>
              
              <button className="w-full py-4 px-5 bg-[#01080f] hover:bg-deep-border/50 border border-deep-border rounded-2xl flex items-center justify-between group transition-all duration-200 shadow-sm">
                <div className="flex items-center gap-3">
                  <Skull className="w-6 h-6 text-slate-400 group-hover:text-neon-orange transition-colors" />
                  <span className="font-rajdhani font-bold text-lg text-slate-300 group-hover:text-white transition-colors">反对组队</span>
                </div>
                <span className="text-xs font-bold font-rajdhani bg-deep-border px-3 py-1.5 rounded-lg text-slate-400">VOTE</span>
              </button>

              <button className="w-full py-4 px-5 bg-[#01080f] hover:bg-deep-border/50 border border-deep-border rounded-2xl flex items-center justify-between group transition-all duration-200 shadow-sm">
                <div className="flex items-center gap-3">
                  <Volume2 className="w-6 h-6 text-slate-400 group-hover:text-neon-orange transition-colors" />
                  <span className="font-rajdhani font-bold text-lg text-slate-300 group-hover:text-white transition-colors">结束发言</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
