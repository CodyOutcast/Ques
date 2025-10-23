import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Send, History, Bell, School, Globe } from 'lucide-react';
import logoIcon from '../assets/icon.jpg';
import { useLanguage } from '../contexts/LanguageContext';
import type { UserProfile } from '../App';
import type { FriendRequest } from './NotificationPanel';
import type { UserRecommendation as ApiUserRecommendation } from '../types/api';
import ChatCards, { ChatCardsRef } from './ChatCards';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  thinking?: string; // 思考流内容
  isStreaming?: boolean; // 是否正在流式输出
}

// 使用api.ts中的UserRecommendation类型，并添加age属性（向后兼容）
type UserRecommendation = ApiUserRecommendation & {
  age?: string; // 向后兼容，从birthday计算得出
};

interface ConversationState {
  lastQuery: string;
  availableContacts: UserRecommendation[];
  shownContacts: UserRecommendation[];
  currentIndex: number;
}

interface QuotedContact {
  id: string;
  name: string;
}

interface ChatInterfaceProps {
  userProfile: UserProfile;
  onShowHistory: () => void;
  onShowNotifications: () => void;
  onRequestWhisper: (contact: UserRecommendation) => void;
  addedContactIds: Set<string>;
  unreadNotifications: number;
  quotedFromNotification: FriendRequest | null;
  onClearQuotedNotification: () => void;
  currentPlan?: 'basic' | 'pro';
  receivesLeft?: number;
  onTopUpReceives?: (amount: number) => void;
  onGiftReceives?: (recipientName: string, amount: number) => void;
  singleCardInChat?: any;
  onClearSingleCard?: () => void;
}

export interface ChatInterfaceRef {
  resetLastSwipe: () => void;
}

// 提示词池 - 包含25个精心设计的提示词
const SUGGESTION_POOL = [
  "Find me a Python co-founder",
  "Connect me with AI researchers",
  "Looking for startup mentors",
  "Need investors for tech startup",
  "Find design collaborators",
  "Connect with product managers",
  "Search for blockchain developers",
  "Find UX/UI designers",
  "Looking for marketing experts",
  "Connect with data scientists",
  "Find mobile app developers",
  "Search for business strategists",
  "Looking for technical writers",
  "Find DevOps engineers",
  "Connect with sales professionals",
  "Search for legal advisors",
  "Find community managers",
  "Looking for growth hackers",
  "Connect with content creators",
  "Find backend developers",
  "Search for frontend specialists",
  "Looking for machine learning engineers",
  "Connect with startup founders",
  "Find full-stack developers",
  "Search for venture capitalists"
];

// 从提示词池中随机选择N个不重复的提示词
const getRandomSuggestions = (count: number = 4): string[] => {
  const shuffled = [...SUGGESTION_POOL].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
};

// 辅助函数：从生日计算年龄
const calculateAge = (birthday: string): string => {
  const birthDate = new Date(birthday);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age.toString();
};

