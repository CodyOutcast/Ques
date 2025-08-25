import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import svgPaths from "../imports/svg-mk78u70ng0";
import svgPathsPending from "../imports/svg-99vtvx8zq1";
import svgPathsState from "../imports/svg-r38v2gasp5";
// Placeholder avatar URL
const imgEllipse13 = "https://api.dicebear.com/7.x/avataaars/svg?seed=chatUser";

type MessageStatus = 'sending' | 'sent' | 'read' | 'failed';

interface Message {
  id: string;
  text: string;
  timestamp: string;
  isOwn: boolean;
  status?: MessageStatus;
}

interface ChatDetailProps {
  chatId: string;
  chatName: string;
  chatAvatar: string;
  isOnline: boolean;
  onBack: () => void;
}

const mockMessages: Message[] = [
  {
    id: '1',
    text: 'sed do eiusmod tempor incididunt ut labore et magna aliqua. Ut enim ad minim veniam,.',
    timestamp: '10:28',
    isOwn: false,
  },
  {
    id: '2',
    text: 'Lorem ipsum dolor sit',
    timestamp: '10:30',
    isOwn: true,
    status: 'read',
  },
  {
    id: '3',
    text: 'sed do eiusmod tempor incididunt ut labore et magna aliqua. Ut enim ad minim veniam,.',
    timestamp: '10:31',
    isOwn: false,
  },
  {
    id: '4',
    text: 'sed do eiusmod tempor incididunt ut labore et magna aliqua. Ut enim ad minim veniam,.',
    timestamp: '10:31',
    isOwn: false,
  },
  {
    id: '5',
    text: 'Lorem ipsum dolor sit',
    timestamp: '10:32',
    isOwn: true,
    status: 'read',
  },
  {
    id: '6',
    text: 'Lorem ipsum dolor sit aaaaaa ssss',
    timestamp: '10:30',
    isOwn: true,
    status: 'read',
  },
  {
    id: '7',
    text: 'sed do eiusmod tempor incididunt ut labore et magna',
    timestamp: '10:32',
    isOwn: false,
  },
  {
    id: '8',
    text: 'Here are some additional messages to test scrolling functionality.',
    timestamp: '10:33',
    isOwn: true,
    status: 'read',
  },
  {
    id: '9',
    text: 'This is another message to make sure the scroll works properly and we can see all messages.',
    timestamp: '10:34',
    isOwn: false,
  },
  {
    id: '10',
    text: 'Last message to test scrolling behavior.',
    timestamp: '10:35',
    isOwn: true,
    status: 'read',
  },
];

function MessageStatusIcon({ status }: { status: MessageStatus }) {
  switch (status) {
    case 'sending':
      return (
        <div className="relative shrink-0 size-3">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 12">
            <path d={svgPathsState.p2ebb4e80} fill="#8593A8" />
          </svg>
        </div>
      );
    case 'sent':
      return (
        <div className="relative shrink-0 size-3">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 12">
            <path d={svgPathsState.pabf9680} stroke="#8593A8" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.125" fill="none" />
          </svg>
        </div>
      );
    case 'read':
      return (
        <div className="relative shrink-0 size-3">
          <div className="absolute inset-[16.67%_8.33%]">
            <div className="absolute inset-[-6.25%_-5%]">
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 10">
                <g>
                  <path d={svgPathsState.p2b7dde60} stroke="#8593A8" strokeLinecap="round" />
                  <path d={svgPathsState.p75e9700} stroke="#8593A8" />
                </g>
              </svg>
            </div>
          </div>
        </div>
      );
    case 'failed':
      return (
        <div className="relative shrink-0 size-3">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 12">
            <path d="M10 10L2 2M10 2L2 10" stroke="#F44336" strokeLinecap="round" />
          </svg>
        </div>
      );
    default:
      return null;
  }
}

