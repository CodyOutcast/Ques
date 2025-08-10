import { useState } from "react";
import svgPaths from "../imports/svg-kxghleytwc";
import Frame13774 from '../imports/Frame13774';

function VuesaxBoldSend() {
  return (
    <div className="relative size-full" data-name="vuesax/bold/send">
      <div className="absolute contents inset-0" data-name="vuesax/bold/send">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 24 24"
        >
          <g id="send">
            <path
              d={svgPaths.p3b62cd80}
              fill="var(--fill-0, #3369FF)"
              id="Vector"
            />
            <g id="Vector_2" opacity="0"></g>
          </g>
        </svg>
      </div>
    </div>
  );
}

function Frame13770() {
  return (
    <div className="box-border content-stretch flex flex-col font-bold gap-1 items-start justify-center leading-[0] p-0 relative shrink-0 text-[#2a2f3f] text-left">
      <div className="font-['Nunito:Bold_Italic',_sans-serif] h-[78px] italic relative shrink-0 text-[72px] w-[311px]">
        <p className="block leading-[normal]">开始行动！</p>
      </div>
      <div className="font-['Nunito:Bold',_sans-serif] relative shrink-0 text-[16px] text-nowrap">
        <p className="block leading-[normal] whitespace-pre">
          发送打招呼消息，开启聊天！
        </p>
      </div>
    </div>
  );
}

interface Frame35Props {
  message: string;
  onMessageChange: (message: string) => void;
  onSend: () => void;
}

function Frame35({ message, onMessageChange, onSend }: Frame35Props) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="bg-[#ffffff] box-border content-stretch flex flex-row gap-2.5 h-14 items-center justify-start pl-[22px] pr-0 py-0 relative rounded-[30px] shrink-0 w-[477px]">
      <div
        aria-hidden="true"
        className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[30px] shadow-[5px_4px_20px_0px_rgba(0,0,0,0.13)]"
      />
      <input
        type="text"
        value={message}
        onChange={(e) => onMessageChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            onSend();
          }
        }}
        className="bg-transparent border-none outline-none flex-1 font-['Nunito:Bold',_sans-serif] font-bold leading-[0] text-[#3369ff] text-[13px] text-left placeholder:text-[#3369ff]/60"
        placeholder="嗨！👋 我对你的项目很感兴趣，想进一步了解。"
        style={{ fontSize: '13px', lineHeight: 'normal' }}
      />
      <button
        onClick={onSend}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`absolute left-[439px] size-6 top-4 cursor-pointer transition-all duration-200 ${
          isHovered 
            ? 'scale-125 drop-shadow-md' 
            : 'scale-100 hover:scale-110'
        }`}
        data-name="vuesax/bold/send"
      >
        <div className={`transition-all duration-200 ${isHovered ? 'brightness-110' : ''}`}>
          <VuesaxBoldSend />
        </div>
      </button>
    </div>
  );
}

interface Frame13771Props {
  message: string;
  onMessageChange: (message: string) => void;
  onSend: () => void;
}

function Frame13771({ message, onMessageChange, onSend }: Frame13771Props) {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0">
      <Frame13770 />
      <Frame35 message={message} onMessageChange={onMessageChange} onSend={onSend} />
    </div>
  );
}

interface StateLayerProps {
  isChecked: boolean;
  onToggle: () => void;
}

