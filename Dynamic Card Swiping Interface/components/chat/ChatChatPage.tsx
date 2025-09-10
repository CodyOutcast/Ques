import { useState, useRef, useEffect } from 'react';
import svgIcons from './svg-icons';
import MessageInput from './MessageInput';
import ChatMessage from './ChatMessage';
import { ImageWithFallback } from '../figma/ImageWithFallback';
// Remove custom UserProfilePage and use the full ProfilePage instead
import { ProfilePage } from '../ProfilePage';
import { t } from '../../translations';

interface ChatChatPageProps {
  onNavigateBack: () => void;
}

interface Message {
  id: number;
  text: string;
  time: string;
  isOwn: boolean;
  isNew?: boolean;
  status?: 'sending' | 'sent' | 'read' | 'failed';
}

// 示例用户数据
const sampleUser = {
  id: 1,
  name: 'Cody',
  age: 28,
  gender: 'Male',
  role: 'Blockchain Developer',
  distance: 2.5,
  avatar: '/sample/cody_avatar.jpg',
  tags: ['Blockchain', 'Web3', 'Smart Contracts', 'DeFi'],
  bio: 'Passionate blockchain developer with 5+ years of experience in building decentralized applications. Love working on innovative projects that push the boundaries of technology.',
  projects: [
    {
      id: 1,
      title: 'DeFi Yield Farming Platform',
      description: 'A comprehensive yield farming platform with automated strategies and risk management.',
      status: 'ongoing' as const,
      tags: ['DeFi', 'Yield Farming', 'Smart Contracts'],
      collaborators: 4
    },
    {
      id: 2,
      title: 'NFT Marketplace',
      description: 'A decentralized NFT marketplace with low fees and high performance.',
      status: 'finished' as const,
      tags: ['NFT', 'Marketplace', 'Ethereum'],
      collaborators: 6
    }
  ]
};

// Initial messages data
const initialMessages: Message[] = [
  {
    id: 1,
    text: "Hey, I'm interested in your project😎",
    time: "10:28",
    isOwn: false,
    status: 'read'
  }
];

function VuesaxLinearArrowLeft({ onClick }: { onClick?: () => void }) {
  return (
    <div className="absolute contents inset-0 cursor-pointer" data-name="vuesax/linear/arrow-left" onClick={(e) => { e.stopPropagation(); onClick && onClick(); }}>
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="arrow-left">
          <path d={svgIcons.arrowLeftIcon} id="Vector" stroke="var(--stroke-0, #424F63)" strokeLinecap="round" strokeLinejoin="round" strokeMiterlimit="10" strokeWidth="1.5" />
          <g id="Vector_2" opacity="0"></g>
        </g>
      </svg>
    </div>
  );
}

function VuesaxLinearArrowLeft1({ onClick }: { onClick?: () => void }) {
  return (
    <div className="relative shrink-0 size-6" data-name="vuesax/linear/arrow-left">
      <VuesaxLinearArrowLeft onClick={onClick} />
    </div>
  );
}

function Group8() {
  return (
    <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
      <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-10">
        <ImageWithFallback
          className="block max-w-none size-full rounded-full object-cover"
          src={sampleUser.avatar}
          alt={sampleUser.name}
        />
      </div>
      <div className="[grid-area:1_/_1] ml-[29px] mt-0 relative size-2">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 8 8">
          <circle cx="4" cy="4" fill="var(--fill-0, #00CC5E)" id="Ellipse 14" r="4" />
        </svg>
      </div>
    </div>
  );
}

