import { useState, useEffect } from 'react';

interface ChatMessageProps {
  message: string;
  time: string;
  isOwn: boolean;
  isNew?: boolean;
  status?: 'sending' | 'sent' | 'read' | 'failed';
}

// 消息状态图标组件
function MessageStatusIcon({ status }: { status?: 'sending' | 'sent' | 'read' | 'failed' }) {
  if (!status || status === 'sending') {
    // 正在发送 - 旋转的加载图标
    return (
      <div className="relative shrink-0 size-3" data-name="sending">
        <div className="absolute inset-[16.67%_8.33%]">
          <svg className="block size-full animate-spin" fill="none" viewBox="0 0 12 12">
            <circle cx="6" cy="6" r="5" stroke="#8593A8" strokeWidth="1" fill="none" strokeDasharray="8 4" />
          </svg>
        </div>
      </div>
    );
  }

  if (status === 'sent') {
    // 已发送 - 单勾
    return (
      <div className="relative shrink-0 size-3" data-name="sent">
        <div className="absolute inset-[16.67%_8.33%]">
          <svg className="block size-full" fill="none" viewBox="0 0 12 12">
            <path d="M2 6l3 3 5-5" stroke="#8593A8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
      </div>
    );
  }

  if (status === 'read') {
    // 已读 - 双勾
    return (
      <div className="relative shrink-0 size-3" data-name="read">
        <div className="absolute inset-[16.67%_8.33%]">
          <svg className="block size-full" fill="none" viewBox="0 0 12 12">
            <path d="M2 6l3 3 5-5" stroke="#0055F7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M2 8l3 3 5-5" stroke="#0055F7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
      </div>
    );
  }

  if (status === 'failed') {
    // 发送失败 - 感叹号
    return (
      <div className="relative shrink-0 size-3" data-name="failed">
        <div className="absolute inset-[16.67%_8.33%]">
          <svg className="block size-full" fill="none" viewBox="0 0 12 12">
            <path d="M6 2v6M6 10h.01" stroke="#EF4444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
      </div>
    );
  }

  return null;
}

