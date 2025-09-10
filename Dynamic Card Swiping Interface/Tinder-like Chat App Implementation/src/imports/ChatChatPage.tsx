import { useState } from 'react';
import svgPaths from "./svg-dxfe5vox50";
import imgEllipse13 from "figma:asset/46c20c2258069168b0b8a15107fe8ee99adab0be.png";
import MessageInput from '../components/MessageInput';
import ChatMessage from '../components/ChatMessage';

interface ChatChatPageProps {
  onNavigateBack: () => void;
}

interface Message {
  id: number;
  text: string;
  time: string;
  isOwn: boolean;
  isNew?: boolean;
}

// Initial messages data
const initialMessages: Message[] = [
  {
    id: 1,
    text: "sed do eiusmod tempor incididunt ut labore et magna aliqua. Ut enim ad minim veniam,.",
    time: "10:28",
    isOwn: false
  },
  {
    id: 2,
    text: "Lorem ipsum dolor sit",
    time: "10:30",
    isOwn: true
  },
  {
    id: 3,
    text: "sed do eiusmod tempor incididunt ut labore et magna aliqua. Ut enim ad minim veniam,.",
    time: "10:31",
    isOwn: false
  },
  {
    id: 4,
    text: "sed do eiusmod tempor incididunt ut labore et magna aliqua. Ut enim ad minim veniam,.",
    time: "10:31",
    isOwn: false
  },
  {
    id: 5,
    text: "Lorem ipsum dolor sit",
    time: "10:30",
    isOwn: true
  },
  {
    id: 6,
    text: "Lorem ipsum dolor sit aaaaaa ssss",
    time: "10:30",
    isOwn: true
  },
  {
    id: 7,
    text: "sed do eiusmod tempor incididunt ut labore et magna",
    time: "10:32",
    isOwn: false
  }
];

function RiMoreFill() {
  return (
    <div className="relative size-full" data-name="ri:more-fill">
      <div className="absolute inset-[41.67%_12.5%]" data-name="Vector">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 4">
          <path d={svgPaths.p11907800} fill="var(--fill-0, black)" id="Vector" />
        </svg>
      </div>
    </div>
  );
}

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

function IconButton1() {
  return (
    <div className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0" data-name="!!<IconButton>">
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

function IconButton2() {
  return (
    <div className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0" data-name="!!<IconButton>">
      <Icon5 />
    </div>
  );
}

function Frame19() {
  return (
    <div className="content-stretch flex items-center justify-start relative shrink-0 w-[120px]">
      <IconButton />
      <IconButton1 />
      <IconButton2 />
    </div>
  );
}

function Frame16() {
  return (
    <div className="content-stretch flex h-[52px] items-end justify-between relative shrink-0 w-[355px]">
      <PopupButton />
      <Frame19 />
    </div>
  );
}

function UpperBar() {
  return (
    <div className="bg-neutral-50 h-[90px] relative shrink-0" data-name="upper bar">
      <div className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative">
        <Frame16 />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function VuesaxLinearArrowLeft({ onClick }: { onClick?: () => void }) {
  return (
    <div className="absolute contents inset-0 cursor-pointer" data-name="vuesax/linear/arrow-left" onClick={onClick}>
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="arrow-left">
          <path d={svgPaths.p2a5cd480} id="Vector" stroke="var(--stroke-0, #424F63)" strokeLinecap="round" strokeLinejoin="round" strokeMiterlimit="10" strokeWidth="1.5" />
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
        <img className="block max-w-none size-full" height="40" src={imgEllipse13} width="40" />
      </div>
      <div className="[grid-area:1_/_1] ml-[29px] mt-0 relative size-2">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 8 8">
          <circle cx="4" cy="4" fill="var(--fill-0, #00CC5E)" id="Ellipse 14" r="4" />
        </svg>
      </div>
    </div>
  );
}

function Frame60() {
  return (
    <div className="content-stretch flex flex-col items-start justify-start leading-[0] relative shrink-0 text-nowrap">
      <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold relative shrink-0 text-[#213241] text-[20px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] text-nowrap whitespace-pre">kevin.eth</p>
      </div>
      <div className="font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[#8593a8] text-[14px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] text-nowrap whitespace-pre">typing...</p>
      </div>
    </div>
  );
}

function Frame61({ onNavigateBack }: { onNavigateBack: () => void }) {
  return (
    <div className="content-stretch flex gap-2.5 items-center justify-start relative shrink-0 w-[185px]">
      <VuesaxLinearArrowLeft1 onClick={onNavigateBack} />
      <Group8 />
      <Frame60 />
    </div>
  );
}

function Frame62({ onNavigateBack }: { onNavigateBack: () => void }) {
  return (
    <div className="content-stretch flex gap-[139px] h-[52px] items-center justify-start relative shrink-0">
      <Frame61 onNavigateBack={onNavigateBack} />
      <div className="relative shrink-0 size-6" data-name="ri:more-fill">
        <RiMoreFill />
      </div>
    </div>
  );
}

function Frame247({ messages }: { messages: Message[] }) {
  return (
    <div className="content-stretch flex flex-col gap-2 items-start justify-start relative shrink-0 max-h-[500px] overflow-y-auto">
      {messages.map((message) => (
        <ChatMessage
          key={message.id}
          message={message.text}
          time={message.time}
          isOwn={message.isOwn}
          isNew={message.isNew}
        />
      ))}
    </div>
  );
}

function Frame14({ onNavigateBack, messages }: { onNavigateBack: () => void; messages: Message[] }) {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-4 h-[663px] items-center justify-start left-[7px] pb-0 pt-[11px] px-0 top-0 w-[379px]">
      <Frame62 onNavigateBack={onNavigateBack} />
      <Frame247 messages={messages} />
    </div>
  );
}

function MainContent({ onNavigateBack, messages }: { onNavigateBack: () => void; messages: Message[] }) {
  return (
    <div className="h-[663px] overflow-clip relative shrink-0 w-[393px]" data-name="main content">
      <Frame14 onNavigateBack={onNavigateBack} messages={messages} />
    </div>
  );
}

function Depth5Frame0() {
  return (
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
  );
}

function Depth4Frame0() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
        <Depth5Frame0 />
      </div>
    </div>
  );
}

function Depth3Frame0() {
  return (
    <div className="content-stretch flex flex-col gap-1 items-center justify-end relative rounded-[16px] shrink-0 w-[65.2px]" data-name="Depth 3, Frame 0">
      <Depth4Frame0 />
    </div>
  );
}

function Group4() {
  return (
    <div className="absolute inset-[4.17%_4.17%_11.98%_8.34%]" data-name="Group">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 21 21">
        <g id="Group">
          <path clipRule="evenodd" d={svgPaths.p11caffd0} fill="var(--fill-0, #616C78)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function MingcuteSearchAiLine() {
  return (
    <div className="relative shrink-0 size-6" data-name="mingcute:search-ai-line">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border overflow-clip relative size-6">
        <Group4 />
      </div>
    </div>
  );
}

function Depth4Frame1() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
        <MingcuteSearchAiLine />
      </div>
    </div>
  );
}

function Depth3Frame1() {
  return (
    <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]" data-name="Depth 3, Frame 1">
      <Depth4Frame1 />
    </div>
  );
}

