import React from 'react';
import { Home, User, Settings } from 'lucide-react';
import type { Screen } from '../App';

interface BottomNavigationProps {
  currentScreen: Screen;
  onScreenChange: (screen: Screen) => void;
}

export function BottomNavigation({ currentScreen, onScreenChange }: BottomNavigationProps) {
  const navItems = [
    { id: 'home' as Screen, icon: Home, label: 'Home' },
    { id: 'profile' as Screen, icon: User, label: 'Profile' },
    { id: 'settings' as Screen, icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="bg-white border-t border-gray-200 px-4 py-2 safe-area-inset-bottom">
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentScreen === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onScreenChange(item.id)}
              className={`flex flex-col items-center py-2 px-4 rounded-lg transition-all duration-200 ${
                isActive 
                  ? 'text-blue-500' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon 
                size={20} 
                className={`transition-all duration-200 ${
                  isActive ? 'scale-110' : ''
                }`}
              />
              <span className="text-xs mt-1">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}