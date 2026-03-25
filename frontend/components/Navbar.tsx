'use client';

import Link from 'next/link';
import { useState } from 'react';
import AuthModal from './AuthModal';

export default function Navbar() {
  const [showAuthModal, setShowAuthModal] = useState(false);

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
            <Link href="/" className="hover:underline">排行榜</Link>
            <span className="text-black">|</span>
            <Link href="/" className="hover:underline">模型</Link>
            <span className="text-black">|</span>
            <Link href="/" className="hover:underline">博客</Link>
            <span className="text-black">|</span>
            <Link href="/" className="hover:underline">关于</Link>
          </div>

          <div className="font-mono text-sm font-bold uppercase">
            <button 
              onClick={() => setShowAuthModal(true)}
              className="underline cursor-pointer hover:bg-black hover:text-white px-2 py-1 transition-colors"
            >
              登录 ↗
            </button>
          </div>
        </div>
      </nav>

      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </>
  );
}
