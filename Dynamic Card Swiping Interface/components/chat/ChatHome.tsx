import { useState, useEffect, useRef } from 'react';
import svgIcons from './svg-icons';
import { ImageWithFallback } from '../figma/ImageWithFallback';
import { t } from '../../translations';

interface ChatHomeProps {
  onNavigateToNotification: () => void;
  onNavigateToSettings: () => void;
  onChatSelect: (chatId: number) => void;
}

// New Match data - recent mutual matches
const newMatchData = [
  // Recent matches - showing only 2-3 at a time
  [
    {
      id: 1,
      name: "Sarah Johnson",
      projectTitle: "AI Creative Platform",
      avatar: "https://images.unsplash.com/photo-1652471949169-9c587e8898cd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3b21hbiUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNzQ5Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      matchTime: "2 minutes ago",
      chatId: 5
    },
    {
      id: 2,
      name: "Michael Chen",
      projectTitle: "VR Education App",
      avatar: "https://images.unsplash.com/photo-1672685667592-0392f458f46f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtYW4lMjBwcm9mZXNzaW9uYWwlMjBwb3J0cmFpdHxlbnwxfHx8fDE3NTYxOTcwMzZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      matchTime: "1 hour ago",
      chatId: 6
    }
  ],
  // Alternate set
  [
    {
      id: 3,
      name: "Emily Davis",
      projectTitle: "Blockchain Solution",
      avatar: "https://images.unsplash.com/photo-1563132337-f159f484226c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEwMDY1MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      matchTime: "3 hours ago",
      chatId: 7
    },
    {
      id: 4,
      name: "David Wilson",
      projectTitle: "Smart IoT Hub",
      avatar: "https://images.unsplash.com/photo-1601489865452-407a1b801dde?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBtYW4lMjBzdWl0fGVufDF8fHx8MTc1NjE5Nzc1Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      matchTime: "Yesterday",
      chatId: 8
    }
  ]
];

// Chat list data
type ChatItemData = {
  id: number;
  name: string;
  lastMessage: string;
  time: string;
  unreadCount: number;
  avatar: string;
  archived?: boolean;
  pinned?: boolean;
};

const initialChats: ChatItemData[] = [
  {
    id: 1,
    name: "Jessica Parker",
    lastMessage: "Thanks for the update!",
    time: "2:30 PM",
    unreadCount: 2,
    avatar: "https://images.unsplash.com/photo-1652471949169-9c587e8898cd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3b21hbiUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNzQ5Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    archived: false,
    pinned: true,
  },
  {
    id: 2,
    name: "Mark Stevens",
    lastMessage: "Let's schedule a meeting",
    time: "1:15 PM",
    unreadCount: 0,
    avatar: "https://images.unsplash.com/photo-1672685667592-0392f458f46f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtYW4lMjBwcm9mZXNzaW9uYWwlMjBwb3J0cmFpdHxlbnwxfHx8fDE3NTYxOTcwMzZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    archived: false,
    pinned: false,
  },
  {
    id: 3,
    name: "Anna Miller",
    lastMessage: "Perfect! See you then",
    time: "12:45 PM",
    unreadCount: 1,
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEzMDI5M3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    archived: false,
    pinned: false,
  },
  {
    id: 4,
    name: "Tom Anderson",
    lastMessage: "Great work on the project",
    time: "11:30 AM",
    unreadCount: 0,
    avatar: "https://images.unsplash.com/photo-1739298061757-7a3339cee982?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNjAzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    archived: true,
    pinned: false,
  }
];

