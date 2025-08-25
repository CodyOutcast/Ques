import { useState, useRef, useEffect } from 'react';
import svgPaths from "../imports/svg-0oogqy1o34";

// Placeholder avatar URLs using DiceBear API
const imgAvatars3DAvatar1 = "https://api.dicebear.com/7.x/avataaars/svg?seed=avatar1";
const imgEllipse11 = "https://api.dicebear.com/7.x/avataaars/svg?seed=kevin";
const imgEllipse12 = "https://api.dicebear.com/7.x/avataaars/svg?seed=druids";
const imgEllipse13 = "https://api.dicebear.com/7.x/avataaars/svg?seed=minari";
const imgEllipse14 = "https://api.dicebear.com/7.x/avataaars/svg?seed=frankie";
const imgEllipse15 = "https://api.dicebear.com/7.x/avataaars/svg?seed=samuel";
const imgEllipse16 = "https://api.dicebear.com/7.x/avataaars/svg?seed=alex";

// Mock chat data for simulation
const mockChats = [
  {
    id: 1,
    name: "kevin.eth",
    lastMessage: "haha",
    time: "14:28",
    unreadCount: 1,
    avatar: imgEllipse11,
    isOnline: true,
  },
  {
    id: 2,
    name: "druids.eth",
    lastMessage: "I thought it was you, lol",
    time: "yesterday",
    unreadCount: 3,
    avatar: imgEllipse12,
    isOnline: false,
  },
  {
    id: 3,
    name: "minari.sol",
    lastMessage: "[Waiting for reply]",
    time: "yesterday",
    unreadCount: 0,
    avatar: imgEllipse13,
    isOnline: false,
    isWaitingReply: true,
  },
  {
    id: 4,
    name: "0x71C7656EC7ab4...dFB7",
    lastMessage: "Whats up Sam, it's Frankie. 😏",
    time: "Friday",
    unreadCount: 0,
    avatar: imgEllipse14,
    isOnline: false,
  },
  {
    id: 5,
    name: "Samuel Garry",
    lastMessage: "Done, 😏",
    time: "07/21/2022",
    unreadCount: 0,
    avatar: imgEllipse15,
    isOnline: false,
  },
  {
    id: 6,
    name: "Alex Chen",
    lastMessage: "Great idea for the project!",
    time: "2 days ago",
    unreadCount: 2,
    avatar: imgEllipse16,
    isOnline: true,
  },
  {
    id: 7,
    name: "sarah.dev",
    lastMessage: "Let's schedule a meeting",
    time: "3 days ago",
    unreadCount: 0,
    avatar: imgEllipse11,
    isOnline: false,
  },
  {
    id: 8,
    name: "crypto_builder",
    lastMessage: "I found a bug in the smart contract",
    time: "1 week ago",
    unreadCount: 1,
    avatar: imgEllipse12,
    isOnline: true,
  }
];

// Mock profile suggestions data pools
const profileSuggestions = [
  [
    { id: 1, name: "Hilima Bibi", role: "Investor", avatar: imgAvatars3DAvatar1 },
    { id: 2, name: "John Doe", role: "Developer", avatar: imgAvatars3DAvatar1 },
    { id: 3, name: "Sarah Chen", role: "Designer", avatar: imgAvatars3DAvatar1 }
  ],
  [
    { id: 4, name: "Mike Wang", role: "Product Manager", avatar: imgAvatars3DAvatar1 },
    { id: 5, name: "Lisa Kim", role: "Marketing Lead", avatar: imgAvatars3DAvatar1 },
    { id: 6, name: "David Lee", role: "Backend Engineer", avatar: imgAvatars3DAvatar1 }
  ],
  [
    { id: 7, name: "Emma Wilson", role: "UI/UX Designer", avatar: imgAvatars3DAvatar1 },
    { id: 8, name: "James Brown", role: "Data Scientist", avatar: imgAvatars3DAvatar1 },
    { id: 9, name: "Anna Garcia", role: "Business Analyst", avatar: imgAvatars3DAvatar1 }
  ]
];

