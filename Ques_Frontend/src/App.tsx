import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WelcomeScreen } from './components/WelcomeScreen';
import { ProfileSetupWizard } from './components/ProfileSetupWizard';
import { ChatInterface } from './components/ChatInterface';
import { ProfileView } from './components/ProfileView';
import { SettingsScreen } from './components/SettingsScreen';
import { BottomNavigation } from './components/BottomNavigation';
import { ContactHistory, type ContactedUser } from './components/ContactHistory';
import { NotificationPanel, type FriendRequest } from './components/NotificationPanel';
import { SwipeableCardStack } from './components/SwipeableCardStack';
import { LanguageProvider } from './contexts/LanguageContext';

export type Screen = 'welcome' | 'profile-setup' | 'home' | 'profile' | 'settings';

export interface UserProfile {
  // Demographic info
  profilePhoto?: string;
  name: string;
  age: string;
  gender: string;
  location: string;
  hobbies: string[];
  languages: string[];
  oneSentenceIntro?: string;
  
  // Skills & Resources
  skills: string[];
  resources: string[];
  
  // Projects
  projects: { 
    title: string; 
    role: string; 
    description: string; 
    referenceLinks: string[] 
  }[];
  
  // Goals & Demands
  goals: string[];
  demands: string[];
  
  // Institutions
  institutions: { 
    name: string; 
    role: string; 
    description: string; 
    email?: string;
    verified: boolean;
  }[];
  
  // University
  university?: {
    name: string;
    verified: boolean;
  };
  
  // Contact & Social
  wechatId?: string;
  
