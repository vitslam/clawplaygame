'use client';

import { useState } from 'react';
import { useUser } from '@/lib/UserContext';

interface AuthModalProps {
  onClose: () => void;
}

export default function AuthModal({ onClose }: AuthModalProps) {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const { setUser } = useUser();
  
  // 登录表单
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  
  // 注册表单
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerNickname, setRegisterNickname] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('/api/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: loginUsername, password: loginPassword }),
      });
      const data = await res.json();
      
      if (data.success) {
        setUser({ id: data.user.id, nickname: data.user.nickname });
        onClose();
      } else {
        setError(data.message || '登录失败');
      }
    } catch (err) {
      setError('登录失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('/api/users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          username: registerUsername, 
          password: registerPassword,
          nickname: registerNickname || registerUsername,
        }),
      });
      const data = await res.json();
      
      if (data.success) {
        setUser({ id: data.user.id, nickname: data.user.nickname });
        onClose();
      } else {
        setError(data.message || '注册失败');
      }
    } catch (err) {
      setError('注册失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white border-2 border-black p-8 max-w-md w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        {/* 标签页 */}
        <div className="flex border-b-2 border-black mb-6">
          <button
            onClick={() => { setActiveTab('login'); setError(''); }}
            className={`flex-1 py-3 font-bold uppercase transition-all ${
              activeTab === 'login' 
                ? 'bg-black text-white' 
                : 'bg-gray-100 text-black hover:bg-gray-200'
            }`}
          >
            登录
          </button>
          <button
            onClick={() => { setActiveTab('register'); setError(''); }}
            className={`flex-1 py-3 font-bold uppercase transition-all ${
              activeTab === 'register' 
                ? 'bg-black text-white' 
                : 'bg-gray-100 text-black hover:bg-gray-200'
            }`}
          >
            注册
          </button>
        </div>

        {/* 登录表单 */}
        {activeTab === 'login' && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block font-bold uppercase mb-2 text-sm">用户名</label>
              <input
                type="text"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                placeholder="输入用户名"
                className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block font-bold uppercase mb-2 text-sm">密码</label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="输入密码"
                className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            {error && (
              <div className="text-red-600 font-bold text-sm">{error}</div>
            )}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-200 text-black px-6 py-3 border-2 border-black font-bold uppercase hover:bg-gray-300 transition-all"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
              >
                {loading ? '登录中...' : '登录'}
              </button>
            </div>
          </form>
        )}

        {/* 注册表单 */}
        {activeTab === 'register' && (
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block font-bold uppercase mb-2 text-sm">用户名</label>
              <input
                type="text"
                value={registerUsername}
                onChange={(e) => setRegisterUsername(e.target.value)}
                placeholder="设置用户名"
                className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block font-bold uppercase mb-2 text-sm">密码</label>
              <input
                type="password"
                value={registerPassword}
                onChange={(e) => setRegisterPassword(e.target.value)}
                placeholder="设置密码"
                className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block font-bold uppercase mb-2 text-sm">昵称（可选）</label>
              <input
                type="text"
                value={registerNickname}
                onChange={(e) => setRegisterNickname(e.target.value)}
                placeholder="设置昵称（默认与用户名相同）"
                className="w-full border-2 border-black px-4 py-3 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {error && (
              <div className="text-red-600 font-bold text-sm">{error}</div>
            )}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-200 text-black px-6 py-3 border-2 border-black font-bold uppercase hover:bg-gray-300 transition-all"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-black text-white px-6 py-3 border-2 border-black font-bold uppercase hover:bg-white hover:text-black disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
              >
                {loading ? '注册中...' : '注册'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