function Frame4() {
  return (
    <div className="content-stretch flex items-center justify-center relative shrink-0">
      <Depth3Frame0 />
      <Depth3Frame1 />
    </div>
  );
}

function Depth5Frame1() {
  return (
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
  );
}

function Depth4Frame2() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
        <Depth5Frame1 />
      </div>
    </div>
  );
}

function Depth3Frame3() {
  return (
    <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]" data-name="Depth 3, Frame 3">
      <Depth4Frame2 />
    </div>
  );
}

function Depth5Frame2() {
  return (
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
  );
}

function Depth4Frame3() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
        <Depth5Frame2 />
      </div>
    </div>
  );
}

function Depth3Frame4() {
  return (
    <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]" data-name="Depth 3, Frame 4">
      <Depth4Frame3 />
    </div>
  );
}

function Frame5() {
  return (
    <div className="content-stretch flex items-center justify-center relative shrink-0">
      <Depth3Frame3 />
      <Depth3Frame4 />
    </div>
  );
}

function Frame6() {
  return (
    <div className="absolute content-stretch flex gap-[105px] items-center justify-start left-[13px] top-[32.5px]">
      <Frame4 />
      <Frame5 />
    </div>
  );
}

function Group5() {
  return (
    <div className="absolute contents inset-[10.417%]" data-name="Group">
      <div className="absolute inset-[10.417%]" data-name="Vector">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 23 23">
          <path d={svgPaths.p3b63e500} fill="var(--fill-0, white)" id="Vector" stroke="var(--stroke-0, white)" />
        </svg>
      </div>
    </div>
  );
}

function MingcuteAddFill() {
  return (
    <div className="aspect-[24/24] basis-0 grow min-h-px min-w-px relative shrink-0" data-name="mingcute:add-fill">
      <Group5 />
    </div>
  );
}

function Icon6() {
  return (
    <div className="basis-0 content-stretch flex grow items-center justify-center min-h-px min-w-px relative shrink-0 w-full" data-name="<Icon>">
      <MingcuteAddFill />
    </div>
  );
}

function IconButton3() {
  return (
    <div className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px]" data-name="!!<IconButton>">
      <Icon6 />
    </div>
  );
}

function NevigationBar() {
  return (
    <div className="bg-neutral-50 h-[121px] relative shrink-0 w-[393px]" data-name="nevigation bar">
      <div className="h-[121px] overflow-clip relative w-[393px]">
        <Frame6 />
        <IconButton3 />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function Screen({ onNavigateBack, messages }: { onNavigateBack: () => void; messages: Message[] }) {
  return (
    <div className="absolute bg-white bottom-0 content-stretch flex flex-col items-center justify-start left-1 overflow-clip right-[5px] top-0" data-name="Screen">
      <UpperBar />
      <MainContent onNavigateBack={onNavigateBack} messages={messages} />
      <NevigationBar />
    </div>
  );
}

export default function ChatChatPage({ onNavigateBack }: ChatChatPageProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);

  const getCurrentTime = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const period = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
  };

  const handleSendMessage = (messageText: string) => {
    const newMessage: Message = {
      id: messages.length + 1,
      text: messageText,
      time: getCurrentTime(),
      isOwn: true,
      isNew: true
    };

    setMessages(prev => [...prev, newMessage]);

    // Simulate receiving a response after a delay
    setTimeout(() => {
      const responseMessage: Message = {
        id: messages.length + 2,
        text: "Thanks for your message! I'll get back to you soon.",
        time: getCurrentTime(),
        isOwn: false,
        isNew: true
      };
      setMessages(prev => [...prev, responseMessage]);
    }, 2000);
  };

  return (
    <div className="relative size-full" data-name="chat-chat page">
      <Screen onNavigateBack={onNavigateBack} messages={messages} />
      <div className="absolute bg-white box-border content-stretch h-[46px] left-[27px] rounded-[30px] top-[686px] w-[347px]">
        <MessageInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
}