function Frame60({ isNewMatch = false, onUserClick }: { isNewMatch?: boolean; onUserClick: () => void }) {
  // 固定在线状态用于演示
  const isOnline = true;
  const lastSeenTime = null;

  useEffect(() => {
    try {
      const nameEl = document.querySelector('[data-chat-username]') as HTMLElement | null;
      const nameText = document.querySelector('[data-chat-username-text]') as HTMLElement | null;
      if (nameEl) {
        nameEl.style.setProperty('color', '#000000', 'important');
        nameEl.style.setProperty('font-weight', '700', 'important');
        // do not force font-size here to respect user adjustments
        nameEl.style.setProperty('line-height', '1.1', 'important');
        nameEl.style.setProperty('opacity', '1', 'important');
      }
      if (nameText) {
        nameText.style.setProperty('color', '#000000', 'important');
        nameText.style.setProperty('opacity', '1', 'important');
      }
    } catch {}
  }, []);

  return (
    <div 
      className="content-stretch flex flex-col items-start justify-start leading-[0] relative shrink-0 text-nowrap"
    >
      {/* 用户名 - Bold 放大并使用黑色 */}
      <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-bold relative shrink-0 text-black text-[32px]" style={{ fontVariationSettings: "'wdth' 100" }} data-chat-username>
        <p className="leading-[normal] text-nowrap whitespace-pre" data-chat-username-text>{sampleUser.name}</p>
      </div>
      
      {/* 状态显示 - 新匹配优先，其次在线状态 */}
      {isNewMatch ? (
        <div className="font-['Instrument_Sans:Italic',_sans-serif] font-normal italic relative shrink-0 text-[#0055f7] text-[14px]" style={{ fontVariationSettings: "'wdth' 100" }}>
          <p className="leading-[normal] text-nowrap whitespace-pre">{t('newMatch') || '新匹配'}</p>
        </div>
      ) : (
        <div className="font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[#8593a8] text-[14px]" style={{ fontVariationSettings: "'wdth' 100" }}>
          <p className="leading-[normal] text-nowrap whitespace-pre">
            {isOnline ? (t('online') || '在线') : `${lastSeenTime}${t('ago') || '前在线'}`}
          </p>
        </div>
      )}
    </div>
  );
}

function Frame61({ onNavigateBack, isNewMatch, onUserClick }: { onNavigateBack: () => void; isNewMatch?: boolean; onUserClick: () => void }) {
  return (
    <div className="content-stretch flex gap-2.5 items-center justify-start relative shrink-0 w-[185px]">
      <div className="flex items-center" onClick={(e) => e.stopPropagation()}>
        <VuesaxLinearArrowLeft1 onClick={onNavigateBack} />
      </div>
      {/* 头像与文字区域，不再单独绑定点击，交由父级头部统一处理 */}
      <div className="flex items-center gap-2">
        <Group8 />
        <Frame60 isNewMatch={isNewMatch} onUserClick={onUserClick} />
      </div>
    </div>
  );
}

function RiMoreFill() {
  return (
    <div className="relative size-full" data-name="ri:more-fill">
      <div className="absolute inset-[41.67%_12.5%]" data-name="Vector">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 4">
          <path d={svgIcons.moreIcon} fill="var(--fill-0, black)" id="Vector" />
        </svg>
      </div>
    </div>
  );
}

function Frame62({ onNavigateBack, isNewMatch, onUserClick }: { onNavigateBack: () => void; isNewMatch?: boolean; onUserClick: () => void }) {
  return (
    <div className="content-stretch flex justify-between h-[52px] items-center relative shrink-0 cursor-pointer" onClick={onUserClick}>
      {/* 左侧：返回+用户信息，整块可点击（返回按钮除外） */}
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <Frame61 onNavigateBack={onNavigateBack} isNewMatch={isNewMatch} onUserClick={onUserClick} />
      </div>
      {/* 右侧更多按钮（同属可点击区域，不单独处理） */}
      <div className="relative shrink-0 size-6" data-name="ri:more-fill">
        <RiMoreFill />
      </div>
    </div>
  );
}