  // Legacy fields for backward compatibility
  bio?: string;
  expertise?: { skill: string; level: string; years: string }[];
  interests?: string[];
  education?: string;
  experience?: string;
  availability?: string;
  preferences?: string[];
  values?: string[];
}

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('welcome');
  const [userProfile, setUserProfile] = useState<UserProfile>({
    // Demographic info
    name: '',
    age: '',
    gender: '',
    location: '',
    hobbies: [],
    languages: [],
    oneSentenceIntro: '',
    
    // Skills & Resources
    skills: [],
    resources: [],
    
    // Projects
    projects: [],
    
    // Goals & Demands
    goals: [],
    demands: [],
    
    // Institutions
    institutions: [],
    

  });
  const [isProfileComplete, setIsProfileComplete] = useState(false);
  const [contactHistory, setContactHistory] = useState<ContactedUser[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [addedContactIds, setAddedContactIds] = useState<Set<string>>(new Set());
  const [friendRequests, setFriendRequests] = useState<FriendRequest[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(2); // Mock initial count
  const [quotedFromNotification, setQuotedFromNotification] = useState<FriendRequest | null>(null);
  const [showOriginalCard, setShowOriginalCard] = useState<any>(null);
  const [currentPlan, setCurrentPlan] = useState<'basic' | 'pro'>('basic');
  const [receivesLeft, setReceivesLeft] = useState(3); // Remaining receives for the month
  const [showGiftModal, setShowGiftModal] = useState(false);
  const [singleCardInChat, setSingleCardInChat] = useState<any>(null);

  const handleScreenChange = (screen: Screen) => {
    setCurrentScreen(screen);
  };

  const handleProfileComplete = (profile: UserProfile) => {
    setUserProfile(profile);
    setIsProfileComplete(true);
    setCurrentScreen('home');
  };

  const handleProfileUpdate = (profile: UserProfile) => {
    setUserProfile(profile);
  };

  const handleAddContact = (recommendation: any) => {
    const newContact: ContactedUser = {
      id: recommendation.id,
      name: recommendation.name,
      age: recommendation.age,
      gender: recommendation.gender,
      avatar: recommendation.avatar,
      location: recommendation.location,
      hobbies: recommendation.hobbies || [],
      languages: recommendation.languages || [],
      skills: recommendation.skills,
      resources: recommendation.resources || [],
      projects: recommendation.projects || [],
      goals: recommendation.goals || [],
      demands: recommendation.demands || [],
      institutions: recommendation.institutions || [],
      university: recommendation.university,
      matchScore: recommendation.matchScore,
      bio: recommendation.bio,
      oneSentenceIntro: recommendation.oneSentenceIntro,
      whyMatch: recommendation.whyMatch,
      receivesLeft: recommendation.receivesLeft,
      contactedAt: new Date(),
      reported: false,
    };
    
    // Add to contact history
    setContactHistory(prev => [newContact, ...prev]);
    
    // Track this contact as added to prevent it from appearing again
    setAddedContactIds(prev => new Set(prev).add(recommendation.id));
  };

  const handleReportContact = (contactId: string, reason: string, attachments?: any[]) => {
    setContactHistory(prev => 
      prev.map(contact => 
        contact.id === contactId 
          ? { ...contact, reported: true, reportReason: reason, reportAttachments: attachments }
          : contact
      )
    );
  };

  const handleQuoteFromHistory = (contact: ContactedUser) => {
    // Close the history panel and switch to home to show the chat
    setShowHistory(false);
    setCurrentScreen('home');
    
    // Convert ContactedUser to FriendRequest-like format for ChatInterface
    const quotedRequest = {
      id: contact.id,
      name: contact.name,
      age: '25', // Default age since ContactedUser doesn't have this
      gender: 'Unknown', // Default gender since ContactedUser doesn't have this
      avatar: contact.avatar,
      location: contact.location,
      hobbies: [], // Default empty array
      languages: [], // Default empty array
      skills: contact.skills,
      resources: [], // Default empty array
      projects: contact.projects.map((p: any) => ({ 
        title: p.title || p, 
        role: 'Collaborator', 
        description: '', 
        referenceLinks: [] 
      })),
      goals: [], // Default empty array
      demands: [], // Default empty array
      institutions: [], // Default empty array
      university: undefined, // Default undefined
      matchScore: contact.matchScore,
      bio: contact.bio,
      oneSentenceIntro: contact.bio?.substring(0, 100) + '...', // Short intro from bio
      receivesLeft: 5, // Default value
      requestedAt: contact.contactedAt,
      mutualInterest: 'Previous conversation partner',
      wechatId: 'existing_contact'
    };
    
    setQuotedFromNotification(quotedRequest);
  };

  const handleRemoveFromHistory = (contactId: string) => {
    setContactHistory(prev => prev.filter(contact => contact.id !== contactId));
  };

  const handleShowNotifications = () => {
    setShowNotifications(true);
    setUnreadNotifications(0); // Mark as read when opened
  };

  const handleQuoteFromNotification = (request: FriendRequest) => {
    // Close the notifications panel and switch to home to show the chat
    setShowNotifications(false);
    setCurrentScreen('home');
    
    // Set the quoted contact to be picked up by ChatInterface
    setQuotedFromNotification(request);
  };

  const handleRemoveRequest = (requestId: string) => {
    setFriendRequests(prev => prev.filter(request => request.id !== requestId));
  };

  const handleAddWhisperToHistory = (request: FriendRequest) => {
    const newContact: ContactedUser = {
      id: request.id,
      name: request.name,
      age: request.age,
      gender: request.gender,
      avatar: request.avatar,
      location: request.location,
      hobbies: request.hobbies,
      languages: request.languages,
      skills: request.skills,
      resources: request.resources,
      projects: request.projects,
      goals: request.goals,
      demands: request.demands,
      institutions: request.institutions,
      university: request.university,
      matchScore: request.matchScore,
      bio: request.bio,
      oneSentenceIntro: request.oneSentenceIntro,
      whyMatch: request.mutualInterest, // 将mutualInterest映射为whyMatch
      receivesLeft: request.receivesLeft,
      contactedAt: new Date(),
      reported: false,
    };
    
    // Add to contact history
    setContactHistory(prev => [newContact, ...prev]);
    
    // Track this contact as added to prevent it from appearing again
    setAddedContactIds(prev => new Set(prev).add(request.id));
  };

  const handleViewOriginalCard = (contact: FriendRequest | ContactedUser) => {
    // Convert to the format expected by ChatCards
    const cardData: any = {
      id: contact.id,
      name: contact.name,
      age: contact.age || '25', // 默认年龄
      gender: contact.gender || 'Unknown', // 默认性别
      avatar: contact.avatar,
      location: contact.location,
      hobbies: contact.hobbies || [],
      languages: contact.languages || [],
      skills: contact.skills,
      resources: contact.resources || [],
      projects: 'projects' in contact 
        ? contact.projects
        : [],
      goals: contact.goals || [],
      demands: contact.demands || [],
      institutions: contact.institutions || [],
      university: contact.university,
      matchScore: contact.matchScore,
      bio: contact.bio,
      oneSentenceIntro: contact.oneSentenceIntro || contact.bio?.substring(0, 100) + '...', // Short intro from bio
      whyMatch: 'whyMatch' in contact ? contact.whyMatch : ('mutualInterest' in contact ? contact.mutualInterest : 'This is the original profile card you requested to review.'),
      receivesLeft: contact.receivesLeft || 5, // 默认值
    };
    
    // Switch to home screen and show in chat
    setCurrentScreen('home');
    setSingleCardInChat(cardData);
  };

  const handleCloseOriginalCard = () => {
    setShowOriginalCard(null);
  };

  const handleTopUpReceives = (amount: number) => {
    setReceivesLeft(prev => Math.min(prev + amount, 50)); // Cap at 50 for basic plan
  };

  const handleGiftReceives = (recipientName: string, amount: number) => {
    // In a real app, this would call an API to gift receives
    console.log(`Gifting ${amount} receives to ${recipientName}`);
    setShowGiftModal(false);
  };

  const handlePlanChange = (plan: 'basic' | 'pro') => {
    setCurrentPlan(plan);
    if (plan === 'pro') {
      setReceivesLeft(999); // Unlimited for pro
    } else {
      setReceivesLeft(Math.min(receivesLeft, 50)); // Cap at 50 for basic plan
    }
  };

  useEffect(() => {
    // Check if profile setup is complete
    if (isProfileComplete && currentScreen === 'profile-setup') {
      setCurrentScreen('home');
    }
  }, [isProfileComplete, currentScreen]);

  // Mock friend requests data - only initialize once
  useEffect(() => {
    if (isProfileComplete && friendRequests.length === 0) {
      const mockRequests: FriendRequest[] = [
        {
          id: 'req_1',
          name: 'Emma Zhang',
          age: '26',
          gender: 'Female',
          avatar: '👩‍💼',
          location: 'Shanghai, China',
          hobbies: ['Design', 'Photography', 'Coffee'],
          languages: ['English', 'Mandarin', 'Japanese'],
          skills: ['Product Design', 'UX Research', 'Figma', 'Sketch', 'User Testing'],
          resources: ['Design Team', 'Research Lab', 'Prototyping Tools', 'User Testing Platform'],
          projects: [
            {
              title: 'Mobile Banking App',
              role: 'Lead Designer',
              description: 'Redesigned mobile banking experience for 2M+ users',
              referenceLinks: ['https://dribbble.com/emma-banking-redesign']
            },
            {
              title: 'Design System Framework',
              role: 'Creator',
              description: 'Built comprehensive design system for startup ecosystem',
              referenceLinks: []
            }
          ],
          goals: ['Start design consultancy', 'Publish design book', 'Teach UX workshops'],
          demands: ['Technical co-founder', 'Frontend developer', 'Business partner'],
          institutions: [
            {
              name: 'ByteDance',
              role: 'Senior Product Designer',
              description: 'Lead designer for TikTok\'s creator tools and monetization features',
              verified: true
            }
          ],
          university: {
            name: 'Shanghai University of Finance and Economics',
            verified: true
          },
          matchScore: 92,
          bio: 'Senior Product Designer at tech startup with passion for creating user-centered experiences',
          oneSentenceIntro: 'I design digital experiences that make complex tasks feel effortless.',
          receivesLeft: 8,
          requestedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
          mutualInterest: 'Perfect design-tech match! 🎨 You have the Python skills she needs for her design tool project, while she offers the UX expertise for your AI platform. Both looking for co-founders in China.',
          wechatId: 'Emma_Designer2024',
          giftedReceives: 2 // She gifted you 2 receives
        },
        {
          id: 'req_2', 
          name: 'David Liu',
          age: '31',
          gender: 'Male',
          avatar: '👨‍💻',
          location: 'Beijing, China',
          hobbies: ['Blockchain', 'Gaming', 'Investing'],
          languages: ['Mandarin', 'English', 'Korean'],
          skills: ['Blockchain', 'Smart Contracts', 'Web3', 'Solidity', 'DeFi', 'Rust'],
          resources: ['Blockchain Infrastructure', 'Crypto Community', 'VC Network', 'Mining Farm Access'],
          projects: [
            {
              title: 'DeFi Lending Protocol',
              role: 'Lead Developer',
              description: 'Built decentralized lending platform with $50M+ TVL',
              referenceLinks: ['https://github.com/davidliu/defi-protocol']
            },
            {
              title: 'NFT Marketplace',
              role: 'Co-founder & CTO',
              description: 'Launched NFT platform for digital artists in Asia',
              referenceLinks: ['https://nftasia.com']
            }
          ],
          goals: ['Build next unicorn startup', 'Create Web3 ecosystem', 'Mentor blockchain developers'],
          demands: ['Business co-founder', 'Marketing expert', 'Regulatory advisor'],
          institutions: [
            {
              name: 'Binance',
              role: 'Former Blockchain Engineer',
              description: 'Core contributor to Binance Smart Chain development',
              verified: true
            }
          ],
          university: {
            name: 'Tsinghua University',
            verified: true
          },
          matchScore: 88,
          bio: 'Blockchain developer and crypto enthusiast building the future of decentralized finance',
          oneSentenceIntro: 'I build blockchain solutions that democratize access to financial services.',
          receivesLeft: 12,
          requestedAt: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 hours ago
          mutualInterest: 'Great tech synergy! ⚡ Your AI background complements his blockchain expertise perfectly for building next-gen fintech solutions. He\'s seeking technical co-founders with your skill set.',
          wechatId: 'DavidLiu_BlockDev'
          // No giftedReceives - will not show gift label
        }
      ];
      setFriendRequests(mockRequests);
    }
  }, [isProfileComplete, friendRequests.length]);

  const showBottomNav = currentScreen !== 'welcome' && currentScreen !== 'profile-setup';

  return (
    <LanguageProvider>
      <div className="w-full h-screen bg-white flex flex-col overflow-hidden mx-auto" style={{ maxWidth: 'min(100vw, 600px)', minWidth: '320px' }}>
      {/* Status Bar - Keep height for device status bar but remove content */}
      <div className="bg-white" style={{ height: 'max(2.75rem, env(safe-area-inset-top, 2.75rem))' }}>
        {/* Empty div to maintain status bar height */}
      </div>

      {/* Main Content */}
      <div className="flex-1 relative">
        {/* Welcome and Profile Setup - use AnimatePresence for these since they're one-time flows */}
        <AnimatePresence mode="wait">
          {currentScreen === 'welcome' && (
            <motion.div
              key="welcome"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0"
            >
              <WelcomeScreen onGetStarted={() => setCurrentScreen('profile-setup')} />
            </motion.div>
          )}

          {currentScreen === 'profile-setup' && (
            <motion.div
              key="profile-setup"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0"
            >
              <ProfileSetupWizard 
                onComplete={handleProfileComplete}
                onBack={() => setCurrentScreen('welcome')}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main App Screens - keep mounted to preserve state */}
        {isProfileComplete && (
          <>
            {/* Chat Interface - always mounted when profile is complete */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ 
                opacity: currentScreen === 'home' ? 1 : 0,
                pointerEvents: currentScreen === 'home' ? 'auto' : 'none'
              }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0"
            >
              <ChatInterface 
                userProfile={userProfile} 
                onShowHistory={() => setShowHistory(true)}
                onShowNotifications={handleShowNotifications}
                onAddContact={handleAddContact}
                addedContactIds={addedContactIds}
                unreadNotifications={unreadNotifications}
                quotedFromNotification={quotedFromNotification}
                onClearQuotedNotification={() => setQuotedFromNotification(null)}
                currentPlan={currentPlan}
                receivesLeft={receivesLeft}
                onTopUpReceives={handleTopUpReceives}
                onGiftReceives={handleGiftReceives}
                singleCardInChat={singleCardInChat}
                onClearSingleCard={() => setSingleCardInChat(null)}
              />
            </motion.div>

            {/* Profile Screen */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ 
                opacity: currentScreen === 'profile' ? 1 : 0,
                pointerEvents: currentScreen === 'profile' ? 'auto' : 'none'
              }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0"
            >
              <ProfileView 
                userProfile={userProfile} 
                onUpdate={handleProfileUpdate}
              />
            </motion.div>

            {/* Settings Screen */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ 
                opacity: currentScreen === 'settings' ? 1 : 0,
                pointerEvents: currentScreen === 'settings' ? 'auto' : 'none'
              }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0"
            >
              <SettingsScreen 
              currentPlan={currentPlan}
              receivesLeft={receivesLeft}
              onPlanChange={handlePlanChange}
              onTopUpReceives={handleTopUpReceives}
              onGiftReceives={handleGiftReceives}
            />
            </motion.div>
          </>
        )}
      </div>

      {/* Bottom Navigation */}
      {showBottomNav && (
        <motion.div
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <BottomNavigation 
            currentScreen={currentScreen} 
            onScreenChange={handleScreenChange}
          />
        </motion.div>
      )}
      
      {/* Contact History Modal */}
      <AnimatePresence>
        {showHistory && (
          <ContactHistory
            isOpen={showHistory}
            onClose={() => setShowHistory(false)}
            contacts={contactHistory}
            onReportContact={handleReportContact}
            onQuoteContact={handleQuoteFromHistory}
            onRemoveContact={handleRemoveFromHistory}
            onViewOriginalCard={handleViewOriginalCard}
            onGiftReceives={handleGiftReceives}
          />
        )}
      </AnimatePresence>

      {/* Notification Panel */}
      <NotificationPanel
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
        friendRequests={friendRequests}
        onQuoteContact={handleQuoteFromNotification}
        onRemoveRequest={handleRemoveRequest}
        onAddToHistory={handleAddWhisperToHistory}
        onViewOriginalCard={handleViewOriginalCard}
        onGiftReceives={handleGiftReceives}
      />
      </div>
    </LanguageProvider>
  );
}