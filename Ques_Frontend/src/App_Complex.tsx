import React, { useState, useEffect } from 'react';
// import { motion, AnimatePresence } from 'motion/react';
import { WelcomeScreen } from './components/WelcomeScreen';
import { ProfileSetupWizard } from './components/ProfileSetupWizard';
import { ChatInterface } from './components/ChatInterface';
import { ProfileView } from './components/ProfileView';
import { SettingsScreen } from './components/SettingsScreen';
import { BottomNavigation } from './components/BottomNavigation';
import { ContactHistory, type ContactedUser } from './components/ContactHistory';
import { NotificationPanel, type FriendRequest } from './components/NotificationPanel';
import { SwipeableCardStack } from './components/SwipeableCardStack';

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
      avatar: recommendation.avatar,
      skills: recommendation.skills,
      location: recommendation.location,
      matchScore: recommendation.matchScore,
      bio: recommendation.bio,
      projects: recommendation.projects,
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
      avatar: contact.avatar,
      skills: contact.skills,
      location: contact.location,
      bio: contact.bio,
      matchScore: contact.matchScore,
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
      avatar: request.avatar,
      skills: request.skills,
      location: request.location,
      matchScore: request.matchScore,
      bio: request.bio,
      projects: [], // Friend requests don't have projects data
      contactedAt: new Date(),
      reported: false,
    };
    
    // Add to contact history
    setContactHistory(prev => [newContact, ...prev]);
    
    // Track this contact as added to prevent it from appearing again
    setAddedContactIds(prev => new Set(prev).add(request.id));
  };

  const handleViewOriginalCard = (contact: FriendRequest | ContactedUser) => {
    // Convert to the format expected by SwipeableCardStack
    const cardData = {
      id: contact.id,
      name: contact.name,
      avatar: contact.avatar,
      skills: contact.skills,
      location: contact.location,
      matchScore: contact.matchScore,
      bio: contact.bio,
      oneSentenceIntro: contact.bio, // Use bio as fallback
      projects: 'projects' in contact ? contact.projects : ['Sample Project 1', 'Sample Project 2'],
      whyMatch: 'mutualInterest' in contact ? contact.mutualInterest : 'You have matching interests and complementary skills.',
    };
    
    setShowOriginalCard(cardData);
  };

  const handleCloseOriginalCard = () => {
    setShowOriginalCard(null);
  };

  const handleTopUpReceives = (amount: number) => {
    setReceivesLeft(prev => prev + amount);
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
      setReceivesLeft(5); // Reset to basic limit
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
          avatar: '👩‍💼',
          skills: ['Product Design', 'UX Research', 'Figma'],
          location: 'Shanghai, China',
          bio: 'Senior Product Designer at tech startup',
          matchScore: 92,
          requestedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
          mutualInterest: 'Perfect design-tech match! 🎨 You have the Python skills she needs for her design tool project, while she offers the UX expertise for your AI platform. Both looking for co-founders in China.',
          wechatId: 'Emma_Designer2024',
          giftedReceives: 2 // She gifted you 2 receives
        },
        {
          id: 'req_2', 
          name: 'David Liu',
          avatar: '👨‍💻',
          skills: ['Blockchain', 'Smart Contracts', 'Web3'],
          location: 'Beijing, China',
          matchScore: 88,
          bio: 'Blockchain developer and crypto enthusiast',
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
    <div className="w-full h-screen bg-white flex flex-col overflow-hidden" style={{ maxWidth: '375px', margin: '0 auto' }}>
      {/* Status Bar Simulator */}
      <div className="h-11 bg-white flex items-center justify-between px-4 text-sm">
        <span>9:41</span>
        <span>Ques</span>
        <div className="flex items-center gap-1">
          <div className="w-4 h-2 bg-black rounded-sm"></div>
          <div className="w-1 h-2 bg-black rounded-sm"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 relative">
        {/* Welcome and Profile Setup - use AnimatePresence for these since they're one-time flows */}
        {/* <AnimatePresence mode="wait"> */}
          {currentScreen === 'welcome' && (
            <div
              className="absolute inset-0"
            >
              <WelcomeScreen onGetStarted={() => setCurrentScreen('profile-setup')} />
            </div>
          )}

          {currentScreen === 'profile-setup' && (
            <div
              className="absolute inset-0"
            >
              <ProfileSetupWizard 
                onComplete={handleProfileComplete}
                onBack={() => setCurrentScreen('welcome')}
              />
            </div>
          )}
        {/* </AnimatePresence> */}

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
      />

      {/* Original Card View */}
      <AnimatePresence>
        {showOriginalCard && (
          <SwipeableCardStack
            recommendations={[showOriginalCard]}
            onWhisper={() => {}} // Disabled for single card view
            onIgnore={() => {}} // Disabled for single card view  
            onClose={handleCloseOriginalCard}
            currentPlan={currentPlan}
            receivesLeft={receivesLeft}
            onTopUpReceives={handleTopUpReceives}
            onGiftReceives={handleGiftReceives}
          />
        )}
      </AnimatePresence>
    </div>
  );
}