import { useState } from 'react';
import ChatHome from './imports/ChatHome';
import ChatNotification from './imports/ChatNotification';
import ChatSettings from './imports/ChatSettings';
import ChatChatPage from './imports/ChatChatPage';

type Screen = 'home' | 'notification' | 'settings' | 'chat';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('home');
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null);

  const handleChatSelect = (chatId: number) => {
    setSelectedChatId(chatId);
    setCurrentScreen('chat');
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return (
          <ChatHome 
            onNavigateToNotification={() => setCurrentScreen('notification')} 
            onNavigateToSettings={() => setCurrentScreen('settings')}
            onChatSelect={handleChatSelect}
          />
        );
      case 'notification':
        return <ChatNotification onNavigateBack={() => setCurrentScreen('home')} />;
      case 'settings':
        return <ChatSettings onNavigateBack={() => setCurrentScreen('home')} />;
      case 'chat':
        return <ChatChatPage onNavigateBack={() => setCurrentScreen('home')} />;
      default:
        return (
          <ChatHome 
            onNavigateToNotification={() => setCurrentScreen('notification')} 
            onNavigateToSettings={() => setCurrentScreen('settings')}
            onChatSelect={handleChatSelect}
          />
        );
    }
  };

  return (
    <div className="size-full">
      {renderScreen()}
    </div>
  );
}