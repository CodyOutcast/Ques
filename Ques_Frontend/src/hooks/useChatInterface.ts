import { useState, useCallback, useRef, useEffect } from 'react';
import { chatService, recommendationService, contactService, notificationService, whisperService, cardTrackingService } from '../services';
import type { 
  ChatMessage,
  ChatResponse,
  UserRecommendation,
  ContactedUser,
  FriendRequest
} from '../types/api';
import type { UserProfile } from '../App';

// 消息状态
interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

// 会话状态
interface ConversationState {
  lastQuery: string;
  availableContacts: UserRecommendation[];
  shownContacts: UserRecommendation[];
  currentIndex: number;
}

// 引用联系人
interface QuotedContact {
  id: string;
  name: string;
}

// Hook状态
interface ChatInterfaceState {
  messages: Message[];
  isTyping: boolean;
  isLoading: boolean;
  error: string | null;
  searchMode: 'inside' | 'global';
  showCards: boolean;
  currentRecommendations: UserRecommendation[];
  cardsTriggerIndex: number | null;
  conversationState: ConversationState;
  quotedContacts: QuotedContact[];
  sessionId: string | null;
  unreadNotifications: number;
  singleCardInChat: any;
}

export function useChatInterface(
  userProfile: UserProfile,
  addedContactIds: Set<string>
) {
  const [state, setState] = useState<ChatInterfaceState>({
    messages: [],
    isTyping: false,
    isLoading: false,
    error: null,
    searchMode: 'inside',
    showCards: false,
    currentRecommendations: [],
    cardsTriggerIndex: null,
    conversationState: {
      lastQuery: '',
      availableContacts: [],
      shownContacts: [],
      currentIndex: 0
    },
    quotedContacts: [],
    sessionId: null,
    unreadNotifications: 0,
    singleCardInChat: null
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  // 更新状态的辅助函数
  const updateState = useCallback((updates: Partial<ChatInterfaceState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  // 设置错误
  const setError = useCallback((error: string | null) => {
    updateState({ error, isLoading: false, isTyping: false });
  }, [updateState]);

  // 清除错误
  const clearError = useCallback(() => {
    updateState({ error: null });
  }, [updateState]);

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // 滚动到卡片位置
  const scrollToCardsPosition = useCallback(() => {
    if (cardsRef.current) {
      const cardsElement = cardsRef.current;
      const container = cardsElement.closest('.overflow-y-auto');
      if (container) {
        const containerRect = container.getBoundingClientRect();
        const cardsRect = cardsElement.getBoundingClientRect();
        const targetScroll = container.scrollTop + (cardsRect.top - containerRect.top) - 
          (containerRect.height / 2) + (cardsRect.height / 2);
        
        container.scrollTo({
          top: targetScroll,
          behavior: 'smooth'
        });
      }
    }
  }, []);

  // 创建会话
  const createSession = useCallback(async () => {
    try {
      const response = await chatService.createSession();
      if (response.success && response.data) {
        updateState({ sessionId: response.data.id });
        return response.data.id;
      }
      return null;
    } catch (error) {
      console.error('Failed to create session:', error);
      return null;
    }
  }, [updateState]);

  // 发送消息
  const sendMessage = useCallback(async (messageContent: string, quotedContactIds?: string[]) => {
    try {
      updateState({ isLoading: true, error: null });

      // 创建会话（如果还没有）
      let sessionId = state.sessionId;
      if (!sessionId) {
        sessionId = await createSession();
        if (!sessionId) {
          throw new Error('Failed to create chat session');
        }
      }

      // 添加用户消息到界面
      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: messageContent,
        timestamp: new Date(),
      };

      updateState({ 
        messages: [...state.messages, userMessage],
        isLoading: false,
        isTyping: true
      });

      // 调用聊天API或使用模拟响应
      let chatResponse: ChatResponse;
      
      if ((import.meta as any).env?.MODE === 'development') {
        // 开发环境使用模拟响应
        chatResponse = await chatService.simulateAIResponse(
          messageContent, 
          state.searchMode, 
          userProfile
        );
      } else {
        // 生产环境调用真实API
        const response = await chatService.sendMessage({
          message: messageContent,
          sessionId,
          searchMode: state.searchMode,
          quotedContacts: quotedContactIds
        });
        
        if (!response.success || !response.data) {
          throw new Error(response.error || 'Failed to send message');
        }
        
        chatResponse = response.data;
      }

      // 添加AI回复到界面
      const aiMessage: Message = {
        id: chatResponse.message.id,
        type: 'ai',
        content: chatResponse.message.content,
        timestamp: new Date(chatResponse.message.timestamp),
      };

      const triggerIndex = chatResponse.recommendations && chatResponse.recommendations.length > 0 
        ? state.messages.length + 1 
        : null;

      updateState({
        messages: [...state.messages, userMessage, aiMessage],
        isTyping: false,
        sessionId: chatResponse.sessionId,
        conversationState: {
          lastQuery: messageContent,
          availableContacts: chatResponse.recommendations || [],
          shownContacts: chatResponse.recommendations || [],
          currentIndex: 0
        }
      });

      // 如果有推荐，显示卡片
      if (chatResponse.recommendations && chatResponse.recommendations.length > 0) {
        // 过滤掉已添加的联系人
        const filteredRecommendations = chatResponse.recommendations.filter(
          rec => !addedContactIds.has(rec.id)
        );

        if (filteredRecommendations.length > 0) {
          setTimeout(() => {
            updateState({
              currentRecommendations: filteredRecommendations,
              showCards: true,
              cardsTriggerIndex: triggerIndex,
            });
            
            // 更新最新卡片到后端（如果有卡片）
            if (filteredRecommendations.length > 0) {
              const latestCard = filteredRecommendations[0]; // 第一张卡片是最新的
              cardTrackingService.quickUpdateCard(latestCard, {
                sessionId: chatResponse.sessionId,
                searchQuery: messageContent,
                searchMode: state.searchMode,
                cardPosition: 0
              }).catch(error => {
                console.error('Failed to update latest card:', error);
                // 不阻塞主流程，只记录错误
              });
            }
            
            // 延迟滚动到卡片位置
            setTimeout(() => {
              scrollToCardsPosition();
            }, 300);
          }, 1000);
        }
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
    }
  }, [
    state.sessionId, 
    state.messages, 
    state.searchMode, 
    userProfile, 
    addedContactIds, 
    createSession, 
    updateState, 
    setError, 
    scrollToCardsPosition
  ]);

  // 切换搜索模式
  const toggleSearchMode = useCallback(() => {
    updateState({ 
      searchMode: state.searchMode === 'inside' ? 'global' : 'inside' 
    });
  }, [state.searchMode, updateState]);

  // 添加联系人
  const addContact = useCallback(async (recommendation: UserRecommendation) => {
    try {
      updateState({ isLoading: true, error: null });

      const contactRequest = {
        contactId: recommendation.id,
        notes: `Added from chat recommendation: ${recommendation.whyMatch}`,
        tags: ['Chat Recommendation']
      };

      const response = await contactService.addContact(contactRequest);

      if (response.success) {
        updateState({ isLoading: false });
        return contactService.convertRecommendationToContact(recommendation);
      } else {
        throw new Error(response.error || 'Failed to add contact');
      }
    } catch (error) {
      console.error('Failed to add contact:', error);
      setError(error instanceof Error ? error.message : 'Failed to add contact');
      return null;
    }
  }, [updateState, setError]);

  // 处理卡片操作 - 发送whisper消息
  const handleCardWhisper = useCallback(async (contact: UserRecommendation) => {
    try {
      updateState({ isLoading: true, error: null });

      // 获取用户微信ID，从localStorage或设置中获取，如果没有则生成默认值
      const getUserWechatId = () => {
        const savedWechatId = localStorage.getItem('user_wechat_id');
        if (savedWechatId && savedWechatId !== 'your_wechat_id') {
          return savedWechatId;
        }
        return userProfile.wechatId || `wechat_${userProfile.name?.replace(/\s+/g, '_').toLowerCase()}_${Date.now()}`;
      };

      // 构建完整的用户档案，确保包含微信ID
      const completeUserProfile = {
        ...userProfile,
        wechatId: getUserWechatId(),
        bio: userProfile.bio || userProfile.oneSentenceIntro || `${userProfile.name} is looking to connect and collaborate.`,
        id: userProfile.name?.replace(/\s+/g, '_').toLowerCase() + '_' + Date.now()
      };

      // 构建whisper请求
      const whisperRequest = whisperService.buildWhisperRequest(
        contact.id,
        completeUserProfile,
        {
          searchQuery: state.conversationState?.lastQuery,
          searchMode: state.searchMode,
          matchExplanation: contact.whyMatch,
          giftReceives: 0
        },
        // 可以添加自定义消息，这里使用默认消息
        undefined
      );

      // 验证whisper请求
      const validation = whisperService.validateWhisperRequest(whisperRequest);
      if (!validation.isValid) {
        throw new Error(`Whisper validation failed: ${validation.errors.join(', ')}`);
      }

      // 发送whisper消息
      const response = await whisperService.sendWhisper(whisperRequest);

      if (response.success) {
        // 发送成功后，同时添加到联系人历史（为了UI显示）
         const addedContact = await addContact(contact);
         
         // 从当前推荐中移除已发送whisper的联系人
         const remainingRecommendations = state.currentRecommendations.filter(rec => rec.id !== contact.id);
         
         updateState({
           currentRecommendations: remainingRecommendations,
           isLoading: false
         });

         // 如果还有卡片，更新最新卡片为下一张
         if (remainingRecommendations.length > 0) {
           const nextCard = remainingRecommendations[0];
           cardTrackingService.quickUpdateCard(nextCard, {
             sessionId: state.sessionId || undefined,
             searchQuery: state.conversationState.lastQuery,
             searchMode: state.searchMode,
             cardPosition: 0
           }).catch(error => {
             console.error('Failed to update next card after whisper:', error);
           });
         } else {
           // 没有卡片了，清除最新卡片
           cardTrackingService.clearLatestCard().catch(error => {
             console.error('Failed to clear latest card after whisper:', error);
           });
         }

         console.log('Whisper sent successfully:', response.data);
         
         // 显示成功提示
         // 注意：这里可以使用 toast 库，但目前使用 console.log 或 alert
         // 在生产环境中建议集成 toast 通知系统
         console.info(`✅ Whisper sent successfully to ${contact.name}!`);
         
         return addedContact;
       } else {
         throw new Error(response.error || 'Failed to send whisper');
       }
     } catch (error) {
       console.error('Failed to send whisper:', error);
       
       // 显示错误提示
       const errorMessage = error instanceof Error ? error.message : 'Failed to send whisper message';
       console.error(`❌ ${errorMessage}`);
       
       setError(`Unable to send whisper to ${contact.name}: ${errorMessage}`);
       updateState({ isLoading: false });
       return null;
     }
  }, [userProfile, state.conversationState, state.searchMode, state.currentRecommendations, addContact, updateState, setError]);

  const handleCardIgnore = useCallback((contact: UserRecommendation) => {
    // 从当前推荐中移除被忽略的联系人
    const remainingRecommendations = state.currentRecommendations.filter(rec => rec.id !== contact.id);
    
    updateState({
      currentRecommendations: remainingRecommendations
    });
    
    // 如果还有卡片，更新最新卡片为下一张
    if (remainingRecommendations.length > 0) {
      const nextCard = remainingRecommendations[0];
      cardTrackingService.quickUpdateCard(nextCard, {
        sessionId: state.sessionId || undefined,
        searchQuery: state.conversationState.lastQuery,
        searchMode: state.searchMode,
        cardPosition: 0
      }).catch(error => {
        console.error('Failed to update next card:', error);
      });
    } else {
      // 没有卡片了，清除最新卡片
      cardTrackingService.clearLatestCard().catch(error => {
        console.error('Failed to clear latest card:', error);
      });
    }
  }, [state.currentRecommendations, state.sessionId, state.conversationState, state.searchMode, updateState]);

  const handleCardStackClose = useCallback(() => {
    updateState({
      showCards: false,
      currentRecommendations: [],
      cardsTriggerIndex: null,
      singleCardInChat: null
    });
    
    // 清除最新卡片
    cardTrackingService.clearLatestCard().catch(error => {
      console.error('Failed to clear latest card:', error);
    });
  }, [updateState]);

  // 添加引用联系人
  const addQuotedContact = useCallback((contact: FriendRequest) => {
    const newQuote: QuotedContact = {
      id: contact.id,
      name: contact.name
    };

    if (!state.quotedContacts.find(q => q.id === contact.id)) {
      updateState({
        quotedContacts: [...state.quotedContacts, newQuote]
      });
    }
  }, [state.quotedContacts, updateState]);

  const removeQuotedContact = useCallback((contactId: string) => {
    updateState({
      quotedContacts: state.quotedContacts.filter(q => q.id !== contactId)
    });
  }, [state.quotedContacts, updateState]);

  const clearQuotedContacts = useCallback(() => {
    updateState({ quotedContacts: [] });
  }, [updateState]);

  // 显示单张卡片
  const showSingleCard = useCallback((card: any) => {
    // 清除现有卡片
    updateState({
      showCards: false,
      currentRecommendations: [],
      cardsTriggerIndex: null,
      singleCardInChat: null
    });

    // 添加AI消息
    const aiMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: "Here's the original profile card you requested to review:",
      timestamp: new Date(),
    };

    setTimeout(() => {
      const newMessages = [...state.messages, aiMessage];
      const triggerIndex = newMessages.length - 1;

      updateState({
        messages: newMessages,
        currentRecommendations: [{
          ...card,
          receivesLeft: card.receivesLeft || 5,
        }],
        showCards: true,
        cardsTriggerIndex: triggerIndex,
        singleCardInChat: card
      });

      // 更新最新卡片到后端
      cardTrackingService.quickUpdateCard(card, {
        sessionId: state.sessionId || undefined,
        searchQuery: 'Single Card View',
        searchMode: state.searchMode,
        cardPosition: 0
      }).catch(error => {
        console.error('Failed to update single card:', error);
      });

      // 滚动到卡片
      setTimeout(() => {
        scrollToCardsPosition();
      }, 300);
    }, 100);
  }, [state.messages, state.sessionId, state.searchMode, updateState, scrollToCardsPosition]);

  // 获取未读通知数量
  const updateUnreadNotifications = useCallback(async () => {
    try {
      const response = await notificationService.getUnreadCount();
      if (response.success && response.data) {
        updateState({ unreadNotifications: response.data.total });
      }
    } catch (error) {
      console.error('Failed to get unread notifications:', error);
    }
  }, [updateState]);

  // 格式化时间
  const formatTime = useCallback((date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  }, []);

  // 获取建议查询
  const getSuggestedQueries = useCallback(() => {
    return [
      "Find me a Python co-founder",
      "Connect me with AI researchers",
      "Looking for startup mentors", 
      "Need investors for tech startup",
      "Find design collaborators",
      "Connect with product managers"
    ];
  }, []);

  // 初始化时获取未读通知
  useEffect(() => {
    updateUnreadNotifications();
  }, [updateUnreadNotifications]);

  // 消息变化时滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [state.messages, scrollToBottom]);

  return {
    // 状态
    messages: state.messages,
    isTyping: state.isTyping,
    isLoading: state.isLoading,
    error: state.error,
    searchMode: state.searchMode,
    showCards: state.showCards,
    currentRecommendations: state.currentRecommendations,
    cardsTriggerIndex: state.cardsTriggerIndex,
    conversationState: state.conversationState,
    quotedContacts: state.quotedContacts,
    sessionId: state.sessionId,
    unreadNotifications: state.unreadNotifications,
    singleCardInChat: state.singleCardInChat,

    // 操作方法
    sendMessage,
    toggleSearchMode,
    addContact,
    handleCardWhisper,
    handleCardIgnore,
    handleCardStackClose,
    addQuotedContact,
    removeQuotedContact,
    clearQuotedContacts,
    showSingleCard,
    updateUnreadNotifications,

    // 工具方法
    formatTime,
    getSuggestedQueries,
    clearError,
    scrollToBottom,
    scrollToCardsPosition,

    // Refs
    messagesEndRef,
    cardsRef,
  };
} 