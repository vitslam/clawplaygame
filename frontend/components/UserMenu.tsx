'use client';

import { useState, useRef, useEffect } from 'react';
import { useUser } from '@/lib/UserContext';
import { LogOut, Image, User } from 'lucide-react';

// 默认头像列表（像素风）
const DEFAULT_AVATARS = [
  '🐙', '🦞', '🦀', '🦐', '🦑',
  '🐟', '🐠', '🐡', '🐬', '🐳',
  '🦈', '🐊', '🐢', '🐸', '🦎',
  '🐍', '🦕', '🦖', '🐙', '🦑',
];

interface UserMenuProps {
  onClose?: () => void;
}

export default function UserMenu({ onClose }: UserMenuProps) {
  const { user, setUser, clearUser } = useUser();
  const [showDropdown, setShowDropdown] = useState(false);
  const [showAvatarPicker, setShowAvatarPicker] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
        setShowAvatarPicker(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    clearUser();
    setShowDropdown(false);
    onClose?.();
  };

  const handleSelectAvatar = (avatar: string) => {
    if (user) {
      setUser({ ...user, avatar });
    }
    setShowAvatarPicker(false);
  };

  const currentAvatar = user?.avatar || DEFAULT_AVATARS[0];

  return (
    <div className="relative" ref={dropdownRef}>
      {/* 用户头像按钮 */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 px-3 py-1 rounded transition-colors group"
      >
        <span className="text-2xl">{currentAvatar}</span>
        <span className="font-bold text-sm hidden sm:inline group-hover:underline">{user?.nickname}</span>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* 下拉菜单 */}
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-64 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] z-50">
          {/* 用户信息 */}
          <div className="p-4 border-b-2 border-black bg-gray-50">
            <div className="flex items-center gap-3">
              <span className="text-4xl">{currentAvatar}</span>
              <div>
                <div className="font-bold text-lg">{user?.nickname}</div>
                <div className="text-xs text-gray-600 font-mono">{user?.id}</div>
              </div>
            </div>
          </div>

          {/* 菜单项 */}
          <div className="p-2">
            <button
              onClick={() => setShowAvatarPicker(!showAvatarPicker)}
              className="w-full flex items-center gap-3 px-4 py-3 hover:underline font-bold uppercase text-sm transition-colors"
            >
              <Image className="w-5 h-5" />
              更换头像
            </button>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-600 hover:text-white font-bold uppercase text-sm transition-colors"
            >
              <LogOut className="w-5 h-5" />
              退出登录
            </button>
          </div>

          {/* 头像选择器 */}
          {showAvatarPicker && (
            <div className="p-4 border-t-2 border-black bg-gray-50">
              <div className="font-bold uppercase text-sm mb-3">选择头像</div>
              <div className="grid grid-cols-5 gap-2">
                {DEFAULT_AVATARS.map((avatar) => (
                  <button
                    key={avatar}
                    onClick={() => handleSelectAvatar(avatar)}
                    className="text-3xl p-2 rounded transition-all hover:translate-y-[-2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                  >
                    {avatar}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
