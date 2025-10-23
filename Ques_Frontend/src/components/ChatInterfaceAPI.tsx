import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ErrorMessage } from './ui/error';
import { LoadingOverlay, InlineLoading } from './ui/loading';
import { useChatInterface } from '../hooks/useChatInterface';
import { Send, History, MessageCircle, Bell, School, Globe } from 'lucide-react';
import type { UserProfile } from '../App';
import type { FriendRequest } from '../types/api';
import ChatCards from './ChatCards';

interface ChatInterfaceAPIProps {
  userProfile: UserProfile;
  onShowHistory: () => void;
  onShowNotifications: () => void;
  onAddContact: (contact: any) => void;
  addedContactIds: Set<string>;
  quotedFromNotification: FriendRequest | null;
  onClearQuotedNotification: () => void;
  currentPlan?: 'basic' | 'pro';
  receivesLeft?: number;
  onTopUpReceives?: (amount: number) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
  singleCardInChat?: any;
  onClearSingleCard?: () => void;
}

export function ChatInterfaceAPI({
  userProfile,
  onShowHistory,
  onShowNotifications,
  onAddContact,
  addedContactIds,
  quotedFromNotification,
  onClearQuotedNotification,
  currentPlan = 'basic',
  receivesLeft = 3,
  onTopUpReceives,
  onGiftReceives,
  singleCardInChat,
  onClearSingleCard
}: ChatInterfaceAPIProps) {
  const [inputValue, setInputValue] = useState('');

  // 使用自定义hook管理聊天状态
  const {
    messages,
    isTyping,
    isLoading,
    error,
    searchMode,
    showCards,
    currentRecommendations,
    cardsTriggerIndex,
    quotedContacts,
    unreadNotifications,
    sendMessage,
    toggleSearchMode,
    handleCardWhisper,
    handleCardIgnore,
    handleCardStackClose,
    addQuotedContact,
    removeQuotedContact,
    clearQuotedContacts,
    showSingleCard,
    formatTime,
    getSuggestedQueries,
    clearError,
    messagesEndRef,
    cardsRef
  } = useChatInterface(userProfile, addedContactIds);

  // 处理引用的通知联系人
  React.useEffect(() => {
    if (quotedFromNotification) {
      addQuotedContact(quotedFromNotification);
      onClearQuotedNotification();
    }
  }, [quotedFromNotification, addQuotedContact, onClearQuotedNotification]);

  // 处理单张卡片显示
  React.useEffect(() => {
    if (singleCardInChat) {
      showSingleCard(singleCardInChat);
    }
  }, [singleCardInChat, showSingleCard]);

  // 发送消息处理
  const handleSendMessage = async () => {
    if (!inputValue.trim() && quotedContacts.length === 0) return;

    // 构建消息内容
    let messageContent = inputValue;
    if (quotedContacts.length > 0) {
      const quotedNames = quotedContacts.map(q => q.name).join(', ');
      messageContent = quotedContacts.length === 1
        ? `About ${quotedNames}: ${inputValue}`
        : `About ${quotedNames}: ${inputValue}`;
    }

    const quotedContactIds = quotedContacts.map(q => q.id);

    // 清理输入
    setInputValue('');
    clearQuotedContacts();

    // 发送消息
    await sendMessage(messageContent, quotedContactIds);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 卡片操作处理
  const handleCardAction = async (contact: any, action: 'whisper' | 'ignore') => {
    if (action === 'whisper') {
      const addedContact = await handleCardWhisper(contact);
      if (addedContact) {
        onAddContact(addedContact);
      }
    } else {
      handleCardIgnore(contact);
    }
  };

  const handleCardClose = () => {
    handleCardStackClose();
    if (onClearSingleCard) {
      onClearSingleCard();
    }
  };

  // 渲染消息前的部分
  const beforeCards = cardsTriggerIndex !== null ? messages.slice(0, cardsTriggerIndex + 1) : messages;
  const afterCards = cardsTriggerIndex !== null ? messages.slice(cardsTriggerIndex + 1) : [];

  return (
    <div className="h-full flex flex-col bg-white">
      {/* 加载覆盖层 */}
      <AnimatePresence>
        {isLoading && (
          <LoadingOverlay message="Processing your request..." />
        )}
      </AnimatePresence>

      {/* 错误显示 */}
      <AnimatePresence>
        {error && (
          <div className="absolute top-4 left-4 right-4 z-50">
            <ErrorMessage
              message={error}
              onClose={clearError}
              onRetry={() => {
                // 可以在这里重试最后一个操作
                clearError();
              }}
            />
          </div>
        )}
      </AnimatePresence>

      {/* 头部 - 仅在有消息时显示 */}
      {messages.length > 0 && (
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <MessageCircle size={16} className="text-white" />
            </div>
            <div>
              <h2 className="font-medium">Ques AI</h2>
              <p className="text-xs text-gray-500">Find your perfect connections</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleSearchMode}
              className="flex items-center justify-center w-8 h-8 rounded-full border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
            >
              {searchMode === 'inside' ? (
                <School size={14} />
              ) : (
                <Globe size={14} />
              )}
            </button>
            <button
              onClick={onShowNotifications}
              className="p-1 hover:bg-gray-100 rounded relative"
            >
              <Bell size={20} className="text-gray-500" />
              {unreadNotifications > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {unreadNotifications > 9 ? '9+' : unreadNotifications}
                </span>
              )}
            </button>
            <button onClick={onShowHistory} className="p-1 hover:bg-gray-100 rounded">
              <History size={20} className="text-gray-500" />
            </button>
          </div>
        </div>
      )}

      {/* 初始状态 - 无消息时的中心图标 */}
      {messages.length === 0 && (
        <>
          <div className="flex items-center justify-end p-4">
            <div className="flex items-center gap-2">
              <button
                onClick={toggleSearchMode}
                className="flex items-center justify-center w-8 h-8 rounded-full border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
              >
                {searchMode === 'inside' ? (
                  <School size={14} />
                ) : (
                  <Globe size={14} />
                )}
              </button>
              <button
                onClick={onShowNotifications}
                className="p-1 hover:bg-gray-100 rounded relative"
              >
                <Bell size={20} className="text-gray-500" />
                {unreadNotifications > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {unreadNotifications > 9 ? '9+' : unreadNotifications}
                  </span>
                )}
              </button>
              <button onClick={onShowHistory} className="p-1 hover:bg-gray-100 rounded">
                <History size={20} className="text-gray-500" />
              </button>
            </div>
          </div>

          <div className="flex-1 flex flex-col items-center justify-center px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <div className="w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <MessageCircle size={32} className="text-white" />
              </div>
              <h1 className="text-2xl mb-2 text-gray-800">Ques AI</h1>
              <p className="text-gray-500 mb-4">Your AI-powered networking agent</p>
            </motion.div>
          </div>
        </>
      )}

      {/* 消息和卡片区域 */}
      {(messages.length > 0 || showCards) && (
        <div className="flex-1 overflow-y-auto px-4 py-4">
          <div className="space-y-6">
            {/* 卡片前的消息 */}
            <div className="w-full space-y-4">
              <AnimatePresence>
                {beforeCards.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    layout
                    className="mb-4"
                  >
                    {message.type === 'user' ? (
                      <div className="flex justify-end mb-3">
                        <div className="bg-blue-500 text-white rounded-2xl rounded-tr-md px-4 py-2 max-w-xs">
                          <p>{message.content}</p>
                          <p className="text-xs opacity-75 mt-1">{formatTime(message.timestamp)}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-start mb-3">
                        <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-2 max-w-xs">
                          <p className="text-gray-800">{message.content}</p>
                          <p className="text-xs text-gray-500 mt-1">{formatTime(message.timestamp)}</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* 卡片显示区域 */}
            <AnimatePresence>
              {showCards && cardsTriggerIndex !== null && (
                <motion.div
                  ref={cardsRef}
                  layout
                  initial={{ opacity: 0, y: 50, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 50, scale: 0.95 }}
                  transition={{ duration: 0.4 }}
                  className="flex justify-center w-full my-6"
                >
                  <ChatCards
                    profiles={currentRecommendations}
                    onSwipeLeft={(contact) => handleCardAction(contact, 'ignore')}
                    onSwipeRight={(contact) => handleCardAction(contact, 'whisper')}
                    onAllCardsFinished={handleCardClose}
                    onGiftReceives={onGiftReceives}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* 卡片后的消息 */}
            <div className="w-full space-y-4">
              <AnimatePresence>
                {afterCards.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    layout
                    className="mb-4"
                  >
                    {message.type === 'user' ? (
                      <div className="flex justify-end mb-3">
                        <div className="bg-blue-500 text-white rounded-2xl rounded-tr-md px-4 py-2 max-w-xs">
                          <p>{message.content}</p>
                          <p className="text-xs opacity-75 mt-1">{formatTime(message.timestamp)}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-start mb-3">
                        <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-2 max-w-xs">
                          <p className="text-gray-800">{message.content}</p>
                          <p className="text-xs text-gray-500 mt-1">{formatTime(message.timestamp)}</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* 输入指示器 */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start mt-4"
              >
                <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-2">
                  <div className="flex space-x-1">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          <div ref={messagesEndRef} />
        </div>
      )}

      {/* 引用联系人显示 */}
      {quotedContacts.length > 0 && (
        <div className="px-4 py-2 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {quotedContacts.map(contact => (
              <div key={contact.id} className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm">
                <span>{contact.name}</span>
                <button
                  onClick={() => removeQuotedContact(contact.id)}
                  className="hover:bg-blue-200 rounded-full p-0.5"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 建议气泡 - 每次对话后都显示 */}
      <div className="px-4 pb-3 pt-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={getSuggestedQueries().join(',')}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="flex flex-wrap gap-2 justify-center"
          >
            {getSuggestedQueries().map((query, index) => (
              <button
                key={`${query}-${index}`}
                onClick={() => {
                  setInputValue(query);
                  setTimeout(() => handleSendMessage(), 100);
                }}
                className={`px-3 py-2 rounded-full text-sm transition-colors border ${
                  index % 4 === 0 ? 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200' :
                  index % 4 === 1 ? 'bg-green-50 hover:bg-green-100 text-green-700 border-green-200' :
                  index % 4 === 2 ? 'bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-200' :
                  'bg-orange-50 hover:bg-orange-100 text-orange-700 border-orange-200'
                }`}
              >
                {query}
              </button>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* 输入区域 */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me to find connections..."
              className="pr-12 rounded-full"
              disabled={isLoading || isTyping}
            />
            <Button
              onClick={handleSendMessage}
              disabled={(!inputValue.trim() && quotedContacts.length === 0) || isLoading || isTyping}
              size="sm"
              className="absolute right-1 top-1/2 transform -translate-y-1/2 rounded-full w-8 h-8 p-0"
            >
              {isLoading || isTyping ? (
                <InlineLoading size="sm" />
              ) : (
                <Send size={14} />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 