function Frame247({ messages }: { messages: Message[] }) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="w-full h-full overflow-y-auto">
      <div className="flex flex-col gap-2 items-start justify-start px-4 pt-2 pb-4 min-h-full">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message.text}
            time={message.time}
            isOwn={message.isOwn}
            isNew={message.isNew}
            status={message.status}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default function ChatChatPage({ onNavigateBack }: ChatChatPageProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isNewMatch, setIsNewMatch] = useState(false); // 可以通过props传入或根据逻辑判断
  const [showUserProfile, setShowUserProfile] = useState(false);

  // 清理：移除调试 mount 日志与边框
  // useEffect(() => {
  //   try { 
  //     console.log('[ChatChatPage] mounted'); 
  //     const el = document.getElementById('chat-detail-root');
  //     if (el) {
  //       el.style.outline = '3px dashed magenta';
  //       el.style.outlineOffset = '2px';
  //       console.log('[ChatChatPage] debug outline applied to #chat-detail-root');
  //     } else {
  //       console.warn('[ChatChatPage] #chat-detail-root not found at mount');
  //     }
  //   } catch {}
  // }, []);

  const getCurrentTime = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    return `${hours}:${minutes.toString().padStart(2, '0')}`;
  };

  const handleSendMessage = (messageText: string) => {
    const newMessage: Message = {
      id: messages.length + 1,
      text: messageText,
      time: getCurrentTime(),
      isOwn: true,
      isNew: true,
      status: 'sending'
    };

    setMessages(prev => [...prev, newMessage]);

    // 模拟发送过程
    setTimeout(() => {
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id ? { ...msg, status: 'sent' } : msg
      ));
    }, 1000);

    // 模拟对方已读
    setTimeout(() => {
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id ? { ...msg, status: 'read' } : msg
      ));
    }, 3000);

    // 移除自动回复
    // setTimeout(() => {
    //   const responseMessage: Message = {
    //     id: messages.length + 2,
    //     text: "Thanks for your message! I'll get back to you soon.",
    //     time: getCurrentTime(),
    //     isOwn: false,
    //     isNew: true,
    //     status: 'read'
    //   };
    //   setMessages(prev => [...prev, responseMessage]);
    // }, 2000);
  };

  const handleUploadFiles = (files: FileList) => {
    const fileArr = Array.from(files);
    const images = fileArr.filter(f => f.type.startsWith('image/'));
    const videos = fileArr.filter(f => f.type.startsWith('video/'));
    const summary = `Uploaded ${images.length} image(s)${videos.length?`, ${videos.length} video(s)`:''}`;
    const newMessage: Message = {
      id: messages.length + 1,
      text: summary,
      time: getCurrentTime(),
      isOwn: true,
      isNew: true,
      status: 'sent'
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleUserClick = () => {
    setShowUserProfile(true);
  };

  const handleBackFromProfile = () => {
    setShowUserProfile(false);
  };

  if (showUserProfile) {
    return (
      <ProfilePage 
        onBack={handleBackFromProfile}
        readOnly={true}
        showBackHeader={false}
        compactHero={true}
      />
    );
  }

  return (
    <div className="h-[662px] flex flex-col relative bg-white pb-[100px]" data-name="chat-chat page">
      {/* Scoped style to enforce sizes/colors */}
      <style>
        {`
          /* Username: apply to container and inner p - do not force size */
          [data-name="chat-chat page"] [data-chat-username],
          [data-name="chat-chat page"] [data-chat-username] p {
            font-weight: 700 !important; color: #000000 !important; line-height: 1.1 !important;
          }
          /* Chat text: container and inner p at 16px */
          [data-name="chat-chat page"] [data-chat-message-other],
          [data-name="chat-chat page"] [data-chat-message-own],
          [data-name="chat-chat page"] [data-chat-message-other-text],
          [data-name="chat-chat page"] [data-chat-message-own-text] {
            font-size: 16px !important;
          }
          /* Other text color */
          [data-name="chat-chat page"] [data-chat-message-other-text] { color: #000000 !important; }
          /* Time: apply bold without changing size */
          [data-name="chat-chat page"] [data-chat-message-time],
          [data-name="chat-chat page"] [data-chat-message-time] p {
            font-weight: 700 !important; color: #3d3d3d !important;
          }
        `}
      </style>
      {/* 聊天头部 - 用户信息 */}
      <div className="px-[7px] pt-[11px] pb-4 shrink-0">
        <Frame62 onNavigateBack={onNavigateBack} isNewMatch={isNewMatch} onUserClick={handleUserClick} />
      </div>
      
      {/* 聊天内容区域 - 确保可以滚动 */}
      <div className="flex-1 overflow-hidden">
        <Frame247 messages={messages} />
      </div>
      
      {/* 输入框：固定在底部栏上方 */}
      <div className="px-[23px] pb-[16px] pt-2 absolute left-0 right-0 bottom-[50px]">
        <div className="bg-white rounded-[30px] h-[46px] shadow-md">
          <MessageInput onSendMessage={handleSendMessage} onUploadFiles={handleUploadFiles} />
        </div>
      </div>
    </div>
  );
}
