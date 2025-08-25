import { useState } from 'react';
import EnhancedChatHome from './components/EnhancedChatHome';
import ChatDetailPage from './components/ChatDetailPage';
import NotificationPage from './components/NotificationPage';
import NotificationSettingsPage from './components/NotificationSettingsPage';

interface ChatData {
  id: number;
  name: string;
  lastMessage: string;
  time: string;
  unreadCount: number;
  avatar: string;
  isOnline: boolean;
  isWaitingReply?: boolean;
}

type ViewType = 'home' | 'chat' | 'notifications' | 'notification-settings';

export default function App() {
  const [currentView, setCurrentView] = useState<ViewType>('home');
  const [selectedChat, setSelectedChat] = useState<ChatData | null>(null);

  const handleChatSelect = (chat: ChatData) => {
    setSelectedChat(chat);
    setCurrentView('chat');
  };

  const handleBackToHome = () => {
    setCurrentView('home');
  };

  const handleNotificationClick = () => {
    setCurrentView('notifications');
  };

  const handleNotificationSettingsClick = () => {
    setCurrentView('notification-settings');
  };

  const handleBackToNotifications = () => {
    setCurrentView('notifications');
  };

  return (
    <div className="size-full">
      {currentView === 'home' && (
        <EnhancedChatHome 
          onChatSelect={handleChatSelect} 
          onNotificationClick={handleNotificationClick}
        />
      )}
      
      {currentView === 'chat' && selectedChat && (
        <ChatDetailPage 
          chatId={selectedChat.id.toString()}
          chatName={selectedChat.name}
          chatAvatar={selectedChat.avatar}
          isOnline={selectedChat.isOnline}
          onBack={handleBackToHome}
        />
      )}
      
      {currentView === 'notifications' && (
        <NotificationPage 
          onBack={handleBackToHome}
          onSettingsClick={handleNotificationSettingsClick}
        />
      )}
      
      {currentView === 'notification-settings' && (
        <NotificationSettingsPage 
          onBack={handleBackToNotifications}
        />
      )}
    </div>
  );
}