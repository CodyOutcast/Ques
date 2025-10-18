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
import ChatCards, { ChatCardsRef } from './ChatCards';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

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

interface UserRecommendation {
  id: string;
  name: string;
  age: string;
  gender: string;
  avatar: string;
  location: string;
  hobbies: string[];
  languages: string[];
  skills: string[];
  resources: string[];
  projects: { 
    title: string; 
    role: string; 
    description: string; 
    referenceLinks: string[] 
  }[];
  goals: string[];
  demands: string[];
  institutions: { 
    name: string; 
    role: string; 
    description: string; 
    verified: boolean;
  }[];
  university?: {
    name: string;
    verified: boolean;
  };
  matchScore: number;
  bio: string;
  oneSentenceIntro?: string;
  whyMatch: string; // Why we match message shown to the user (receiver's perspective)
  whisperDefaultMessage?: string; // AI-generated message from user's perspective for whisper
  receivesLeft?: number;
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

const MOCK_RECOMMENDATIONS: UserRecommendation[] = [
  {
    id: '1',
    name: 'Sarah Chen',
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
    whisperDefaultMessage: 'Hi Sarah! I noticed we both share a passion for ethical AI and have strong Python skills. I\'m really impressed by your ML Ethics Framework project. I believe my technical background could complement your ML expertise perfectly, and I\'d love to explore potential collaboration opportunities!',
    receivesLeft: 5,
  },
  {
    id: '2',
    name: 'Alex Kumar',
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
    whisperDefaultMessage: 'Hi Alex! Your experience scaling EdTech to $10M ARR is incredibly inspiring. I have strong technical Python skills and I\'m looking for someone with your product and scaling expertise. I think we could build something amazing together in the China market!',
    receivesLeft: 3,
  },
  {
    id: '3',
    name: 'Maria Rodriguez',
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
    whisperDefaultMessage: 'Hi Maria! I\'m deeply interested in AI ethics and your Bias Detection Framework research caught my attention. I share your values-driven approach to AI development and would love to discuss how we might collaborate on ethical AI solutions, especially in healthcare applications.',
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
    setIsTyping(true);
    
    // Simulate thinking time
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    let aiResponse = AI_RESPONSES[Math.floor(Math.random() * AI_RESPONSES.length)];
    let recommendations: UserRecommendation[] = [];
    let triggerIndex: number | null = null;

    const userMessageLower = userMessage.toLowerCase();

    if (userMessageLower.includes('co-founder') || 
        userMessageLower.includes('startup') ||
        userMessageLower.includes('python') ||
        userMessageLower.includes('ai')) {
      recommendations = MOCK_RECOMMENDATIONS
        .filter(rec => !addedContactIds.has(rec.id))
        .map(rec => ({
          ...rec,
          whyMatch: generateMutualMatchExplanation(rec, userMessage)
        }));
      
      if (recommendations.length > 0) {
        aiResponse = "I found some excellent matches for you! Let me show them in an interactive format...";
        triggerIndex = messages.length;
      } else {
        aiResponse = "I've already shown you all the best matches for this type of search. Would you like to try a different query?";
      }
    } else if (userMessageLower.includes('mentor')) {
      recommendations = MOCK_RECOMMENDATIONS
        .filter(r => !addedContactIds.has(r.id) && (r.name === 'Sarah Chen' || r.name === 'Alex Kumar'))
        .map(rec => ({
          ...rec,
          whyMatch: generateMutualMatchExplanation(rec, userMessage)
        }));
      
      if (recommendations.length > 0) {
        aiResponse = "I found some experienced mentors who are also seeking mentees with your profile! Let me show them...";
        triggerIndex = messages.length;
      } else {
        aiResponse = "I've already shown you all the available mentors. Would you like to try a different search?";
      }
    } else if (userMessageLower.includes('investor')) {
      recommendations = MOCK_RECOMMENDATIONS
        .filter(r => !addedContactIds.has(r.id) && r.name === 'Alex Kumar')
        .map(rec => ({
          ...rec,
          whyMatch: generateMutualMatchExplanation(rec, userMessage)
        }));
      
      if (recommendations.length > 0) {
        aiResponse = "Here are some investors actively seeking founders with profiles like yours! Opening the stack...";
        triggerIndex = messages.length;
      } else {
        aiResponse = "I've already shown you all the available investors. Would you like to try a different search?";
      }
    }

    setIsTyping(false);
    
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: aiResponse,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);

    if (triggerIndex !== null && recommendations.length > 0) {
      setConversationState({
        lastQuery: userMessage,
        availableContacts: recommendations,
        shownContacts: recommendations,
        currentIndex: 0
      });

      setTimeout(() => {
        // Show cards directly below last message
        setCurrentRecommendations(recommendations);
        setShowCards(true);
        setCardsTriggerIndex(triggerIndex);
        
        // Trigger scroll animation to center cards
        setTimeout(() => {
          setScrollToCards(true);
        }, 100);
      }, 1000);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() && quotedContacts.length === 0) return;

    // Build the message content with quoted contacts context
    let messageContent = inputValue;
    if (quotedContacts.length > 0) {
      const quotedNames = quotedContacts.map(q => q.name).join(', ');
      messageContent = quotedContacts.length === 1 
        ? `About ${quotedNames}: ${inputValue}`
        : `About ${quotedNames}: ${inputValue}`;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToProcess = messageContent;
    setInputValue('');
    setQuotedContacts([]);

    await simulateAIResponse(messageToProcess);
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
                          <p className="text-gray-800">{message.content}</p>
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
                        <p className="text-gray-800">{message.content}</p>
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

      {/* Suggestion Bubbles - only show in initial state */}
      {messages.length === 0 && (
        <div className="px-4 pb-3">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-wrap gap-2 justify-center"
          >
            <button
              onClick={() => {
                setInputValue("Find me a Python co-founder");
                handleSendMessage();
              }}
              className="bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded-full text-sm transition-colors border border-blue-200"
            >
              Python co-founder
            </button>
            <button
              onClick={() => setInputValue("Connect me with AI researchers")}
              className="bg-green-50 hover:bg-green-100 text-green-700 px-3 py-2 rounded-full text-sm transition-colors border border-green-200"
            >
              AI researchers
            </button>
            <button
              onClick={() => setInputValue("Find design mentors")}
              className="bg-purple-50 hover:bg-purple-100 text-purple-700 px-3 py-2 rounded-full text-sm transition-colors border border-purple-200"
            >
              Design mentors
            </button>
            <button
              onClick={() => setInputValue("Startup advisors needed")}
              className="bg-orange-50 hover:bg-orange-100 text-orange-700 px-3 py-2 rounded-full text-sm transition-colors border border-orange-200"
            >
              Startup advisors
            </button>
          </motion.div>
        </div>
      )}

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
