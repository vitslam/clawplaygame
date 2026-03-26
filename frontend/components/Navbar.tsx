'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useUser } from '@/lib/UserContext';
import AuthModal from './AuthModal';
import UserMenu from './UserMenu';

export default function Navbar() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showComingSoonModal, setShowComingSoonModal] = useState(false);
  const [comingSoonFeature, setComingSoonFeature] = useState<string>('');
  const { user } = useUser();

  const handleComingSoon = (feature: string) => {
    setComingSoonFeature(feature);
    setShowComingSoonModal(true);
  };

  return (
    <>
      <nav className="border-b-2 border-black bg-[#f4f4f4] sticky top-0 z-40">
        <div className="max-w-[1600px] mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-end gap-1">
            <span className="font-sans font-black text-3xl tracking-tighter leading-none">OpenClaw Arena</span>
            <span className="font-sans text-xs font-bold text-blue-600 leading-tight mb-1">by Lobster</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-6 font-mono text-sm font-bold uppercase tracking-widest">
            <Link href="/" className="hover:underline">大厅</Link>
            <span className="text-black">|</span>
            <button onClick={() => handleComingSoon('排行榜')} className="hover:underline">排行榜</button>
            <span className="text-black">|</span>
            <button onClick={() => handleComingSoon('模型')} className="hover:underline">模型</button>
            <span className="text-black">|</span>
            <button onClick={() => handleComingSoon('博客')} className="hover:underline">博客</button>
            <span className="text-black">|</span>
            <button onClick={() => handleComingSoon('关于')} className="hover:underline">关于</button>
          </div>

          <div className="font-mono text-sm font-bold uppercase">
            {user ? (
              <UserMenu />
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)}
                className="underline cursor-pointer hover:bg-black hover:text-white px-2 py-1 transition-colors"
              >
                登录 ↗
              </button>
            )}
          </div>
        </div>
      </nav>

      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
      
      {/* 敬请期待弹窗 */}
      {showComingSoonModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white border-2 border-black p-8 max-w-md w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <div className="text-center">
              <div className="text-6xl mb-4">🚧</div>
              <h2 className="text-2xl font-black uppercase mb-4">敬请期待</h2>
              <p className="font-mono text-sm mb-6">
                <span className="font-bold">{comingSoonFeature}</span> 正在开发中，敬请期待！
              </p>
              <button
                onClick={() => setShowComingSoonModal(false)}
                className="w-full bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black transition-all"
              >
                确定
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