const MOCK_RECOMMENDATIONS: UserRecommendation[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    birthday: '1999-03-15',
    age: '24',
    gender: 'Female',
    avatar: '👩‍💻',
    location: 'Beijing, China',
    hobbies: ['Rock Climbing', 'Photography', 'Cooking'],
    languages: ['English', 'Mandarin', 'Python'],
    skills: ['Python', 'Machine Learning', 'TensorFlow', 'Deep Learning', 'PyTorch'],
    resources: ['GPU Cluster Access', 'Research Lab', 'Datasets', 'ML Infrastructure'],
    projects: [
      {
        title: 'ML Ethics Framework',
        role: 'Lead Developer',
        description: 'Open-source framework for evaluating bias in ML models',
        referenceLinks: ['https://github.com/sarahchen/ml-ethics']
      },
      {
        title: 'Startup Accelerator',
        role: 'Technical Mentor',
        description: 'Mentoring 20+ AI startups on technical architecture',
        referenceLinks: []
      }
    ],
    goals: ['Build ethical AI products', 'Start a tech company', 'Publish research papers'],
    demands: ['Co-founder with business experience', 'Funding connections', 'Industry mentorship'],
    institutions: [
      {
        name: 'Tsinghua University',
        role: 'PhD Student - Computer Science',
        description: 'Research focus on ethical AI and machine learning safety',
        verified: true
      }
    ],
    university: {
      name: 'Tsinghua University',
      verified: true
    },
    matchScore: 95,
    bio: 'AI researcher passionate about ethical machine learning and startup innovation. PhD in Computer Science with 5 years of industry experience at Google AI.',
    oneSentenceIntro: 'I build AI systems that solve real-world problems while keeping humans at the center.',
    whyMatch: 'Perfect co-founder match! 🚀 You both have strong Python skills and share a passion for AI innovation. Sarah has the ML expertise to complement your technical background, and she\'s actively seeking a co-founder for her next venture.',
    receivesLeft: 5,
  },
  {
    id: '2',
    name: 'Alex Kumar',
    birthday: '1994-07-22',
    age: '29',
    gender: 'Male',
    avatar: '👨‍💼',
    location: 'Shanghai, China',
    hobbies: ['Chess', 'Travel', 'Wine Tasting'],
    languages: ['English', 'Hindi', 'Mandarin'],
    skills: ['Product Management', 'Startup Scaling', 'Design Thinking', 'Growth Hacking', 'UX Strategy'],
    resources: ['VC Network', 'Mentor Network', 'Marketing Channels', 'International Connections'],
    projects: [
      {
        title: 'EdTech Platform',
        role: 'Co-founder & CEO',
        description: 'Built and scaled online learning platform to $10M ARR',
        referenceLinks: ['https://techcrunch.com/alex-kumar-edtech']
      },
      {
        title: 'SaaS Analytics Tool',
        role: 'Product Lead',
        description: 'Led product development for B2B analytics platform',
        referenceLinks: []
      }
    ],
    goals: ['Scale next startup to $100M', 'Expand to global markets', 'Build category-defining product'],
    demands: ['Technical co-founder', 'Engineering team', 'Series A funding'],
    institutions: [
      {
        name: 'Alibaba Group',
        role: 'Former Product Director',
        description: 'Led product strategy for cloud computing division',
        verified: true
      }
    ],
    university: {
      name: 'Shanghai Jiao Tong University',
      verified: true
    },
    matchScore: 88,
    bio: 'Serial entrepreneur with 3 successful exits, now mentoring and building. Former Product Director at Alibaba, expert in scaling 0-to-1 products.',
    oneSentenceIntro: 'I turn technical innovations into market-winning products that users love.',
    whyMatch: 'Excellent bidirectional match! 🤝 He brings the product management and startup scaling experience you need, while you offer the technical Python skills he\'s seeking for his next venture. Both actively looking for co-founders in the China market.',
    receivesLeft: 3,
  },
  {
    id: '3',
    name: 'Maria Rodriguez',
    birthday: '1997-11-08',
    age: '26',
    gender: 'Female',
    avatar: '👩‍🔬',
    location: 'Guangzhou, China',
    hobbies: ['Hiking', 'Reading', 'Volunteer Work'],
    languages: ['Spanish', 'English', 'Portuguese'],
    skills: ['Data Science', 'Python', 'Research', 'Statistical Analysis', 'R', 'SQL'],
    resources: ['Research Database Access', 'Academic Network', 'Grant Writing', 'Publication Channels'],
    projects: [
      {
        title: 'Bias Detection Framework',
        role: 'Research Lead',
        description: 'Academic research on detecting and mitigating AI bias',
        referenceLinks: ['https://arxiv.org/abs/maria-bias-detection']
      },
      {
        title: 'Healthcare Analytics Platform',
        role: 'Data Scientist',
        description: 'ML models for predicting patient outcomes',
        referenceLinks: []
      }
    ],
    goals: ['Commercialize research', 'Impact healthcare with AI', 'Build diverse tech team'],
    demands: ['Business development partner', 'Healthcare industry connections', 'Regulatory expertise'],
    institutions: [
      {
        name: 'Sun Yat-sen University',
        role: 'Postdoc Researcher',
        description: 'Research in AI ethics and fairness in machine learning',
        verified: true
      }
    ],
    university: {
      name: 'Sun Yat-sen University',
      verified: true
    },
    matchScore: 82,
    bio: 'Data scientist passionate about AI ethics and open source contributions. Published researcher with 20+ papers in top-tier journals.',
    oneSentenceIntro: 'I use data science to solve real-world problems with ethical AI solutions.',
    whyMatch: 'Strong mutual interest! 🤝 Your AI ethics values align perfectly with her research focus, while your technical skills complement her data science background. She\'s looking for collaborators who share her values-driven approach to AI development.',
    receivesLeft: 8,
  }
];

