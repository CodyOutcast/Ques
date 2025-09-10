import { useState, useEffect } from 'react';

interface ChatMessageProps {
  message: string;
  time: string;
  isOwn: boolean;
  isNew?: boolean;
}

function SolarEyeBroken() {
  return (
    <div className="relative shrink-0 size-3" data-name="solar:eye-broken">
      <div className="absolute inset-[16.67%_8.33%]" data-name="Group">
        <div className="absolute inset-[-6.25%_-5%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 10">
            <g id="Group">
              <path d="M6 1C3.79 1 1.89 2.38 1 4.5C1.89 6.62 3.79 8 6 8S10.11 6.62 11 4.5C10.11 2.38 8.21 1 6 1Z" stroke="var(--stroke-0, #8593A8)" strokeLinecap="round" />
              <path d="M6 6.5C7.38 6.5 8.5 5.38 8.5 4C8.5 2.62 7.38 1.5 6 1.5" stroke="var(--stroke-0, #8593A8)" />
            </g>
          </svg>
        </div>
      </div>
    </div>
  );
}

export default function ChatMessage({ message, time, isOwn, isNew = false }: ChatMessageProps) {
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

  if (isOwn) {
    return (
      <div 
        className={`
          content-stretch flex flex-col items-end justify-start relative shrink-0 w-[357px]
          transition-all duration-300 ease-out
          ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}
        `}
      >
        <div className="content-stretch flex items-end justify-start relative shrink-0">
          <SolarEyeBroken />
          <div className="bg-[#0055f7] box-border content-stretch flex gap-2.5 items-center justify-start overflow-clip p-[12px] relative rounded-bl-[30px] rounded-tl-[30px] rounded-tr-[30px] shrink-0">
            <div className="capitalize font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#f2f2f2] text-[12px]" style={{ fontVariationSettings: "'wdth' 100" }}>
              <p className="leading-[normal] whitespace-pre-wrap">{message}</p>
            </div>
          </div>
        </div>
        <div className="box-border content-stretch flex gap-2.5 items-start justify-start overflow-clip px-[5px] py-0.5 relative rounded-bl-[8px] rounded-br-[8px] shrink-0">
          <div className="capitalize font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[#3d3d3d] text-[7px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
            <p className="leading-[normal] whitespace-pre">{time}</p>
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
        <div className="bg-[#eceaf5] relative rounded-br-[30px] rounded-tl-[30px] rounded-tr-[30px] shrink-0 w-full">
          <div className="flex flex-row items-center overflow-clip relative size-full">
            <div className="box-border content-stretch flex gap-2.5 items-center justify-start p-[12px] relative w-full">
              <div className="basis-0 capitalize font-['Instrument_Sans:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px relative shrink-0 text-[#050607] text-[12px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[normal] whitespace-pre-wrap">{message}</p>
              </div>
            </div>
          </div>
        </div>
        <div className="box-border content-stretch flex gap-2.5 items-start justify-start overflow-clip px-[5px] py-0.5 relative rounded-bl-[8px] rounded-br-[8px] shrink-0">
          <div className="capitalize font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[#3d3d3d] text-[7px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
            <p className="leading-[normal] whitespace-pre">{time}</p>
          </div>
        </div>
      </div>
    </div>
  );
}