function PopupButton() {
  return (
    <div className="box-border content-stretch flex gap-[3px] items-start justify-center leading-[0] px-0 py-[13px] relative shrink-0 text-nowrap" data-name="Popup Button">
      <div className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic relative shrink-0 text-[#0055f7] text-[40px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[9px] text-nowrap whitespace-pre">Ques</p>
      </div>
      <div className="css-r804ei flex flex-col font-['SF_Pro:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#0088ff] text-[18px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[18px] text-nowrap whitespace-pre">􀆏</p>
      </div>
    </div>
  );
}

function IconButton({ onClick }: { onClick?: () => void }) {
  return (
    <div 
      className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0 cursor-pointer" 
      data-name="!!<IconButton>"
      onClick={onClick}
    >
      <div className="relative shrink-0 size-6" data-name="Icon">
        <div className="absolute inset-[8.33%_12.05%_0.78%_8.34%]" data-name="Group">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 22">
            <g id="Group">
              <path clipRule="evenodd" d={svgIcons.notificationIcon} fill="var(--fill-0, white)" fillRule="evenodd" id="Vector" />
              <path clipRule="evenodd" d={svgIcons.notificationDot} fill="var(--fill-0, black)" fillRule="evenodd" id="Vector_2" />
            </g>
          </svg>
        </div>
      </div>
    </div>
  );
}

function IconButton1({ onClick }: { onClick?: () => void }) {
  return (
    <div 
      className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0 cursor-pointer" 
      data-name="!!<IconButton>"
      onClick={onClick}
    >
      <div className="relative shrink-0 size-6" data-name="Icon">
        <div className="absolute inset-[8.33%_12.76%_0.78%_12.76%]" data-name="Group">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 22">
            <g id="Group">
              <path clipRule="evenodd" d={svgIcons.messageIcon} fill="var(--fill-0, black)" fillRule="evenodd" id="Vector" />
              <path clipRule="evenodd" d={svgIcons.messageIconDot} fill="var(--fill-0, black)" fillRule="evenodd" id="Vector_2" />
            </g>
          </svg>
        </div>
      </div>
    </div>
  );
}

function IconButton2({ onClick }: { onClick?: () => void }) {
  return (
    <div 
      className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0 cursor-pointer" 
      data-name="!!<IconButton>"
      onClick={onClick}
    >
      <div className="relative shrink-0 size-6" data-name="Icon">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
          <g id="Icon">
            <path d={svgIcons.settingsIcon} fill="var(--fill-0, black)" id="Vector" />
          </g>
        </svg>
      </div>
    </div>
  );
}

function Frame19({ onNavigateToNotification, onNavigateToSettings }: { onNavigateToNotification: () => void; onNavigateToSettings: () => void }) {
  return (
    <div className="content-stretch flex items-center justify-start relative shrink-0 w-[120px]">
      <IconButton />
      <IconButton1 onClick={onNavigateToNotification} />
      <IconButton2 onClick={onNavigateToSettings} />
    </div>
  );
}

function Frame16({ onNavigateToNotification, onNavigateToSettings }: { onNavigateToNotification: () => void; onNavigateToSettings: () => void }) {
  return (
    <div className="content-stretch flex h-[52px] items-end justify-between relative shrink-0 w-[355px]">
      <PopupButton />
      <Frame19 onNavigateToNotification={onNavigateToNotification} onNavigateToSettings={onNavigateToSettings} />
    </div>
  );
}

function UpperBar({ onNavigateToNotification, onNavigateToSettings }: { onNavigateToNotification: () => void; onNavigateToSettings: () => void }) {
  return (
    <div className="bg-neutral-50 h-[90px] relative shrink-0" data-name="upper bar">
      <div className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative">
        <Frame16 onNavigateToNotification={onNavigateToNotification} onNavigateToSettings={onNavigateToSettings} />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

// Refresh and close button components removed as per requirements

function Frame40() {
  return (
    <div className="bg-[#ffffff] h-[29px] relative shrink-0 w-[363px]">
      <div className="absolute left-0 right-0 bottom-0 h-[1px] z-10 chat-people-border"></div>
      <div className="absolute flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-medium h-[26px] justify-end leading-[0] left-0 text-[#000000] text-[16px] top-[26px] translate-y-[-100%] w-[363px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <h3 className="leading-[normal] whitespace-pre chat-people-title">
          {t('newMatches') || '新匹配'}
        </h3>
      </div>
    </div>
  );
}

function Frame39() {
  return (
    <div className="content-stretch flex flex-col gap-4 items-center justify-start relative shrink-0">
      <Frame40 />
    </div>
  );
}

// Old components removed - replaced with NewMatchAvatar

function NewMatchAvatar({ match, onAvatarClick }: { match: any; onAvatarClick: (chatId: number) => void }) {
  return (
    <div 
      className="relative shrink-0 cursor-pointer"
      data-name="new-match-avatar"
      onClick={() => onAvatarClick(match.chatId)}
    >
      <div className="relative">
        {/* 醒目的渐变边框 - 放大尺寸，变细边框 */}
        <div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 p-0.5">
          <div className="w-full h-full rounded-full bg-white p-0.5">
            <ImageWithFallback 
              className="w-full h-full rounded-full object-cover" 
              src={match.avatar}
              alt={match.name}
            />
          </div>
        </div>
        {/* 新匹配指示点 - 嵌入头像框 */}
        <div className="absolute top-0 right-0 w-4 h-4 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center">
          <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
        </div>
      </div>
      {/* 用户名 */}
      <div className="mt-1.5 text-left">
        <p className="font-['Instrument_Sans:Medium',_sans-serif] font-medium text-[12px] text-[#000000] truncate max-w-[64px]" style={{ fontVariationSettings: "'wdth' 100" }}>
          {match.name}
        </p>
        <p className="font-['Instrument_Sans:Regular',_sans-serif] font-normal text-[9px] text-[#0088ff] mt-0.5" style={{ fontVariationSettings: "'wdth' 100" }}>
          {match.matchTime}
        </p>
      </div>
    </div>
  );
}

// Component36 replaced with NewMatchAvatar

// Component38 replaced with NewMatchAvatar

function NewMatchList({ matchData, onAvatarClick }: { matchData: any[]; onAvatarClick: (chatId: number) => void }) {
  // Empty state when no matches
  if (!matchData || matchData.length === 0) {
    return (
      <div className="content-stretch flex items-start justify-start relative shrink-0 py-4 px-4">
        <div className="text-left">
          <p className="font-['Instrument_Sans:Medium',_sans-serif] font-medium text-[12px] text-[#666666]" style={{ fontVariationSettings: "'wdth' 100" }}>
            {t('noNewMatches') || '暂无新的匹配'}
          </p>
          <p className="font-['Instrument_Sans:Regular',_sans-serif] font-normal text-[10px] text-[#999999] mt-1" style={{ fontVariationSettings: "'wdth' 100" }}>
            {t('keepSwipingForMatches') || '继续滑动以发现更多匹配！'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="content-stretch flex gap-4 items-start justify-start relative shrink-0 px-4">
      {matchData.map((match, index) => (
        <NewMatchAvatar 
          key={match.id} 
          match={match} 
          onAvatarClick={onAvatarClick}
        />
      ))}
    </div>
  );
}

function ChatItem({ 
  chat, 
  isOpen, 
  onOpen, 
  onClose, 
  onChatSelect,
  onDelete,
  onPinToggle,
  onArchiveToggle
}: { 
  chat: ChatItemData; 
  isOpen: boolean; 
  onOpen: (id: number) => void; 
  onClose: () => void; 
  onChatSelect: (chatId: number) => void;
  onDelete: (id: number) => void;
  onPinToggle: (id: number) => void;
  onArchiveToggle: (id: number) => void;
}) {
  const startXRef = useRef<number | null>(null);
  const currentXRef = useRef<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dx, setDx] = useState(0);

  useEffect(() => {
    setDx(isOpen ? -250 : 0);
  }, [isOpen]);

  const clamp = (v: number, min: number, max: number) => Math.max(min, Math.min(max, v));

  const onStart = (clientX: number) => {
    startXRef.current = clientX;
    currentXRef.current = dx;
  };

  const onMove = (clientX: number) => {
    if (startXRef.current === null) return;
    const delta = clientX - startXRef.current;
    const next = clamp(currentXRef.current + delta, -250, 0);
    setDx(next);
  };

  const onEnd = () => {
    if (dx <= -100) {
      onOpen(chat.id);
      setDx(-250);
    } else {
      onClose();
      setDx(0);
    }
    startXRef.current = null;
  };

  return (
    <div className="relative overflow-hidden">
      {/* 操作区 */}
      <div className="absolute inset-y-0 right-0 flex items-stretch gap-1 pr-2 pl-4" aria-hidden>
        <button
          onClick={() => { onDelete(chat.id); onClose(); }}
          className="my-2 px-3 w-[72px] rounded-md bg-red-500 text-white text-sm font-medium hover:bg-red-600 transition"
        >{t('delete') || '删除'}</button>
        <button
          onClick={() => { onPinToggle(chat.id); onClose(); }}
          className="my-2 px-3 w-[72px] rounded-md bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition"
        >{chat.pinned ? (t('unpin') || '取消置顶') : (t('pin') || '置顶')}</button>
        <button
          onClick={() => { onArchiveToggle(chat.id); onClose(); }}
          className="my-2 px-3 w-[72px] rounded-md bg-gray-200 text-gray-800 text-sm font-medium hover:bg-gray-300 transition"
        >{chat.archived ? (t('unarchive') || '取消归档') : (t('archive') || '归档')}</button>
      </div>

      {/* 卡片 */}
      <div
        ref={containerRef}
        className={`flex items-center gap-3 p-3 ${chat.pinned ? 'bg-blue-50' : 'bg-white'} cursor-pointer select-none`}
        style={{ transform: `translateX(${dx}px)`, transition: startXRef.current === null ? 'transform 0.18s ease' : 'none' }}
        onClick={() => onChatSelect(chat.id)}
        onTouchStart={(e) => onStart(e.touches[0].clientX)}
        onTouchMove={(e) => onMove(e.touches[0].clientX)}
        onTouchEnd={onEnd}
        onMouseDown={(e) => onStart(e.clientX)}
        onMouseMove={(e) => { if (startXRef.current !== null) onMove(e.clientX); }}
        onMouseUp={onEnd}
        onMouseLeave={() => { if (startXRef.current !== null) onEnd(); }}
      >
        <div className="relative">
          <ImageWithFallback 
            className="size-12 rounded-full object-cover" 
            src={chat.avatar}
            alt={chat.name}
          />
          {chat.unreadCount > 0 && !chat.archived && (
            <div className="absolute -top-1 -right-1 bg-[#0088ff] text-white text-xs rounded-full size-5 flex items-center justify-center">
              {chat.unreadCount}
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="font-['Instrument_Sans:Medium',_sans-serif] font-medium text-[16px] text-[#000000] truncate" style={{ fontVariationSettings: "'wdth' 100" }}>
              {chat.name}
            </h4>
            <span className="font-['Instrument_Sans:Regular',_sans-serif] font-normal text-[12px] text-[#666666]" style={{ fontVariationSettings: "'wdth' 100" }}>
              {chat.time}
            </span>
          </div>
          <p className="font-['Instrument_Sans:Regular',_sans-serif] font-normal text-[14px] text-[#666666] truncate mt-1" style={{ fontVariationSettings: "'wdth' 100" }}>
            {chat.lastMessage}
          </p>
        </div>
      </div>
    </div>
  );
}

function ChatList({ 
  chats,
  sortOption,
  onChatSelect,
  openSwipeId,
  setOpenSwipeId,
  onDelete,
  onPinToggle,
  onArchiveToggle
}: {
  chats: ChatItemData[];
  sortOption: 'all' | 'unread' | 'archived';
  onChatSelect: (chatId: number) => void;
  openSwipeId: number | null;
  setOpenSwipeId: (id: number | null) => void;
  onDelete: (id: number) => void;
  onPinToggle: (id: number) => void;
  onArchiveToggle: (id: number) => void;
}) {
  const filtered = chats.filter(chat => {
    if (sortOption === 'unread') return chat.unreadCount > 0 && !chat.archived;
    if (sortOption === 'archived') return !!chat.archived;
    return !chat.archived;
  });
  const sorted = filtered.sort((a, b) => Number(!!b.pinned) - Number(!!a.pinned));
  return (
    <div className="w-full">
      {sorted.map((chat) => (
        <ChatItem 
          key={chat.id} 
          chat={chat} 
          isOpen={openSwipeId === chat.id}
          onOpen={(id) => setOpenSwipeId(id)}
          onClose={() => setOpenSwipeId(null)}
          onChatSelect={onChatSelect}
          onDelete={onDelete}
          onPinToggle={onPinToggle}
          onArchiveToggle={onArchiveToggle}
        />
      ))}
      {sorted.length === 0 && (
        <div className="p-4 text-center text-sm text-gray-500">{t('noChatsInCategory') || '暂无此分类的会话'}</div>
      )}
    </div>
  );
}

function MaterialSymbolsSortRounded({ onClick }: { onClick?: () => void }) {
  return (
    <div 
      className="absolute left-[336px] size-4 top-1.5 cursor-pointer" 
      data-name="material-symbols:sort-rounded"
      onClick={onClick}
    >
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:sort-rounded">
          <path d={svgIcons.sortIcon} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function SortPopup({ 
  isOpen, 
  onClose, 
  onSelectOption, 
  currentOption 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  onSelectOption: (option: 'all' | 'unread' | 'archived') => void; 
  currentOption: string; 
}) {
  if (!isOpen) return null;

  return (
    <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg z-50 overflow-hidden">
      <div 
        className={`px-4 py-2 cursor-pointer font-['Instrument_Sans:Medium',_sans-serif] text-[14px] ${currentOption === 'all' ? 'bg-blue-100/60 text-[#0055F7]' : 'hover:bg-gray-50'}`}
        onClick={() => onSelectOption('all')}
      >
        {t('allChats') || '全部聊天'}
      </div>
      <div 
        className={`px-4 py-2 cursor-pointer font-['Instrument_Sans:Medium',_sans-serif] text-[14px] ${currentOption === 'unread' ? 'bg-blue-100/60 text-[#0055F7]' : 'hover:bg-gray-50'}`}
        onClick={() => onSelectOption('unread')}
      >
        {t('unread') || '未读'}
      </div>
      <div 
        className={`px-4 py-2 cursor-pointer font-['Instrument_Sans:Medium',_sans-serif] text-[14px] ${currentOption === 'archived' ? 'bg-blue-100/60 text-[#0055F7]' : 'hover:bg-gray-50'}`}
        onClick={() => onSelectOption('archived')}
      >
        {t('archived') || '已归档'}
      </div>
    </div>
  );
}

function Frame246({ 
  showSuggestions, 
  currentProfileSet,
  onAvatarClick
}: { 
  showSuggestions: boolean; 
  currentProfileSet: number;
  onAvatarClick: (chatId: number) => void;
}) {
  if (!showSuggestions) return null;
  
  return (
    <div className="content-stretch flex flex-col gap-6 items-start justify-start relative shrink-0 flex-none">
      <Frame39 />
      <NewMatchList matchData={newMatchData[currentProfileSet]} onAvatarClick={onAvatarClick} />
    </div>
  );
}

function Frame78({ 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  onChatSelect,
  unreadCount,
  chats,
  openSwipeId,
  setOpenSwipeId,
  onDelete,
  onPinToggle,
  onArchiveToggle 
}: { 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  onChatSelect: (chatId: number) => void;
  unreadCount: number;
  chats: ChatItemData[];
  openSwipeId: number | null;
  setOpenSwipeId: (id: number | null) => void;
  onDelete: (id: number) => void;
  onPinToggle: (id: number) => void;
  onArchiveToggle: (id: number) => void;
}) {
    return (
    <div className="bg-[#ffffff] relative shrink-0 w-[363px] flex flex-col flex-1 min-h-0">
      <div className="h-[29px] relative shrink-0">
        <div className="absolute left-0 right-0 bottom-0 h-[1px] z-10 chat-chats-border"></div>
        <div className="absolute flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-medium h-[26px] justify-end leading-[0] left-0 text-[#000000] text-[16px] top-[26px] translate-y-[-100%] w-[363px]" style={{ fontVariationSettings: "'wdth' 100" }}>
          <h3 className="leading-[normal] whitespace-pre chat-chats-title">
            {t('chats') || '聊天'}{unreadCount > 0 && <span className="font-['Instrument_Sans:Regular',_sans-serif] font-regular text-[#000000] text-[16px]" style={{ fontVariationSettings: "'wdth' 100" }}>({unreadCount})</span>}
          </h3>
        </div>
        <div className="relative">
          <MaterialSymbolsSortRounded onClick={onToggleSortPopup} />
          <SortPopup 
            isOpen={showSortPopup} 
            onClose={() => onToggleSortPopup()} 
            onSelectOption={onSortSelect} 
            currentOption={sortOption} 
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto min-h-0" onClick={() => setOpenSwipeId(null)}>
        <ChatList 
          chats={chats}
          sortOption={sortOption as 'all' | 'unread' | 'archived'} 
          onChatSelect={onChatSelect} 
          openSwipeId={openSwipeId}
          setOpenSwipeId={setOpenSwipeId}
          onDelete={onDelete}
          onPinToggle={onPinToggle}
          onArchiveToggle={onArchiveToggle}
        />
      </div>
    </div>
  );
}

function Frame14({ 
  showSuggestions, 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  currentProfileSet,
  onChatSelect,
  unreadCount,
  chats,
  openSwipeId,
  setOpenSwipeId,
  onDelete,
  onPinToggle,
  onArchiveToggle
}: { 
  showSuggestions: boolean; 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  currentProfileSet: number;
  onChatSelect: (chatId: number) => void;
  unreadCount: number;
  chats: ChatItemData[];
  openSwipeId: number | null;
  setOpenSwipeId: (id: number | null) => void;
  onDelete: (id: number) => void;
  onPinToggle: (id: number) => void;
  onArchiveToggle: (id: number) => void;
}) {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-4 h-[650px] items-start justify-start left-[7px] pb-0 pt-0 px-0 top-[12px] w-[379px]">
      <Frame246 
        showSuggestions={showSuggestions} 
        currentProfileSet={currentProfileSet}
        onAvatarClick={onChatSelect}
      />
      <Frame78 
        showSortPopup={showSortPopup} 
        onToggleSortPopup={onToggleSortPopup} 
        onSortSelect={onSortSelect} 
        sortOption={sortOption}
        onChatSelect={onChatSelect}
        unreadCount={unreadCount}
        // pass chats and swipe/action handlers down
        chats={chats}
        openSwipeId={openSwipeId}
        setOpenSwipeId={setOpenSwipeId}
        onDelete={onDelete}
        onPinToggle={onPinToggle}
        onArchiveToggle={onArchiveToggle}
      />
    </div>
  );
}

function MainContent({ 
  showSuggestions, 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  currentProfileSet,
  onChatSelect,
  unreadCount,
  chats,
  openSwipeId,
  setOpenSwipeId,
  onDelete,
  onPinToggle,
  onArchiveToggle
}: { 
  showSuggestions: boolean; 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  currentProfileSet: number;
  onChatSelect: (chatId: number) => void;
  unreadCount: number;
  chats: ChatItemData[];
  openSwipeId: number | null;
  setOpenSwipeId: (id: number | null) => void;
  onDelete: (id: number) => void;
  onPinToggle: (id: number) => void;
  onArchiveToggle: (id: number) => void;
}) {
  return (
    <div className="h-full overflow-hidden relative shrink-0 w-[393px]" data-name="main content">
      <Frame14 
        showSuggestions={showSuggestions} 
        showSortPopup={showSortPopup} 
        onToggleSortPopup={onToggleSortPopup} 
        onSortSelect={onSortSelect} 
        sortOption={sortOption} 
        currentProfileSet={currentProfileSet}
        onChatSelect={onChatSelect}
        unreadCount={unreadCount}
        chats={chats}
        openSwipeId={openSwipeId}
        setOpenSwipeId={setOpenSwipeId}
        onDelete={onDelete}
        onPinToggle={onPinToggle}
        onArchiveToggle={onArchiveToggle}
      />
    </div>
  );
}

function Screen({ 
  onNavigateToNotification, 
  onNavigateToSettings,
  showSuggestions, 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  currentProfileSet,
  onChatSelect,
  unreadCount,
  chats,
  openSwipeId,
  setOpenSwipeId,
  onDelete,
  onPinToggle,
  onArchiveToggle
}: { 
  onNavigateToNotification: () => void; 
  onNavigateToSettings: () => void;
  showSuggestions: boolean; 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  currentProfileSet: number;
  onChatSelect: (chatId: number) => void;
  unreadCount: number;
  chats: ChatItemData[];
  openSwipeId: number | null;
  setOpenSwipeId: (id: number | null) => void;
  onDelete: (id: number) => void;
  onPinToggle: (id: number) => void;
  onArchiveToggle: (id: number) => void;
}) {
  return (
    <MainContent 
      showSuggestions={showSuggestions} 
      showSortPopup={showSortPopup} 
      onToggleSortPopup={onToggleSortPopup} 
      onSortSelect={onSortSelect} 
      sortOption={sortOption} 
      currentProfileSet={currentProfileSet}
      onChatSelect={onChatSelect}
      unreadCount={unreadCount}
      chats={chats}
      openSwipeId={openSwipeId}
      setOpenSwipeId={setOpenSwipeId}
      onDelete={onDelete}
      onPinToggle={onPinToggle}
      onArchiveToggle={onArchiveToggle}
    />
  );
}

export default function ChatHome({ onNavigateToNotification, onNavigateToSettings, onChatSelect }: ChatHomeProps) {
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [showSortPopup, setShowSortPopup] = useState(false);
  const [sortOption, setSortOption] = useState('all');
  const [currentProfileSet, setCurrentProfileSet] = useState(0);
  const [chats, setChats] = useState<ChatItemData[]>(initialChats);
  const [openSwipeId, setOpenSwipeId] = useState<number | null>(null);
  
  // Calculate total unread messages
  const unreadCount = chats.filter(c => !c.archived).reduce((total, chat) => total + chat.unreadCount, 0);

  // 强制样式应用 - 修复样式系统干扰问题
  useEffect(() => {
    const timer = setTimeout(() => {
      const peopleTitle = document.querySelector('.chat-people-title') as HTMLElement;
      const chatsTitle = document.querySelector('.chat-chats-title') as HTMLElement;
      const peopleBorder = document.querySelector('.chat-people-border') as HTMLElement;
      const chatsBorder = document.querySelector('.chat-chats-border') as HTMLElement;
      
      if (peopleTitle) {
        peopleTitle.style.setProperty('color', '#000000', 'important');
        peopleTitle.style.setProperty('font-weight', '400', 'important');
        peopleTitle.style.setProperty('background-color', 'transparent', 'important');
      }
      
      if (chatsTitle) {
        chatsTitle.style.setProperty('color', '#000000', 'important');
        chatsTitle.style.setProperty('font-weight', '400', 'important');
        chatsTitle.style.setProperty('background-color', 'transparent', 'important');
      }

      if (peopleBorder) {
        peopleBorder.style.setProperty('background-color', '#0088ff', 'important');
        peopleBorder.style.setProperty('height', '1px', 'important');
        peopleBorder.style.setProperty('display', 'block', 'important');
        peopleBorder.style.setProperty('border', 'none', 'important');
        peopleBorder.style.setProperty('box-shadow', 'none', 'important');
      }
      
      if (chatsBorder) {
        chatsBorder.style.setProperty('background-color', '#0088ff', 'important');
        chatsBorder.style.setProperty('height', '1px', 'important');
        chatsBorder.style.setProperty('display', 'block', 'important');
        chatsBorder.style.setProperty('border', 'none', 'important');
        chatsBorder.style.setProperty('box-shadow', 'none', 'important');
      }
    }, 500);
    
    return () => clearTimeout(timer);
  }, []);

  // Remove refresh functionality as buttons are removed

  const handleToggleSortPopup = () => {
    setShowSortPopup(prev => !prev);
  };

  const handleSortSelect = (option: 'all' | 'unread' | 'archived') => {
    setSortOption(option);
    setShowSortPopup(false);
  };

  const handleDelete = (id: number) => {
    setChats(prev => prev.filter(c => c.id !== id));
  };

  const handlePinToggle = (id: number) => {
    setChats(prev => prev.map(c => c.id === id ? { ...c, pinned: !c.pinned } : c));
  };

  const handleArchiveToggle = (id: number) => {
    setChats(prev => prev.map(c => c.id === id ? { ...c, archived: !c.archived } : c));
  };

  return (
    <div className="relative size-full" data-name="chat-home">
      <Screen 
        onNavigateToNotification={onNavigateToNotification}
        onNavigateToSettings={onNavigateToSettings}
        showSuggestions={showSuggestions}
        showSortPopup={showSortPopup}
        onToggleSortPopup={handleToggleSortPopup}
        onSortSelect={handleSortSelect}
        sortOption={sortOption}
        currentProfileSet={currentProfileSet}
        onChatSelect={onChatSelect}
        unreadCount={unreadCount}
        // pass chats and swipe/action handlers down
        chats={chats}
        openSwipeId={openSwipeId}
        setOpenSwipeId={setOpenSwipeId}
        onDelete={handleDelete}
        onPinToggle={handlePinToggle}
        onArchiveToggle={handleArchiveToggle}
      />
    </div>
  );
} 