const AI_RESPONSES = [
  "I'll help you find the perfect connections! Can you tell me more about what kind of collaboration you're looking for?",
  "Great! Let me search for people who match your criteria. This might take a moment...",
  "Based on your profile and request, I found some excellent matches. Here are the top recommendations:",
  "Would you like me to refine these results or search for different criteria?"
];

export const ChatInterface = forwardRef<ChatInterfaceRef, ChatInterfaceProps>(({ 
  userProfile, 
  onShowHistory, 
  onShowNotifications, 
  onRequestWhisper, 
  addedContactIds, 
  unreadNotifications, 
  quotedFromNotification, 
  onClearQuotedNotification,
  currentPlan = 'basic',
  receivesLeft = 3,
  onTopUpReceives,
  onGiftReceives,
  singleCardInChat,
  onClearSingleCard
}, ref) => {
  const { t } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [currentThinking, setCurrentThinking] = useState('');
  const [searchInside, setSearchInside] = useState(true);
  const chatCardsRef = useRef<ChatCardsRef>(null);
  const [showCardStack, setShowCardStack] = useState(false);
  const [currentRecommendations, setCurrentRecommendations] = useState<UserRecommendation[]>([]);
  const [showCards, setShowCards] = useState(false);
  const [cardsTriggerIndex, setCardsTriggerIndex] = useState<number | null>(null);
  const [messagesBottomMargin, setMessagesBottomMargin] = useState(0);
  const [isAnimatingUp, setIsAnimatingUp] = useState(false);
  const [isAnimatingDown, setIsAnimatingDown] = useState(false);
  const [scrollToCards, setScrollToCards] = useState(false);
  const [conversationState, setConversationState] = useState({
    lastQuery: '',
    availableContacts: [] as UserRecommendation[],
    shownContacts: [] as UserRecommendation[],
    currentIndex: 0
  });
  const [quotedContacts, setQuotedContacts] = useState<QuotedContact[]>([]);
  const [currentSuggestions, setCurrentSuggestions] = useState<string[]>(() => getRandomSuggestions(4));

  // Add state to track if waiting for single card setup
  const [pendingSingleCard, setPendingSingleCard] = useState<any>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  // 暴露重置方法给父组件
  useImperativeHandle(ref, () => ({
    resetLastSwipe: () => {
      console.log('🔄 ChatInterface: Calling resetLastSwipe on ChatCards');
      chatCardsRef.current?.resetLastSwipe();
    }
  }), []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToCardsPosition = () => {
    if (cardsRef.current) {
      const cardsElement = cardsRef.current;
      const container = cardsElement.closest('.overflow-y-auto');
      if (container) {
        const containerRect = container.getBoundingClientRect();
        const cardsRect = cardsElement.getBoundingClientRect();
        const targetScroll = container.scrollTop + (cardsRect.top - containerRect.top) - (containerRect.height / 2) + (cardsRect.height / 2);
        
        container.scrollTo({
          top: targetScroll,
          behavior: 'smooth'
        });
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (scrollToCards) {
      scrollToCardsPosition();
      setScrollToCards(false);
    }
  }, [scrollToCards]);

  // Handle quoted contact from notifications
  useEffect(() => {
    if (quotedFromNotification) {
      const newQuote: QuotedContact = {
        id: quotedFromNotification.id,
        name: quotedFromNotification.name
      };
      
      // Add to quoted contacts if not already quoted
      if (!quotedContacts.find(q => q.id === quotedFromNotification.id)) {
        setQuotedContacts(prev => [...prev, newQuote]);
      }
      
      // Clear the notification quote
      onClearQuotedNotification();
    }
  }, [quotedFromNotification, quotedContacts, onClearQuotedNotification]);

  // Handle single card in chat - force setup
  useEffect(() => {
    if (singleCardInChat) {
      // Clear any existing cards first
      setShowCards(false);
      setCurrentRecommendations([]);
      setCardsTriggerIndex(null);
      setPendingSingleCard(null);
      
      // Small delay to ensure state is cleared
      setTimeout(() => {
        const aiMessage: Message = {
          id: Date.now().toString(),
          type: 'ai',
          content: "Here's the original profile card you requested to review:",
          timestamp: new Date(),
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setPendingSingleCard(singleCardInChat);
      }, 100);
    }
  }, [singleCardInChat]);

  // Set up single card after messages update
  useEffect(() => {
    if (pendingSingleCard && messages.length > 0) {
      const newIndex = messages.length - 1;
      
      setCurrentRecommendations([{
        ...pendingSingleCard,
        receivesLeft: pendingSingleCard.receivesLeft || 5, // default
      }]);
      setShowCards(true);
      setCardsTriggerIndex(newIndex);
      setPendingSingleCard(null);
      
      // Trigger scroll to center
      setTimeout(() => {
        setScrollToCards(true);
      }, 300);
    }
  }, [messages, pendingSingleCard]);

  const generateMutualMatchExplanation = (recommendation: UserRecommendation, userQuery: string) => {
    const userSkills = userProfile.skills.join(', ') || 'technical skills';
    const userLocation = userProfile.location || 'your location';
    const userGoals = userProfile.goals || 'your goals';
    
    // Create personalized mutual matching explanations
    if (userQuery.toLowerCase().includes('co-founder')) {
      return `Perfect mutual match! ✨ You offer the ${userSkills} they need for their next venture, while they bring ${recommendation.skills.slice(0, 2).join(' and ')} expertise you're seeking. Both actively looking for co-founders with complementary skills.`;
    } else if (userQuery.toLowerCase().includes('mentor')) {
      return `Excellent mentoring match! 🎯 They're looking to mentor someone with your ${userSkills} background, while you gain from their ${recommendation.skills[0]} expertise. Your ${userGoals.join(', ')} goals align with their mentoring focus.`;
    } else if (userQuery.toLowerCase().includes('investor')) {
      return `Strong investor-founder fit! 💰 Your ${userSkills} expertise matches their investment thesis, while their portfolio in ${recommendation.projects[0]} aligns with your sector. Mutual interest in ${userLocation} market.`;
    } else {
      return `Great bidirectional match! 🤝 You complement each other's skills (your ${userSkills} + their ${recommendation.skills[0]}), share similar goals, and they're also looking for someone with your background in ${userLocation}.`;
    }
  };

  const simulateAIResponse = async (userMessage: string) => {
    const userMessageLower = userMessage.toLowerCase();
    
    // 判断是否需要复杂搜索（有思考流）
    const needsComplexSearch = userMessageLower.includes('co-founder') || 
                               userMessageLower.includes('startup') ||
                               userMessageLower.includes('python') ||
                               userMessageLower.includes('ai') ||
                               userMessageLower.includes('mentor') ||
                               userMessageLower.includes('investor');

    // 创建AI消息占位符
    const aiMessageId = Date.now().toString();
    const aiMessage: Message = {
      id: aiMessageId,
      type: 'ai',
      content: '',
      thinking: '',
      timestamp: new Date(),
      isStreaming: true
    };

    // 获取当前消息索引（在添加AI消息之前）
    let currentMessageIndex = 0;
    
    // 添加消息到列表，并获取正确的索引
    setMessages(prev => {
      currentMessageIndex = prev.length; // AI消息将被添加到这个位置
      return [...prev, aiMessage];
    });

    // 使用chatService的模拟stream响应
    const { chatService } = await import('../services/chatService');
    
    await chatService.simulateStreamResponse(
      userMessage,
      {
        onThinkingChunk: (chunk, fullThinking) => {
          setIsThinking(true);
          setCurrentThinking(fullThinking);
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, thinking: fullThinking }
              : msg
          ));
        },
        onResultChunk: (chunk, fullResult) => {
          setIsThinking(false);
          setIsTyping(true);
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, content: fullResult }
              : msg
          ));
        },
        onRecommendations: (recommendations) => {
          const filteredRecs = recommendations
            .filter(rec => !addedContactIds.has(rec.id))
            .map(rec => ({
              ...rec,
              whyMatch: generateMutualMatchExplanation(rec, userMessage)
            }));

          if (filteredRecs.length > 0) {
            setConversationState({
              lastQuery: userMessage,
              availableContacts: filteredRecs,
              shownContacts: filteredRecs,
              currentIndex: 0
            });

            setTimeout(() => {
              setCurrentRecommendations(filteredRecs);
              setShowCards(true);
              setCardsTriggerIndex(currentMessageIndex);
              
              setTimeout(() => {
                setScrollToCards(true);
              }, 100);
            }, 500);
          }
        },
        onComplete: (response) => {
          setIsTyping(false);
          setIsThinking(false);
          setCurrentThinking('');
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, isStreaming: false }
              : msg
          ));
          
          // 刷新建议提示词
          setCurrentSuggestions(getRandomSuggestions(4));
        },
        onError: (error) => {
          console.error('Stream error:', error);
          setIsTyping(false);
          setIsThinking(false);
          setCurrentThinking('');
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId 
              ? { 
                  ...msg, 
                  content: 'Sorry, something went wrong. Please try again.',
                  isStreaming: false 
                }
              : msg
          ));
        }
      },
      searchInside ? 'inside' : 'global',
      userProfile
    );
  };

  const handleSendMessage = async () => {
    // 先保存当前输入值，避免状态更新导致的竞态条件
    const currentInput = inputValue.trim();
    const currentQuotedContacts = [...quotedContacts];
    
    if (!currentInput && currentQuotedContacts.length === 0) return;

    // 立即清空输入框和引用联系人，避免重复发送
    setInputValue('');
    setQuotedContacts([]);

    // Build the message content with quoted contacts context
    let messageContent = currentInput;
    if (currentQuotedContacts.length > 0) {
      const quotedNames = currentQuotedContacts.map(q => q.name).join(', ');
      messageContent = currentQuotedContacts.length === 1 
        ? `About ${quotedNames}: ${currentInput}`
        : `About ${quotedNames}: ${currentInput}`;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    // 添加用户消息
    setMessages(prev => [...prev, userMessage]);

    // 等待一小段时间确保状态更新完成
    await new Promise(resolve => setTimeout(resolve, 10));
    
    // 调用AI响应
    await simulateAIResponse(messageContent);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const removeQuotedContact = (contactId: string) => {
    setQuotedContacts(prev => prev.filter(q => q.id !== contactId));
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  // Handle card stack actions
  const handleCardWhisper = (contact: UserRecommendation) => {
    console.log('💬 ChatInterface handleCardWhisper:', contact.name);
    // 延迟弹窗，等待卡片飞出动画完成（300ms动画 + 50ms缓冲）
    setTimeout(() => {
      onRequestWhisper(contact);
    }, 200);
  };

  const handleCardIgnore = (contact: UserRecommendation) => {
    // Just ignore, no action needed
  };

  const handleCardStackClose = () => {
    setShowCards(false);
    setCurrentRecommendations([]);
    setCardsTriggerIndex(null);
    if (onClearSingleCard) {
      onClearSingleCard();
    }
  };

  const beforeCards = cardsTriggerIndex !== null ? messages.slice(0, cardsTriggerIndex + 1) : messages;
  const afterCards = cardsTriggerIndex !== null ? messages.slice(cardsTriggerIndex + 1) : [];

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header - only show when there are messages */}
      {messages.length > 0 && (
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center overflow-hidden">
              <img 
                src={logoIcon} 
                alt="Ques AI" 
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h2 className="font-medium">{t('chat.appName')}</h2>
              <p className="text-xs text-gray-500">{t('chat.headerSubtitle')}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setSearchInside(!searchInside)}
              className="flex items-center justify-center w-8 h-8 rounded-full border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
            >
              {searchInside ? (
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



      {/* Initial State - centered icon (only when no messages) */}
      {messages.length === 0 && (
        <>
          {/* Header for initial state */}
          <div className="flex items-center justify-end p-4">
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setSearchInside(!searchInside)}
                className="flex items-center justify-center w-8 h-8 rounded-full border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
              >
                {searchInside ? (
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
              <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg overflow-hidden">
                <img 
                  src={logoIcon} 
                  alt="Ques AI Logo" 
                  className="w-full h-full object-cover"
                />
              </div>
              <h1 className="text-2xl mb-2 text-gray-800">{t('chat.appName')}</h1>
              <p className="text-gray-500 mb-4">{t('chat.appTagline')}</p>
            </motion.div>
          </div>
        </>
      )}

      {/* Messages and Cards - show when there are messages or cards */}
      {(messages.length > 0 || showCards) && (
        <div className="flex-1 overflow-y-auto px-4 py-4">
          <div className="space-y-6">
            {/* Before Cards Messages */}
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
                          {/* 思考流显示 */}
                          {message.thinking && (
                            <div className="mb-2 pb-2 border-b border-gray-300">
                              <div className="flex items-center gap-2 mb-1">
                                {message.isStreaming && !message.content ? (
                                  // 思考中 - 显示动画
                                  <>
                                    <div className="flex items-center space-x-1">
                                      <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                                        className="w-2 h-2 bg-blue-500 rounded-full"
                                      />
                                      <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                                        className="w-2 h-2 bg-blue-500 rounded-full"
                                      />
                                      <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                                        className="w-2 h-2 bg-blue-500 rounded-full"
                                      />
                                    </div>
                                    <span className="text-xs text-blue-600 font-medium">思考中</span>
                                  </>
                                ) : (
                                  // 思考完成 - 显示勾选图标
                                  <>
                                    <svg className="w-3 h-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-xs text-green-600 font-medium">思考完成</span>
                                  </>
                                )}
                              </div>
                              <p className="text-xs text-gray-600 whitespace-pre-line">{message.thinking}</p>
                            </div>
                          )}
                          
                          {/* 结果内容 */}
                          {message.content && (
                            <p className="text-gray-800">{message.content}</p>
                          )}
                          
                          {!message.content && !message.thinking && message.isStreaming && (
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
                          )}
                          
                          <p className="text-xs text-gray-500 mt-1">{formatTime(message.timestamp)}</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* Cards Display Area - appears below last message, then scrolls into center */}
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
                    ref={chatCardsRef}
                    profiles={currentRecommendations}
                    onSwipeLeft={handleCardIgnore}
                    onSwipeRight={handleCardWhisper}
                    onAllCardsFinished={handleCardStackClose}
                    onGiftReceives={onGiftReceives}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* After Cards Messages */}
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
                        {/* 思考流显示 */}
                        {message.thinking && (
                            <div className="mb-2 pb-2 border-b border-gray-300">
                              <div className="flex items-center gap-2 mb-1">
                                {message.isStreaming && !message.content ? (
                                  // 思考中 - 显示动画
                                  <>
                                    <div className="flex items-center space-x-1">
                                      <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                                        className="w-2 h-2 bg-blue-500 rounded-full"
                                      />
                                      <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                                        className="w-2 h-2 bg-blue-500 rounded-full"
                                      />
                                      <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                                        className="w-2 h-2 bg-blue-500 rounded-full"
                                      />
                                    </div>
                                    <span className="text-xs text-blue-600 font-medium">思考中</span>
                                  </>
                                ) : (
                                  // 思考完成 - 显示勾选图标
                                  <>
                                    <svg className="w-3 h-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span className="text-xs text-green-600 font-medium">思考完成</span>
                                  </>
                                )}
                              </div>
                              <p className="text-xs text-gray-600 whitespace-pre-line">{message.thinking}</p>
                            </div>
                        )}
                        
                        {/* 结果内容 */}
                        {message.content && (
                          <p className="text-gray-800">{message.content}</p>
                        )}
                        
                        {!message.content && !message.thinking && message.isStreaming && (
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
                        )}
                        
                        <p className="text-xs text-gray-500 mt-1">{formatTime(message.timestamp)}</p>
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            </div>

            {/* Typing Indicator */}
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

      {/* Quoted Contacts Display */}
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

      {/* Suggestion Bubbles - show after every conversation */}
      <div className="px-4 pb-3 pt-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSuggestions.join(',')}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="flex flex-wrap gap-2 justify-center"
          >
            {currentSuggestions.map((suggestion, index) => (
              <button
                key={`${suggestion}-${index}`}
                onClick={async () => {
                  setInputValue(suggestion);
                  // 使用setTimeout确保状态更新完成
                  await new Promise(resolve => setTimeout(resolve, 50));
                  await handleSendMessage();
                }}
                className={`px-3 py-2 rounded-full text-sm transition-colors border ${
                  index % 4 === 0 ? 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200' :
                  index % 4 === 1 ? 'bg-green-50 hover:bg-green-100 text-green-700 border-green-200' :
                  index % 4 === 2 ? 'bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-200' :
                  'bg-orange-50 hover:bg-orange-100 text-orange-700 border-orange-200'
                }`}
              >
                {suggestion}
              </button>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
              <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('chat.typeMessage')}
              className="pr-12 rounded-full"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() && quotedContacts.length === 0}
              size="sm"
              className="absolute right-1 top-1/2 transform -translate-y-1/2 rounded-full w-8 h-8 p-0"
            >
              <Send size={14} />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
});

ChatInterface.displayName = 'ChatInterface';
