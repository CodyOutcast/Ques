import { useState } from 'react';
import svgPaths from "./svg-4qmai1fpwm";
import { ImageWithFallback } from '../components/figma/ImageWithFallback';

interface ChatHomeProps {
  onNavigateToNotification: () => void;
  onNavigateToSettings: () => void;
  onChatSelect: (chatId: number) => void;
}

// People profile data with real avatars - expanded for refresh functionality
const allProfileData = [
  // First set
  [
    {
      id: 1,
      name: "Sarah Johnson",
      title: "Marketing Director",
      avatar: "https://images.unsplash.com/photo-1652471949169-9c587e8898cd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3b21hbiUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNzQ5Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    },
    {
      id: 2,
      name: "Michael Chen",
      title: "Software Engineer",
      avatar: "https://images.unsplash.com/photo-1672685667592-0392f458f46f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtYW4lMjBwcm9mZXNzaW9uYWwlMjBwb3J0cmFpdHxlbnwxfHx8fDE3NTYxOTcwMzZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    },
    {
      id: 3,
      name: "Alex Rodriguez",
      title: "Product Manager",
      avatar: "https://images.unsplash.com/photo-1739298061757-7a3339cee982?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNjAzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    }
  ],
  // Second set
  [
    {
      id: 4,
      name: "Emily Davis",
      title: "Business Analyst",
      avatar: "https://images.unsplash.com/photo-1563132337-f159f484226c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEwMDY1MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    },
    {
      id: 5,
      name: "David Wilson",
      title: "Finance Director",
      avatar: "https://images.unsplash.com/photo-1601489865452-407a1b801dde?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBtYW4lMjBzdWl0fGVufDF8fHx8MTc1NjE5Nzc1Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    },
    {
      id: 6,
      name: "Lisa Thompson",
      title: "UX Designer",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEzMDI5M3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    }
  ]
];

// Chat list data
const chatListData = [
  {
    id: 1,
    name: "Jessica Parker",
    lastMessage: "Thanks for the update!",
    time: "2:30 PM",
    unreadCount: 2,
    avatar: "https://images.unsplash.com/photo-1652471949169-9c587e8898cd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3b21hbiUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNzQ5Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
  },
  {
    id: 2,
    name: "Mark Stevens",
    lastMessage: "Let's schedule a meeting",
    time: "1:15 PM",
    unreadCount: 0,
    avatar: "https://images.unsplash.com/photo-1672685667592-0392f458f46f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtYW4lMjBwcm9mZXNzaW9uYWwlMjBwb3J0cmFpdHxlbnwxfHx8fDE3NTYxOTcwMzZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
  },
  {
    id: 3,
    name: "Anna Miller",
    lastMessage: "Perfect! See you then",
    time: "12:45 PM",
    unreadCount: 1,
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEzMDI5M3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
  },
  {
    id: 4,
    name: "Tom Anderson",
    lastMessage: "Great work on the project",
    time: "11:30 AM",
    unreadCount: 0,
    avatar: "https://images.unsplash.com/photo-1739298061757-7a3339cee982?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNjAzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
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

function Group() {
  return (
    <div className="absolute inset-[8.33%_12.05%_0.78%_8.34%]" data-name="Group">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 22">
        <g id="Group">
          <path clipRule="evenodd" d={svgPaths.p2992a100} fill="var(--fill-0, white)" fillRule="evenodd" id="Vector" />
          <path clipRule="evenodd" d={svgPaths.p3651e400} fill="var(--fill-0, black)" fillRule="evenodd" id="Vector_2" />
        </g>
      </svg>
    </div>
  );
}

function Icon() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <Group />
    </div>
  );
}

function Icon1() {
  return (
    <div className="content-stretch flex items-start justify-start relative shrink-0" data-name="<Icon>">
      <Icon />
    </div>
  );
}

function IconButton() {
  return (
    <div className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0" data-name="!!<IconButton>">
      <Icon1 />
    </div>
  );
}

function Group1() {
  return (
    <div className="absolute inset-[8.33%_12.76%_0.78%_12.76%]" data-name="Group">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 22">
        <g id="Group">
          <path clipRule="evenodd" d={svgPaths.p36ad9000} fill="var(--fill-0, black)" fillRule="evenodd" id="Vector" />
          <path clipRule="evenodd" d={svgPaths.p3dc12500} fill="var(--fill-0, black)" fillRule="evenodd" id="Vector_2" />
        </g>
      </svg>
    </div>
  );
}

function Icon2() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <Group1 />
    </div>
  );
}

function Icon3() {
  return (
    <div className="content-stretch flex items-start justify-start relative shrink-0" data-name="<Icon>">
      <Icon2 />
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
      <Icon3 />
    </div>
  );
}

function Icon4() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Icon">
          <path d={svgPaths.p36c52800} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Icon5() {
  return (
    <div className="content-stretch flex items-start justify-start relative shrink-0" data-name="<Icon>">
      <Icon4 />
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
      <Icon5 />
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

function MaterialSymbolsRefreshRounded({ isRefreshing, onClick }: { isRefreshing?: boolean; onClick?: () => void }) {
  return (
    <div 
      className={`relative shrink-0 size-4 cursor-pointer transition-transform duration-1000 ${isRefreshing ? 'animate-spin' : ''}`}
      data-name="material-symbols:refresh-rounded"
      onClick={onClick}
    >
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:refresh-rounded">
          <path d={svgPaths.p17b74300} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function MaterialSymbolsCloseRounded({ onClick }: { onClick?: () => void }) {
  return (
    <div 
      className="relative shrink-0 size-4 cursor-pointer" 
      data-name="material-symbols:close-rounded"
      onClick={onClick}
    >
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:close-rounded">
          <path d={svgPaths.p3a73d3a2} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame244({ isRefreshing, onRefresh, onCloseSuggestions }: { isRefreshing: boolean; onRefresh: () => void; onCloseSuggestions: () => void }) {
  return (
    <div className="absolute content-stretch flex gap-1.5 items-center justify-start left-[314px] top-2.5">
      <MaterialSymbolsRefreshRounded isRefreshing={isRefreshing} onClick={onRefresh} />
      <MaterialSymbolsCloseRounded onClick={onCloseSuggestions} />
    </div>
  );
}

function Frame40({ isRefreshing, onRefresh, onCloseSuggestions }: { isRefreshing: boolean; onRefresh: () => void; onCloseSuggestions: () => void }) {
  return (
    <div className="bg-[#ffffff] h-[30px] relative shrink-0 w-[363px]">
      <div aria-hidden="true" className="absolute border-[#0088ff] border-[0px_0px_1px] border-solid bottom-[-1px] left-0 pointer-events-none right-0 top-0" />
      <div className="absolute flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-[26px] justify-end leading-[0] left-0 text-[#000000] text-[16px] top-[26px] translate-y-[-100%] w-[363px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] whitespace-pre">People You May Want to Know...</p>
      </div>
      <Frame244 isRefreshing={isRefreshing} onRefresh={onRefresh} onCloseSuggestions={onCloseSuggestions} />
    </div>
  );
}

function Frame39({ isRefreshing, onRefresh, onCloseSuggestions }: { isRefreshing: boolean; onRefresh: () => void; onCloseSuggestions: () => void }) {
  return (
    <div className="content-stretch flex flex-col gap-4 items-center justify-start relative shrink-0">
      <Frame40 isRefreshing={isRefreshing} onRefresh={onRefresh} onCloseSuggestions={onCloseSuggestions} />
    </div>
  );
}

function Component3DAvatars1({ avatar, isRefreshing }: { avatar: string; isRefreshing?: boolean }) {
  return (
    <div 
      className={`relative shrink-0 size-14 transition-all duration-600 ${isRefreshing ? 'scale-90 opacity-70' : ''}`}
      data-name="3D Avatars / 1"
    >
      <ImageWithFallback 
        className="absolute inset-0 size-full rounded-full object-cover" 
        src={avatar}
        alt="Profile"
      />
    </div>
  );
}

function Frame241({ name, title, isRefreshing }: { name: string; title: string; isRefreshing?: boolean }) {
  return (
    <div 
      className={`content-stretch flex flex-col gap-1 items-center justify-center leading-[0] relative shrink-0 text-center transition-transform duration-600 ${isRefreshing ? '-translate-y-1' : ''}`}
    >
      <div className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium justify-center relative shrink-0 text-[#000000] text-[16px] w-32" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal]">{name}</p>
      </div>
      <div className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#666666] text-[12px] w-[138px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal]">{title}</p>
      </div>
    </div>
  );
}

function Tag() {
  return (
    <div className="bg-[#0088ff] box-border content-stretch flex gap-2.5 h-[29px] items-end justify-center px-[18px] py-2 relative rounded-[100px] shrink-0" data-name="Tag">
      <div aria-hidden="true" className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[100px]" />
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold justify-center leading-[0] relative shrink-0 text-[#ffffff] text-[12px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] whitespace-pre">check</p>
      </div>
    </div>
  );
}

function Tag1() {
  return (
    <div className="bg-[#0088ff] box-border content-stretch flex gap-2.5 h-[29px] items-end justify-center px-[18px] py-2 relative rounded-[100px] shrink-0" data-name="Tag">
      <div aria-hidden="true" className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[100px]" />
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold justify-center leading-[0] relative shrink-0 text-[#ffffff] text-[12px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] whitespace-pre">check</p>
      </div>
    </div>
  );
}

function Tag2() {
  return (
    <div className="bg-[#0088ff] box-border content-stretch flex gap-2.5 h-[29px] items-end justify-center px-[18px] py-2 relative rounded-[100px] shrink-0" data-name="Tag">
      <div aria-hidden="true" className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[100px]" />
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold justify-center leading-[0] relative shrink-0 text-[#ffffff] text-[12px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] whitespace-pre">check</p>
      </div>
    </div>
  );
}

function Component37({ profile, isRefreshing }: { profile: any; isRefreshing?: boolean }) {
  return (
    <div 
      className={`bg-[#ffffff] h-[166px] relative rounded-[12px] shrink-0 w-[109px] transition-transform duration-600 ${isRefreshing ? '-translate-y-2' : ''}`}
      data-name="37"
    >
      <div className="box-border content-stretch flex flex-col gap-2 h-[166px] items-center justify-center overflow-clip pb-6 pt-8 px-6 relative w-[109px]">
        <Component3DAvatars1 avatar={profile.avatar} isRefreshing={isRefreshing} />
        <Frame241 name={profile.name} title={profile.title} isRefreshing={isRefreshing} />
        <Tag />
      </div>
      <div aria-hidden="true" className="absolute border-[#eceaf5] border-[5px] border-solid inset-[-5px] pointer-events-none rounded-[17px]" />
    </div>
  );
}

function Component36({ profile, isRefreshing }: { profile: any; isRefreshing?: boolean }) {
  return (
    <div 
      className={`bg-[#ffffff] h-[166px] relative rounded-[12px] shrink-0 w-[109px] transition-transform duration-600 delay-100 ${isRefreshing ? '-translate-y-2' : ''}`}
      data-name="36"
    >
      <div className="box-border content-stretch flex flex-col gap-2 h-[166px] items-center justify-center overflow-clip pb-6 pt-8 px-6 relative w-[109px]">
        <Component3DAvatars1 avatar={profile.avatar} isRefreshing={isRefreshing} />
        <Frame241 name={profile.name} title={profile.title} isRefreshing={isRefreshing} />
        <Tag1 />
      </div>
      <div aria-hidden="true" className="absolute border-[#eceaf5] border-[5px] border-solid inset-[-5px] pointer-events-none rounded-[17px]" />
    </div>
  );
}

function Component38({ profile, isRefreshing }: { profile: any; isRefreshing?: boolean }) {
  return (
    <div 
      className={`bg-[#ffffff] h-[166px] relative rounded-[12px] shrink-0 w-[109px] transition-transform duration-600 delay-200 ${isRefreshing ? '-translate-y-2' : ''}`}
      data-name="38"
    >
      <div className="box-border content-stretch flex flex-col gap-2 h-[166px] items-center justify-center overflow-clip pb-6 pt-8 px-6 relative w-[109px]">
        <Component3DAvatars1 avatar={profile.avatar} isRefreshing={isRefreshing} />
        <Frame241 name={profile.name} title={profile.title} isRefreshing={isRefreshing} />
        <Tag2 />
      </div>
      <div aria-hidden="true" className="absolute border-[#eceaf5] border-[5px] border-solid inset-[-5px] pointer-events-none rounded-[17px]" />
    </div>
  );
}

function Frame245({ profileData, isRefreshing }: { profileData: any[]; isRefreshing?: boolean }) {
  return (
    <div className="content-stretch flex gap-4 items-start justify-start relative shrink-0">
      <Component37 profile={profileData[0]} isRefreshing={isRefreshing} />
      <Component36 profile={profileData[1]} isRefreshing={isRefreshing} />
      <Component38 profile={profileData[2]} isRefreshing={isRefreshing} />
    </div>
  );
}

function ChatItem({ chat, onChatSelect }: { chat: any; onChatSelect: (chatId: number) => void }) {
  return (
    <div 
      className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
      onClick={() => onChatSelect(chat.id)}
    >
      <div className="relative">
        <ImageWithFallback 
          className="size-12 rounded-full object-cover" 
          src={chat.avatar}
          alt={chat.name}
        />
        {chat.unreadCount > 0 && (
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
  );
}

function ChatList({ onChatSelect }: { onChatSelect: (chatId: number) => void }) {
  return (
    <div className="w-full">
      {chatListData.map((chat) => (
        <ChatItem key={chat.id} chat={chat} onChatSelect={onChatSelect} />
      ))}
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
          <path d={svgPaths.p32915380} fill="var(--fill-0, black)" id="Vector" />
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
        className="px-4 py-2 hover:bg-gray-50 cursor-pointer font-['Instrument_Sans:Medium',_sans-serif] text-[14px]"
        onClick={() => onSelectOption('all')}
      >
        All Chats
      </div>
      <div 
        className="px-4 py-2 hover:bg-gray-50 cursor-pointer font-['Instrument_Sans:Medium',_sans-serif] text-[14px]"
        onClick={() => onSelectOption('unread')}
      >
        Unread
      </div>
      <div 
        className="px-4 py-2 hover:bg-gray-50 cursor-pointer font-['Instrument_Sans:Medium',_sans-serif] text-[14px]"
        onClick={() => onSelectOption('archived')}
      >
        Archived
      </div>
    </div>
  );
}

function MdiContact() {
  return (
    <div className="absolute left-[15px] size-6 top-[15px]" data-name="mdi:contact">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="mdi:contact">
          <path d={svgPaths.p18e83d80} fill="var(--fill-0, white)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function VuesaxBoldMessageText() {
  return (
    <div className="absolute contents left-[15px] top-[15px]" data-name="vuesax/bold/message-text">
      <MdiContact />
    </div>
  );
}

function BtnNewChat() {
  return (
    <div className="absolute left-[316px] size-[54px] top-[587px]" data-name="__btn-new-chat">
      <VuesaxBoldMessageText />
    </div>
  );
}

function Frame246({ 
  showSuggestions, 
  isRefreshing, 
  onRefresh, 
  onCloseSuggestions,
  currentProfileSet
}: { 
  showSuggestions: boolean; 
  isRefreshing: boolean; 
  onRefresh: () => void; 
  onCloseSuggestions: () => void; 
  currentProfileSet: number;
}) {
  if (!showSuggestions) return null;
  
  return (
    <div className="content-stretch flex flex-col gap-6 items-center justify-start relative shrink-0">
      <Frame39 isRefreshing={isRefreshing} onRefresh={onRefresh} onCloseSuggestions={onCloseSuggestions} />
      <Frame245 profileData={allProfileData[currentProfileSet]} isRefreshing={isRefreshing} />
    </div>
  );
}

function Frame78({ 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  onChatSelect 
}: { 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  onChatSelect: (chatId: number) => void;
}) {
  return (
    <div className="bg-[#ffffff] relative shrink-0 w-[363px] flex flex-col">
      <div className="h-[24px] relative">
        <div aria-hidden="true" className="absolute border-[#0088ff] border-[0px_0px_1px] border-solid bottom-[-1px] left-0 pointer-events-none right-0 top-0" />
        <div className="absolute flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-[20px] justify-end leading-[0] left-0 text-[#000000] text-[16px] top-[20px] translate-y-[-100%] w-[363px]" style={{ fontVariationSettings: "'wdth' 100" }}>
          <p className="leading-[normal] whitespace-pre">Chats</p>
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
      <ChatList onChatSelect={onChatSelect} />
    </div>
  );
}

function Frame14({ 
  showSuggestions, 
  isRefreshing, 
  onRefresh, 
  onCloseSuggestions, 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  currentProfileSet,
  onChatSelect
}: { 
  showSuggestions: boolean; 
  isRefreshing: boolean; 
  onRefresh: () => void; 
  onCloseSuggestions: () => void; 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  currentProfileSet: number;
  onChatSelect: (chatId: number) => void;
}) {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-4 h-[663px] items-center justify-start left-[7px] pb-0 pt-[11px] px-0 top-0 w-[379px]">
      <Frame246 
        showSuggestions={showSuggestions} 
        isRefreshing={isRefreshing} 
        onRefresh={onRefresh} 
        onCloseSuggestions={onCloseSuggestions} 
        currentProfileSet={currentProfileSet}
      />
      <Frame78 
        showSortPopup={showSortPopup} 
        onToggleSortPopup={onToggleSortPopup} 
        onSortSelect={onSortSelect} 
        sortOption={sortOption}
        onChatSelect={onChatSelect} 
      />
    </div>
  );
}

function MainContent({ 
  showSuggestions, 
  isRefreshing, 
  onRefresh, 
  onCloseSuggestions, 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  currentProfileSet,
  onChatSelect
}: { 
  showSuggestions: boolean; 
  isRefreshing: boolean; 
  onRefresh: () => void; 
  onCloseSuggestions: () => void; 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  currentProfileSet: number;
  onChatSelect: (chatId: number) => void;
}) {
  return (
    <div className="h-[663px] overflow-clip relative shrink-0 w-[393px]" data-name="main content">
      <Frame14 
        showSuggestions={showSuggestions} 
        isRefreshing={isRefreshing} 
        onRefresh={onRefresh} 
        onCloseSuggestions={onCloseSuggestions} 
        showSortPopup={showSortPopup} 
        onToggleSortPopup={onToggleSortPopup} 
        onSortSelect={onSortSelect} 
        sortOption={sortOption} 
        currentProfileSet={currentProfileSet}
        onChatSelect={onChatSelect}
      />
      <BtnNewChat />
    </div>
  );
}

function Screen({ 
  onNavigateToNotification, 
  onNavigateToSettings,
  showSuggestions, 
  isRefreshing, 
  onRefresh, 
  onCloseSuggestions, 
  showSortPopup, 
  onToggleSortPopup, 
  onSortSelect, 
  sortOption,
  currentProfileSet,
  onChatSelect
}: { 
  onNavigateToNotification: () => void; 
  onNavigateToSettings: () => void;
  showSuggestions: boolean; 
  isRefreshing: boolean; 
  onRefresh: () => void; 
  onCloseSuggestions: () => void; 
  showSortPopup: boolean; 
  onToggleSortPopup: () => void; 
  onSortSelect: (option: 'all' | 'unread' | 'archived') => void; 
  sortOption: string; 
  currentProfileSet: number;
  onChatSelect: (chatId: number) => void;
}) {
  return (
    <div className="absolute bg-white bottom-0 content-stretch flex flex-col items-center justify-start left-1 overflow-clip right-[5px] top-0" data-name="Screen">
      <UpperBar onNavigateToNotification={onNavigateToNotification} onNavigateToSettings={onNavigateToSettings} />
      <MainContent 
        showSuggestions={showSuggestions} 
        isRefreshing={isRefreshing} 
        onRefresh={onRefresh} 
        onCloseSuggestions={onCloseSuggestions} 
        showSortPopup={showSortPopup} 
        onToggleSortPopup={onToggleSortPopup} 
        onSortSelect={onSortSelect} 
        sortOption={sortOption} 
        currentProfileSet={currentProfileSet}
        onChatSelect={onChatSelect}
      />
      <div className="bg-neutral-50 h-[121px] relative shrink-0 w-[393px]" data-name="nevigation bar">
        <div className="h-[121px] overflow-clip relative w-[393px]">
          <div className="absolute content-stretch flex gap-[105px] items-center justify-start left-[13px] top-[32.5px]">
            <div className="content-stretch flex items-center justify-center relative shrink-0">
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative rounded-[16px] shrink-0 w-[65.2px]" data-name="Depth 3, Frame 0">
                <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0" data-name="Depth 5, Frame 0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
                          <div className="absolute inset-[9.38%_12.5%_12.5%_12.5%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 19">
                              <path clipRule="evenodd" d={svgPaths.p11f24e80} fill="var(--fill-0, #616C78)" fillRule="evenodd" id="Vector - 0" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]" data-name="Depth 3, Frame 1">
                <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="relative shrink-0 size-6" data-name="mingcute:search-ai-line">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border overflow-clip relative size-6">
                        <div className="absolute inset-[4.17%_4.17%_11.98%_8.34%]" data-name="Group">
                          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 21 21">
                            <g id="Group">
                              <path clipRule="evenodd" d={svgPaths.p11caffd0} fill="var(--fill-0, #616C78)" fillRule="evenodd" id="Vector" />
                            </g>
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="content-stretch flex items-center justify-center relative shrink-0">
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]" data-name="Depth 3, Frame 3">
                <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0" data-name="Depth 5, Frame 0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
                          <div className="absolute inset-[9.39%_9.38%_9.37%_9.37%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                              <path clipRule="evenodd" d={svgPaths.p19a90780} fill="var(--fill-0, #0055F7)" fillRule="evenodd" id="Vector - 0" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]" data-name="Depth 3, Frame 4">
                <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0" data-name="Depth 5, Frame 0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
                          <div className="absolute inset-[9.36%_9.34%_12.43%_9.34%]" style={{ "--fill-0": "rgba(97, 108, 120, 1)" } as React.CSSProperties}>
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                              <path clipRule="evenodd" d={svgPaths.p3d54cd00} fill="var(--fill-0, #616C78)" fillRule="evenodd" id="Vector - 0" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px]" data-name="!!<IconButton>">
            <div className="basis-0 content-stretch flex grow items-center justify-center min-h-px min-w-px relative shrink-0 w-full" data-name="<Icon>">
              <div className="aspect-[24/24] basis-0 grow min-h-px min-w-px relative shrink-0" data-name="mingcute:add-fill">
                <div className="absolute contents inset-[10.417%]" data-name="Group">
                  <div className="absolute inset-[10.417%]" data-name="Vector">
                    <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 23 23">
                      <path d={svgPaths.p3b63e500} fill="var(--fill-0, white)" id="Vector" stroke="var(--stroke-0, white)" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div aria-hidden="true" className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none" />
      </div>
    </div>
  );
}

export default function ChatHome({ onNavigateToNotification, onNavigateToSettings, onChatSelect }: ChatHomeProps) {
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showSortPopup, setShowSortPopup] = useState(false);
  const [sortOption, setSortOption] = useState('all');
  const [currentProfileSet, setCurrentProfileSet] = useState(0);

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Change to next profile set
    setCurrentProfileSet(prev => (prev + 1) % allProfileData.length);
    
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };

  const handleCloseSuggestions = () => {
    setShowSuggestions(false);
  };

  const handleToggleSortPopup = () => {
    setShowSortPopup(prev => !prev);
  };

  const handleSortSelect = (option: 'all' | 'unread' | 'archived') => {
    setSortOption(option);
    setShowSortPopup(false);
  };

  return (
    <div className="relative size-full" data-name="chat-home">
      <Screen 
        onNavigateToNotification={onNavigateToNotification}
        onNavigateToSettings={onNavigateToSettings}
        showSuggestions={showSuggestions}
        isRefreshing={isRefreshing}
        onRefresh={handleRefresh}
        onCloseSuggestions={handleCloseSuggestions}
        showSortPopup={showSortPopup}
        onToggleSortPopup={handleToggleSortPopup}
        onSortSelect={handleSortSelect}
        sortOption={sortOption}
        currentProfileSet={currentProfileSet}
        onChatSelect={onChatSelect}
      />
    </div>
  );
}