export default function ChatMessage({ message, time, isOwn, isNew = false, status }: ChatMessageProps) {
  const [isVisible, setIsVisible] = useState(!isNew);

  useEffect(() => {
    if (isNew) {
      // Trigger animation after component mounts
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isNew]);

  useEffect(() => {
    try {
      const scope = document.currentScript ? undefined : document;
      const root = scope as Document;
      const others = root.querySelectorAll('[data-chat-message-other]');
      const mine = root.querySelectorAll('[data-chat-message-own]');
      const times = root.querySelectorAll('[data-chat-message-time]');
      others.forEach((el) => {
        (el as HTMLElement).style.setProperty('color', '#000000', 'important');
        (el as HTMLElement).style.setProperty('font-size', '16px', 'important');
        (el as HTMLElement).style.setProperty('opacity', '1', 'important');
      });
      mine.forEach((el) => {
        (el as HTMLElement).style.setProperty('font-size', '16px', 'important');
        (el as HTMLElement).style.setProperty('opacity', '1', 'important');
      });
      times.forEach((el) => {
        (el as HTMLElement).style.setProperty('color', '#3d3d3d', 'important');
        (el as HTMLElement).style.setProperty('font-size', '9px', 'important');
        (el as HTMLElement).style.setProperty('opacity', '1', 'important');
      });
      const timeTexts = root.querySelectorAll('[data-chat-message-time-text]');
      timeTexts.forEach((p) => {
        (p as HTMLElement).style.setProperty('color', '#3d3d3d', 'important');
        (p as HTMLElement).style.setProperty('font-size', '9px', 'important');
        (p as HTMLElement).style.setProperty('opacity', '1', 'important');
        (p as HTMLElement).style.setProperty('line-height', '1.2', 'important');
      });
      const otherTexts = root.querySelectorAll('[data-chat-message-other-text]');
      const ownTexts = root.querySelectorAll('[data-chat-message-own-text]');
      otherTexts.forEach((p) => {
        (p as HTMLElement).style.setProperty('color', '#000000', 'important');
        (p as HTMLElement).style.setProperty('opacity', '1', 'important');
        (p as HTMLElement).style.setProperty('mix-blend-mode', 'normal', 'important');
        (p as HTMLElement).style.setProperty('filter', 'none', 'important');
        (p as HTMLElement).style.setProperty('font-size', '16px', 'important');
      });
      ownTexts.forEach((p) => {
        (p as HTMLElement).style.setProperty('opacity', '1', 'important');
        (p as HTMLElement).style.setProperty('mix-blend-mode', 'normal', 'important');
        (p as HTMLElement).style.setProperty('filter', 'none', 'important');
        (p as HTMLElement).style.setProperty('font-size', '16px', 'important');
      });
    } catch {}
  }, [isOwn, message, time]);

  if (isOwn) {
    return (
      <div 
        className={`
          content-stretch flex flex-col items-end justify-start relative shrink-0 w-[357px]
          transition-all duration-300 ease-out
          ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}
        `}
      >
        <div className="content-stretch flex items-end justify-end relative shrink-0">
          {/* 状态图标和气泡的组合容器 - 作为整体右对齐 */}
          <div className="flex items-end gap-1">
            {/* 消息状态图标 - 只在自己的消息上显示 */}
            <MessageStatusIcon status={status} />
            {/* 我方气泡：#0055F7背景，白色文字 - 添加最大宽度限制以支持自动换行 */}
            <div className="bg-[#0055f7] box-border flex gap-2.5 items-center justify-start overflow-clip p-[12px] relative rounded-bl-[30px] rounded-tl-[30px] rounded-tr-[30px]" style={{ maxWidth: 'calc(90vw - 80px)' }}>
              <div 
                className="font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] relative text-[16px] text-white" 
                style={{ fontVariationSettings: "'wdth' 100", wordBreak: 'break-word' }}
                data-chat-message-own
              >
                <p 
                  className="leading-[normal] whitespace-pre-wrap"
                  data-chat-message-own-text
                  style={{ wordBreak: 'break-word', overflowWrap: 'break-word' }}
                >
                  {message}
                </p>
              </div>
            </div>
          </div>
        </div>
        {/* 时间显示更小 */}
        <div className="box-border content-stretch flex gap-2.5 items-start justify-start overflow-clip px-[5px] py-0.5 relative rounded-bl-[8px] rounded-br-[8px] shrink-0">
          <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[#3d3d3d] text-[9px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }} data-chat-message-time>
            <p className="leading-[normal] whitespace-pre" data-chat-message-time-text>{time}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`
        content-stretch flex gap-3 items-center justify-center relative shrink-0 w-[357px]
        transition-all duration-300 ease-out
        ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}
      `}
    >
      <div className="basis-0 content-stretch flex flex-col grow items-start justify-start min-h-px min-w-px relative shrink-0">
        {/* 对方气泡：#ECEAF5背景，黑色文字 - 自适应宽度，限制最大宽度 */}
        <div className="relative shrink-0 inline-flex rounded-br-[30px] rounded-tl-[30px] rounded-tr-[30px] bg-[#eceaf5]" style={{ maxWidth: '90%' }}>
          <div className="flex flex-row items-center overflow-clip relative size-full">
            <div className="box-border content-stretch flex gap-2.5 items-center justify-start p-[12px] relative">
              <div 
                className="basis-0 font-['Instrument_Sans:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px relative shrink-0 text-[16px] text-black" 
                style={{ fontVariationSettings: "'wdth' 100" }}
                data-chat-message-other
              >
                <p className="leading-[normal] whitespace-pre-wrap" data-chat-message-other-text>{message}</p>
              </div>
            </div>
          </div>
        </div>
        {/* 时间显示更小 */}
        <div className="box-border content-stretch flex gap-2.5 items-start justify-start overflow-clip px-[5px] py-0.5 relative rounded-bl-[8px] rounded-br-[8px] shrink-0">
          <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[#3d3d3d] text-[9px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }} data-chat-message-time>
            <p className="leading-[normal] whitespace-pre" data-chat-message-time-text>{time}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