function StateLayer({ isChecked, onToggle }: StateLayerProps) {
  return (
    <div
      className="box-border content-stretch flex flex-row items-center justify-center p-[11px] relative rounded-[100px] shrink-0 cursor-pointer hover:bg-gray-50 transition-colors"
      data-name="state-layer"
      onClick={onToggle}
    >
      <div
        className="relative rounded-sm shrink-0 size-[18px] flex items-center justify-center"
        data-name="container"
      >
        <div
          aria-hidden="true"
          className={`absolute border-2 border-solid inset-0 pointer-events-none rounded-sm transition-all duration-200 ${
            isChecked ? 'border-[#3369ff] bg-[#3369ff]' : 'border-[#49454f] bg-transparent'
          }`}
        />
        {isChecked && (
          <svg
            className="text-white z-10 relative"
            width="12"
            height="9"
            viewBox="0 0 12 9"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M1 4.5L4.5 8L11 1"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </div>
    </div>
  );
}

interface CheckboxesProps {
  isChecked: boolean;
  onToggle: () => void;
}

function Checkboxes({ isChecked, onToggle }: CheckboxesProps) {
  return (
    <div
      className="box-border content-stretch flex flex-col items-center justify-center p-[4px] relative shrink-0"
      data-name="Checkboxes"
    >
      <StateLayer isChecked={isChecked} onToggle={onToggle} />
    </div>
  );
}

interface Frame13772Props {
  isChecked: boolean;
  onToggle: () => void;
}

function Frame13772({ isChecked, onToggle }: Frame13772Props) {
  return (
    <div className="box-border content-stretch flex flex-row items-center justify-center p-0 relative shrink-0">
      <Checkboxes isChecked={isChecked} onToggle={onToggle} />
      <div className="font-['Nunito:Bold',_sans-serif] font-bold h-[38px] leading-[0] relative shrink-0 text-[#000000] text-[13px] text-left w-[148px]">
        <p className="block leading-[normal]">设为默认开场白</p>
      </div>
    </div>
  );
}

interface Frame13773Props {
  isChecked: boolean;
  onToggle: () => void;
  onBackLater: () => void;
}

function Frame13773({ isChecked, onToggle, onBackLater }: Frame13773Props) {
  return (
    <div className="box-border content-stretch flex flex-row gap-[147px] items-start justify-start p-0 relative shrink-0 w-[477px]">
      <Frame13772 isChecked={isChecked} onToggle={onToggle} />
      <div className="flex flex-col font-['Nunito:Bold',_sans-serif] font-bold h-12 justify-end leading-[0] relative shrink-0 text-[#b1bccd] text-[15px] text-left w-[134px]">
        <button
          onClick={onBackLater}
          className="[text-decoration-line:underline] [text-decoration-style:solid] [text-underline-position:from-font] block leading-[normal] cursor-pointer hover:text-[#8a9bb3] transition-colors text-left"
        >
          稍后再说
        </button>
      </div>
    </div>
  );
}

interface AutoLayout4Props {
  message: string;
  onMessageChange: (message: string) => void;
  onSend: () => void;
  isChecked: boolean;
  onToggle: () => void;
  onBackLater: () => void;
}

function AutoLayout4({ message, onMessageChange, onSend, isChecked, onToggle, onBackLater }: AutoLayout4Props) {
  return (
    <div
      className="absolute bg-[#ffffff] box-border content-stretch flex flex-col gap-[7px] h-[268px] items-start justify-start left-0 overflow-clip pb-12 pl-8 pr-0 pt-[22px] rounded-[48px] shadow-[0px_15px_28px_0px_rgba(171,178,187,0.25)] top-0 w-[548px]"
      data-name="Auto layout 4"
    >
      <Frame13771 message={message} onMessageChange={onMessageChange} onSend={onSend} />
      <Frame13773 isChecked={isChecked} onToggle={onToggle} onBackLater={onBackLater} />
    </div>
  );
}

interface InteractivePopupProps {
  onClose?: () => void;
  defaultChecked?: boolean;
  onDefaultChange?: (checked: boolean) => void;
}

export default function InteractivePopup({ onClose, defaultChecked = false, onDefaultChange }: InteractivePopupProps) {
  const [message, setMessage] = useState("嗨！👋 我对你的项目很感兴趣，想进一步了解。");
  const [isChecked, setIsChecked] = useState(!!defaultChecked);

  const handleSend = () => {
    if (onClose) onClose();
  };

  const handleBackLater = () => {
    if (onClose) onClose();
  };

  const handleToggle = () => {
    const next = !isChecked;
    setIsChecked(next);
    onDefaultChange?.(next);
  };

  return (
    <div className="popup-frame">
      <div className="popup-inner">
        <div className="popup-title">开始行动！</div>
        <div className="popup-subtitle">发送打招呼消息，开启聊天！</div>
        
        <div className="popup-input-row">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="嗨！👋 我对你的项目很感兴趣，想进一步了解。"
          />
          <button className="popup-send-btn" onClick={handleSend}>
            <VuesaxBoldSend />
          </button>
          </div>
        
        <div className="popup-checkbox-row" style={{ alignItems: 'flex-end' }}>
          <label className="popup-checkbox-label" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              type="checkbox"
              className="custom-checkbox"
              checked={isChecked}
              onChange={handleToggle}
            />
            <span>设为默认开场白</span>
          </label>
          <button className="popup-later" onClick={handleBackLater}>
            稍后再说
          </button>
        </div>
      </div>
      <div className="popup-emoji" aria-hidden>🫵</div>
    </div>
  );
}