function MessageBubble({ message, onResend }: { message: Message; onResend?: (messageId: string) => void }) {
  if (message.isOwn) {
    return (
      <motion.div 
        initial={{ opacity: 0, x: 20, scale: 0.8 }}
        animate={{ opacity: 1, x: 0, scale: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="content-stretch flex flex-col items-end justify-start relative shrink-0 w-full"
      >
        <div className="content-stretch flex items-end justify-start relative shrink-0">
          <MessageStatusIcon status={message.status || 'sent'} />
          <div className="bg-[#0055f7] box-border content-stretch flex gap-2.5 items-center justify-start overflow-clip p-[12px] relative rounded-bl-[30px] rounded-tl-[30px] rounded-tr-[30px] shrink-0 max-w-[280px]">
            <div className="capitalize font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#f2f2f2] text-[12px]" style={{ fontVariationSettings: "'wdth' 100" }}>
              <p className="leading-[normal] whitespace-pre-wrap">{message.text}</p>
            </div>
          </div>
        </div>
        <div className="box-border content-stretch flex gap-2.5 items-start justify-start overflow-clip px-[5px] py-0.5 relative rounded-bl-[8px] rounded-br-[8px] shrink-0">
          {message.status === 'failed' && onResend && (
            <button 
              onClick={() => onResend(message.id)}
              className="font-['Instrument_Sans:Medium',_sans-serif] font-medium relative shrink-0 text-[#0055f7] text-[7px] text-nowrap leading-[0] hover:underline"
              style={{ fontVariationSettings: "'wdth' 100" }}
            >
              <p className="leading-[normal] text-nowrap whitespace-pre underline">Resend</p>
            </button>
          )}
          <div className="capitalize font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[#3d3d3d] text-[7px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
            <p className="leading-[normal] whitespace-pre">{message.timestamp}</p>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20, scale: 0.8 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="content-stretch flex gap-3 items-start justify-start relative shrink-0 w-full"
    >
      <div className="basis-0 content-stretch flex flex-col grow items-start justify-start min-h-px min-w-px relative shrink-0 max-w-[280px]">
        <div className="bg-[#eceaf5] relative rounded-br-[30px] rounded-tl-[30px] rounded-tr-[30px] shrink-0 w-full">
          <div className="flex flex-row items-center overflow-clip relative size-full">
            <div className="box-border content-stretch flex gap-2.5 items-center justify-start p-[12px] relative w-full">
              <div className="basis-0 capitalize font-['Instrument_Sans:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px relative shrink-0 text-[#050607] text-[12px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[normal]">{message.text}</p>
              </div>
            </div>
          </div>
        </div>
        <div className="box-border content-stretch flex gap-2.5 items-start justify-start overflow-clip px-[5px] py-0.5 relative rounded-bl-[8px] rounded-br-[8px] shrink-0">
          <div className="capitalize font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[#3d3d3d] text-[7px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
            <p className="leading-[normal] whitespace-pre">{message.timestamp}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ChatInput({ disabled, onSendMessage }: { 
  disabled: boolean; 
  onSendMessage: (message: string) => void;
}) {
  const [inputValue, setInputValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSend = () => {
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="absolute left-[23px] top-[686px] w-[347px] h-[46px]">
      <div 
        className={`relative w-full h-full bg-white rounded-[30px] border flex items-center px-[22px] gap-2 transition-all duration-200 ${
          isFocused && !disabled 
            ? 'border-[#3369FF] shadow-[0px_0px_0px_4px_rgba(51,105,255,0.1),0px_0px_20px_0px_rgba(0,0,0,0.13)] scale-[1.02]' 
            : disabled 
            ? 'border-[#e5e5ea] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.13)]' 
            : 'border-[#E8EDF2] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.13)]'
        }`}
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          placeholder={disabled ? "Waiting for reply..." : "This is a text..."}
          className={`flex-1 h-full bg-transparent border-none outline-none font-['Instrument_Sans:Regular',_sans-serif] font-normal text-[16px] ${
            disabled ? 'italic text-[#8e8e93] placeholder:text-[#8e8e93]' : isFocused ? 'text-[#0055f7] placeholder:text-[#0055f7]' : 'text-[#050607] placeholder:text-[#8593a8]'
          }`}
          style={{ fontVariationSettings: "'wdth' 100" }}
        />
        
        {/* Photo Button */}
        <button 
          type="button"
          className="w-6 h-6 flex items-center justify-center shrink-0 hover:scale-110 transition-transform"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24">
            <path d={svgPaths.p22924f00} fill="#616C78" />
          </svg>
        </button>
        
        {/* Send Button */}
        <button 
          type="button"
          onClick={handleSend}
          disabled={disabled || !inputValue.trim()}
          className={`w-6 h-6 flex items-center justify-center shrink-0 transition-all ${
            disabled || !inputValue.trim() ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:scale-110'
          }`}
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24">
            <path d={svgPaths.p3b62cd80} fill={disabled || !inputValue.trim() ? "#616C78" : "#3369FF"} />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default function ChatDetailPage({ chatId, chatName, chatAvatar, isOnline, onBack }: ChatDetailProps) {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [isWaitingForReply, setIsWaitingForReply] = useState(false);
  const [showOneMessageRule, setShowOneMessageRule] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check if we're waiting for a reply (last message is from user and no response yet)
    const lastMessage = messages[messages.length - 1];
    const hasUnrepliedMessage = lastMessage?.isOwn && messages.filter(m => m.isOwn && !messages.slice(messages.indexOf(m) + 1).some(reply => !reply.isOwn)).length > 0;
    setIsWaitingForReply(hasUnrepliedMessage);
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
      isOwn: true,
      status: 'sending'
    };

    setMessages(prev => [...prev, newMessage]);
    
    // Check if this is the first message the user sends to this contact
    const userMessageCount = messages.filter(m => m.isOwn).length;
    if (userMessageCount === 0) {
      setShowOneMessageRule(true);
      // Auto-hide after 5 seconds
      setTimeout(() => {
        setShowOneMessageRule(false);
      }, 5000);
    }
    
    // Simulate message status progression
    setTimeout(() => {
      setMessages(prev => prev.map(m => 
        m.id === newMessage.id ? { ...m, status: 'sent' } : m
      ));
    }, 1000);

    setTimeout(() => {
      setMessages(prev => prev.map(m => 
        m.id === newMessage.id ? { ...m, status: 'read' } : m
      ));
    }, 2000);
  };

  const handleResendMessage = (messageId: string) => {
    setMessages(prev => prev.map(m => 
      m.id === messageId ? { ...m, status: 'sending' } : m
    ));

    setTimeout(() => {
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { ...m, status: 'sent' } : m
      ));
    }, 1000);
  };

  return (
    <div className="bg-[#fcfcfd] flex flex-col gap-2 h-[844px] overflow-clip relative w-[393px]">
      {/* Upper Bar */}
      <div className="bg-neutral-50 h-[90px] relative shrink-0">
        <div className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative">
          <div className="box-border content-stretch flex h-[52px] items-end justify-between p-0 relative shrink-0 w-[355px]">
            <div className="box-border content-stretch flex gap-[3px] items-start justify-center leading-[0] px-0 py-[13px] relative shrink-0 text-nowrap">
              <div className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic relative shrink-0 text-[#0055f7] text-[40px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[9px] text-nowrap whitespace-pre">Ques</p>
              </div>
              <div className="css-r804ei flex flex-col font-['SF_Pro:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#0088ff] text-[18px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[18px] text-nowrap whitespace-pre">􀆏</p>
              </div>
            </div>
            <div className="box-border content-stretch flex items-center justify-start p-0 relative shrink-0 w-[81px]">
              <div className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0">
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
              <div className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0">
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
              </div>
            </div>
          </div>
        </div>
        <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
      </div>

      {/* Chat Header */}
      <div className="px-4 py-2">
        <div className="content-stretch flex gap-2.5 h-[52px] items-center justify-between relative shrink-0">
          <div className="content-stretch flex gap-2.5 items-center justify-start relative shrink-0">
            <button 
              onClick={onBack}
              className="relative shrink-0 size-6 cursor-pointer hover:opacity-70 transition-opacity"
            >
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
                <path d={svgPaths.p2a5cd480} stroke="#424F63" strokeLinecap="round" strokeLinejoin="round" strokeMiterlimit="10" strokeWidth="1.5" />
              </svg>
            </button>
            <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
              <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-10">
                <img className="block max-w-none size-full rounded-full" height="40" src={chatAvatar} width="40" />
              </div>
              {isOnline && (
                <div className="[grid-area:1_/_1] ml-[29px] mt-0 relative size-2">
                  <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 8 8">
                    <circle cx="4" cy="4" fill="#00CC5E" r="4" />
                  </svg>
                </div>
              )}
            </div>
            <div className="content-stretch flex flex-col items-start justify-start leading-[0] relative shrink-0 text-nowrap">
              <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold relative shrink-0 text-[#213241] text-[20px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[normal] text-nowrap whitespace-pre">{chatName}</p>
              </div>
              <div className={`font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[14px] ${
                isWaitingForReply ? 'text-[#0055f7] italic' : 'text-[#8593a8]'
              }`} style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[normal] text-nowrap whitespace-pre">
                  {isWaitingForReply ? 'Waiting for reply' : 'online'}
                </p>
              </div>
            </div>
          </div>
          <div className="relative shrink-0 size-6 cursor-pointer hover:opacity-70 transition-opacity">
            <div className="relative size-full">
              <div className="absolute inset-[41.67%_12.5%]">
                <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 4">
                  <path d={svgPaths.p11907800} fill="black" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area - Fixed height with scrolling */}
      <div className="flex-1 overflow-hidden relative">
        <div className="h-full overflow-y-auto px-4 pb-4" style={{ maxHeight: 'calc(844px - 90px - 68px - 121px - 46px - 20px)' }}>
          <div className="content-stretch flex flex-col gap-3 items-start justify-start relative shrink-0">
            <AnimatePresence>
              {messages.map((message) => (
                <MessageBubble 
                  key={message.id} 
                  message={message} 
                  onResend={handleResendMessage}
                />
              ))}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* One message rule indicator - Fixed position overlay */}
      <AnimatePresence>
        {showOneMessageRule && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-40 bg-white/95 backdrop-blur-sm rounded-lg px-6 py-4 shadow-lg border border-gray-200"
          >
            <div className="flex items-center gap-4">
              <div className="h-px bg-[#AEAEB2] flex-1 w-16" />
              <div className="flex flex-col font-['Instrument_Sans:Italic',_sans-serif] font-normal italic justify-center leading-[0] text-[#8e8e93] text-[12px] text-center" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[normal] whitespace-nowrap">You can only send 1 message before the other replies</p>
              </div>
              <div className="h-px bg-[#AEAEB2] flex-1 w-16" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation Bar */}
      <div className="bg-neutral-50 h-[121px] relative shrink-0">
        <div className="h-[121px] overflow-clip relative w-[393px]">
          <div className="absolute content-stretch flex gap-[105px] items-center justify-start left-[13px] top-[32.5px]">
            <div className="content-stretch flex items-center justify-center relative shrink-0">
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative rounded-2xl shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0">
                          <div className="absolute inset-[9.38%_12.5%_12.5%_12.5%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 19">
                              <path clipRule="evenodd" d={svgPaths.p11f24e80} fill="#616C78" fillRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="relative shrink-0 size-6">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border overflow-clip relative size-6">
                        <div className="absolute inset-[4.17%_4.17%_11.98%_8.34%]">
                          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 21 21">
                            <path clipRule="evenodd" d={svgPaths.p11caffd0} fill="#616C78" fillRule="evenodd" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="content-stretch flex items-center justify-center relative shrink-0">
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0">
                          <div className="absolute inset-[9.39%_9.38%_9.37%_9.37%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                              <path clipRule="evenodd" d={svgPaths.p19a90780} fill="#0055F7" fillRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0">
                          <div className="absolute inset-[9.36%_9.34%_12.43%_9.34%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                              <path clipRule="evenodd" d={svgPaths.p3d54cd00} fill="#616C78" fillRule="evenodd" />
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
          <div className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px] hover:scale-105 transition-transform cursor-pointer">
            <div className="basis-0 content-stretch flex grow items-center justify-center min-h-px min-w-px relative shrink-0 w-full">
              <div className="aspect-[24/24] basis-0 grow min-h-px min-w-px relative shrink-0">
                <div className="absolute contents inset-[10.417%]">
                  <div className="absolute inset-[10.417%]">
                    <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 23 23">
                      <path d={svgPaths.p3b63e500} fill="white" stroke="white" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div aria-hidden="true" className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none" />
      </div>

      {/* Chat Input */}
      <ChatInput 
        disabled={isWaitingForReply} 
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}