const filterOptions = ['all', 'my greetings', 'others\' greetings'] as const;
type FilterOption = typeof filterOptions[number];

interface EnhancedChatHomeProps {
  onChatSelect: (chat: typeof mockChats[0]) => void;
  onNotificationClick: () => void;
}

function PopupButton() {
  return (
    <div
      className="box-border content-stretch flex gap-[3px] items-start justify-center leading-[0] px-0 py-[13px] relative shrink-0 text-nowrap"
      data-name="Popup Button"
    >
      <div
        className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic relative shrink-0 text-[#0055f7] text-[40px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[9px] text-nowrap whitespace-pre">Ques</p>
      </div>
      <div
        className="css-r804ei flex flex-col font-['SF_Pro:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#0088ff] text-[18px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[18px] text-nowrap whitespace-pre">􀆏</p>
      </div>
    </div>
  );
}

function RefreshButton({ onClick, isRefreshing }: { onClick: () => void; isRefreshing: boolean }) {
  return (
    <button 
      onClick={onClick} 
      disabled={isRefreshing}
      className={`relative shrink-0 size-4 cursor-pointer hover:opacity-70 transition-all duration-300 ${
        isRefreshing ? 'animate-spin' : ''
      }`}
    >
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:refresh-rounded">
          <path d={svgPaths.p17b74300} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </button>
  );
}

function CloseButton({ onClick }: { onClick: () => void }) {
  return (
    <button onClick={onClick} className="relative shrink-0 size-4 cursor-pointer hover:opacity-70 transition-all duration-200 hover:rotate-90">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:close-rounded">
          <path d={svgPaths.p3a73d3a2} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </button>
  );
}

function FilterButton({ onClick, isOpen }: { onClick: () => void; isOpen: boolean }) {
  return (
    <button 
      onClick={onClick} 
      className={`relative shrink-0 size-4 cursor-pointer hover:opacity-70 transition-all duration-200 z-10 ${
        isOpen ? 'rotate-180' : ''
      }`}
    >
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:sort-rounded">
          <path d={svgPaths.p32915380} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </button>
  );
}

function UnreadBadge({ count }: { count: number }) {
  if (count === 0) return null;
  
  return (
    <div className="relative shrink-0">
      <div className="size-5">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
          <circle cx="10" cy="10" fill="#0573F3" r="10" />
        </svg>
      </div>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="font-['Instrument_Sans:Regular',_sans-serif] font-normal text-[#f6fbff] text-[12px] leading-none">
          {count}
        </span>
      </div>
    </div>
  );
}

function ChatItem({ 
  chat, 
  onSelect, 
  isPressed 
}: { 
  chat: typeof mockChats[0]; 
  onSelect: (chat: typeof mockChats[0]) => void;
  isPressed: boolean;
}) {
  return (
    <button 
      onClick={() => onSelect(chat)}
      className={`h-16 relative shrink-0 w-full transition-all duration-150 text-left rounded-lg px-2 py-1 ${
        isPressed 
          ? 'bg-[#E8F3FF] border-l-4 border-[#0055f7] shadow-sm scale-98' 
          : 'hover:bg-gray-50 active:bg-[#E8F3FF] active:border-l-4 active:border-[#0055f7] active:scale-98'
      }`}
    >
      <div className="absolute box-border content-stretch flex gap-[9px] items-start justify-start left-2 p-0 top-2">
        <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
          <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-12">
            <img className="block max-w-none size-full rounded-full" height="48" src={chat.avatar} width="48" />
          </div>
          {chat.isOnline && (
            <div className="[grid-area:1_/_1] ml-[37px] mt-px relative size-3">
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 12">
                <circle cx="6" cy="6" fill="#00CC5E" r="6" />
              </svg>
            </div>
          )}
        </div>
        <div className="h-12 leading-[0] relative shrink-0 text-[16px] text-nowrap tracking-[-0.32px] w-[148px]">
          <div
            className={`absolute font-['Instrument_Sans:Medium',_sans-serif] font-medium left-[0.5px] top-0 transition-colors duration-150 ${
              isPressed ? 'text-[#0055f7]' : 'text-[#213241]'
            }`}
            style={{ fontVariationSettings: "'wdth' 100" }}
          >
            <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">{chat.name}</p>
          </div>
          <div
            className={`absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal left-0 top-6 transition-colors duration-150 ${
              chat.isWaitingReply ? 'text-[#0055f7] italic' : isPressed ? 'text-[#0077cc]' : 'text-[#8593a8]'
            }`}
            style={{ fontVariationSettings: "'wdth' 100" }}
          >
            <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">{chat.lastMessage}</p>
          </div>
        </div>
      </div>
      <div className="absolute box-border content-stretch flex flex-col gap-1 items-end justify-start leading-[0] p-0 right-2 top-2">
        <div
          className={`font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[12px] text-nowrap tracking-[-0.24px] transition-colors duration-150 ${
            isPressed ? 'text-[#0077cc]' : 'text-[#8593a8]'
          }`}
          style={{ fontVariationSettings: "'wdth' 100" }}
        >
          <p className="adjustLetterSpacing block leading-[24px] whitespace-pre">{chat.time}</p>
        </div>
        <UnreadBadge count={chat.unreadCount} />
      </div>
    </button>
  );
}

function ProfileCard({ profile, index }: { profile: any; index: number }) {
  return (
    <div 
      className="bg-[#ffffff] h-[166px] relative rounded-xl shrink-0 w-[109px] transform transition-all duration-500 ease-out"
      style={{ 
        animationDelay: `${index * 100}ms`,
        animation: 'slideInUp 0.6s ease-out forwards'
      }}
    >
      <div className="box-border content-stretch flex flex-col gap-2 h-[166px] items-center justify-center overflow-clip pb-6 pt-8 px-6 relative w-[109px]">
        <div className="relative shrink-0 size-14">
          <div
            className="absolute bg-center bg-cover bg-no-repeat inset-0 rounded-full"
            style={{ backgroundImage: `url('${profile.avatar}')` }}
          />
        </div>
        <div className="box-border content-stretch flex flex-col gap-1 items-center justify-center leading-[0] p-0 relative shrink-0 text-center">
          <div
            className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium justify-center relative shrink-0 text-[#000000] text-[16px] w-32"
            style={{ fontVariationSettings: "'wdth' 100" }}
          >
            <p className="block leading-[normal]">{profile.name}</p>
          </div>
          <div
            className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#666666] text-[12px] w-[138px]"
            style={{ fontVariationSettings: "'wdth' 100" }}
          >
            <p className="block leading-[normal]">{profile.role}</p>
          </div>
        </div>
        <button className="bg-[#0088ff] box-border content-stretch flex gap-2.5 h-[29px] items-end justify-center px-[18px] py-2 relative rounded-[100px] shrink-0 hover:bg-[#0066cc] transition-colors duration-200">
          <div
            className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold justify-center leading-[0] relative shrink-0 text-[#ffffff] text-[12px] text-nowrap"
            style={{ fontVariationSettings: "'wdth' 100" }}
          >
            <p className="block leading-[normal] whitespace-pre">check</p>
          </div>
        </button>
      </div>
      <div
        aria-hidden="true"
        className="absolute border-[#eceaf5] border-[5px] border-solid inset-[-5px] pointer-events-none rounded-[17px]"
      />
    </div>
  );
}

export default function EnhancedChatHome({ onChatSelect, onNotificationClick }: EnhancedChatHomeProps) {
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [showFilterMenu, setShowFilterMenu] = useState(false);
  const [currentFilter, setCurrentFilter] = useState<FilterOption>('all');
  const [chats, setChats] = useState(mockChats);
  const [currentProfileSet, setCurrentProfileSet] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [profiles, setProfiles] = useState(profileSuggestions[0]);
  const [pressedChatId, setPressedChatId] = useState<number | null>(null);
  const filterMenuRef = useRef<HTMLDivElement>(null);

  // Close filter menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (filterMenuRef.current && !filterMenuRef.current.contains(event.target as Node)) {
        setShowFilterMenu(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    
    // Simulate loading time
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const nextSet = (currentProfileSet + 1) % profileSuggestions.length;
    setCurrentProfileSet(nextSet);
    setProfiles(profileSuggestions[nextSet]);
    setIsRefreshing(false);
  };

  const handleCloseSuggestions = () => {
    setShowSuggestions(false);
  };

  const handleFilterClick = () => {
    setShowFilterMenu(!showFilterMenu);
  };

  const handleFilterSelect = (filter: FilterOption) => {
    setCurrentFilter(filter);
    setShowFilterMenu(false);
    
    // Filter chats based on selection
    let filteredChats = mockChats;
    if (filter === 'my greetings') {
      filteredChats = mockChats.filter(chat => chat.isWaitingReply);
    } else if (filter === 'others\' greetings') {
      filteredChats = mockChats.filter(chat => chat.unreadCount > 0);
    }
    setChats(filteredChats);
  };

  const handleChatSelect = (chat: typeof mockChats[0]) => {
    setPressedChatId(chat.id);
    // Small delay to show the pressed state before navigating
    setTimeout(() => {
      onChatSelect(chat);
      setPressedChatId(null);
    }, 150);
  };

  const filteredChatsCount = chats.length;

  return (
    <div className="bg-[#fcfcfd] flex flex-col gap-2 h-[844px] overflow-clip relative w-[393px]">
      <style jsx>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeInDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeOutUp {
          from {
            opacity: 1;
            transform: translateY(0);
          }
          to {
            opacity: 0;
            transform: translateY(-10px);
          }
        }
        
        .animate-fadeInDown {
          animation: fadeInDown 0.3s ease-out forwards;
        }
        
        .animate-fadeOutUp {
          animation: fadeOutUp 0.3s ease-out forwards;
        }
        
        .smooth-scroll {
          scroll-behavior: smooth;
        }
        
        .scale-98 {
          transform: scale(0.98);
        }
      `}</style>

      {/* Upper Bar */}
      <div className="bg-neutral-50 h-[90px] relative shrink-0">
        <div className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative">
          <div className="box-border content-stretch flex h-[52px] items-end justify-between p-0 relative shrink-0 w-[355px]">
            <PopupButton />
            <div className="box-border content-stretch flex items-center justify-start p-0 relative shrink-0 w-[81px]">
              <div className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0">
                {/* Settings Icon */}
                <div className="relative shrink-0 size-6">
                  <div className="absolute inset-[8.33%_12.05%_0.78%_8.34%]">
                    <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 22">
                      <g>
                        <path clipRule="evenodd" d={svgPaths.p2992a100} fill="white" fillRule="evenodd" />
                        <path clipRule="evenodd" d={svgPaths.p3651e400} fill="black" fillRule="evenodd" />
                      </g>
                    </svg>
                  </div>
                </div>
              </div>
              <button 
                onClick={onNotificationClick}
                className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0 hover:opacity-70 transition-opacity cursor-pointer"
              >
                {/* Profile/Notification Icon */}
                <div className="relative shrink-0 size-6">
                  <div className="absolute inset-[8.33%_12.76%_0.78%_12.76%]">
                    <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 22">
                      <g>
                        <path clipRule="evenodd" d={svgPaths.p36ad9000} fill="black" fillRule="evenodd" />
                        <path clipRule="evenodd" d={svgPaths.p3dc12500} fill="black" fillRule="evenodd" />
                      </g>
                    </svg>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
        <div
          aria-hidden="true"
          className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none"
        />
      </div>

      {/* People You May Want to Know Section */}
      {showSuggestions && (
        <div className={`box-border content-stretch flex flex-col gap-6 items-center justify-start p-0 px-4 relative shrink-0 transition-all duration-500 ease-out ${
          showSuggestions ? 'animate-fadeInDown' : 'animate-fadeOutUp'
        }`}>
          <div className="box-border content-stretch flex flex-col gap-4 items-center justify-start p-0 relative shrink-0">
            <div className="bg-[#ffffff] h-[30px] relative shrink-0 w-[363px]">
              <div
                aria-hidden="true"
                className="absolute border-[#0088ff] border-[0px_0px_1px] border-solid bottom-[-1px] left-0 pointer-events-none right-0 top-0"
              />
              <div
                className="absolute flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-[26px] justify-end leading-[0] left-0 text-[#000000] text-[16px] top-[26px] translate-y-[-100%] w-[363px]"
                style={{ fontVariationSettings: "'wdth' 100" }}
              >
                <p className="block leading-[normal]">People You May Want to Know...</p>
              </div>
              <div className="absolute box-border content-stretch flex gap-1.5 items-center justify-start left-[314px] p-0 top-2.5">
                <RefreshButton onClick={handleRefresh} isRefreshing={isRefreshing} />
                <CloseButton onClick={handleCloseSuggestions} />
              </div>
            </div>
          </div>
          
          {/* Suggestion Cards */}
          <div className="box-border content-stretch flex gap-4 items-start justify-start p-0 relative shrink-0">
            {profiles.map((profile, index) => (
              <ProfileCard key={`${profile.id}-${currentProfileSet}`} profile={profile} index={index} />
            ))}
          </div>
        </div>
      )}

      {/* Chats Section */}
      <div className="flex-1 overflow-hidden px-4">
        <div className="box-border content-stretch flex flex-col gap-4 items-center justify-start p-0 relative shrink-0">
          <div className="relative w-[363px]" ref={filterMenuRef}>
            {/* Restructured header to prevent button overlap */}
            <div className="box-border content-stretch flex items-center justify-between p-0 relative shrink-0 w-[363px] h-[26px]">
              <div
                aria-hidden="true"
                className="absolute border-[#0088ff] border-[0px_0px_1px] border-solid bottom-[-1px] left-0 pointer-events-none right-0 top-0"
              />
              <div
                className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-[26px] justify-center leading-[0] relative shrink-0 text-[#000000] text-[16px] pointer-events-none"
                style={{ fontVariationSettings: "'wdth' 100" }}
              >
                <p className="block leading-[normal]">Chats ({filteredChatsCount})</p>
              </div>
              <FilterButton onClick={handleFilterClick} isOpen={showFilterMenu} />
            </div>
            
            {/* Filter Menu */}
            {showFilterMenu && (
              <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg z-20 min-w-[140px] animate-fadeInDown">
                {filterOptions.map((option) => (
                  <button
                    key={option}
                    onClick={() => handleFilterSelect(option)}
                    className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 first:rounded-t-lg last:rounded-b-lg transition-colors duration-150 ${
                      currentFilter === option ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat List - Scrollable with proper bottom padding */}
        <div className="mt-4 h-full overflow-y-auto space-y-2 pb-24 smooth-scroll">
          {chats.map((chat) => (
            <ChatItem 
              key={chat.id} 
              chat={chat} 
              onSelect={handleChatSelect} 
              isPressed={pressedChatId === chat.id}
            />
          ))}
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="bg-[#ffffff] h-[100px] relative shrink-0">
        <div className="absolute h-[100px] left-0 top-0 w-full">
          <div
            aria-hidden="true"
            className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none"
          />
          <div className="absolute bg-[#0088ff] h-14 left-[169px] rounded-[100px] top-6 w-14 hover:bg-[#0066cc] transition-colors duration-200 hover:scale-105 transform">
            <div className="box-border content-stretch flex flex-col h-14 items-center justify-center overflow-clip p-4 relative w-14">
              <div className="relative shrink-0 size-6">
                <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
                  <g>
                    <path clipRule="evenodd" d="M12 6a1 1 0 0 1 1 1v4h4a1 1 0 1 1 0 2h-4v4a1 1 0 1 1-2 0v-4H7a1 1 0 1 1 0-2h4V7a1 1 0 0 1 1-1z" fill="white" fillRule="evenodd" />
                  </g>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}