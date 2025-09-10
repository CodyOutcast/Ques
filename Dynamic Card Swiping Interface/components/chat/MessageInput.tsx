import { useState, useRef, useEffect } from 'react';
import svgIcons from './svg-icons';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  onUploadFiles?: (files: FileList) => void;
}

function IcRoundPhoto() {
  return (
    <div className="relative size-full" data-name="ic:round-photo">
      <div className="absolute inset-[12.5%]" data-name="Vector">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 18">
          <path d={svgIcons.photoIcon} fill="var(--fill-0, #616C78)" id="Vector" />
        </svg>
      </div>
    </div>
  );
}

function VuesaxBoldSend({ isActive }: { isActive: boolean }) {
  return (
    <div className="absolute contents inset-0" data-name="vuesax/bold/send">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="send">
          <path 
            d={svgIcons.sendIcon} 
            fill={isActive ? "var(--fill-0, #3369FF)" : "var(--fill-0, #616C78)"} 
            id="Vector" 
            className="transition-colors duration-200"
          />
          <g id="Vector_2" opacity="0"></g>
        </g>
      </svg>
    </div>
  );
}

function VuesaxBoldSend1({ isActive, onClick }: { isActive: boolean; onClick: () => void }) {
  return (
    <div 
      className="relative shrink-0 size-6 cursor-pointer hover:scale-110 transition-transform duration-200" 
      data-name="vuesax/bold/send"
      onClick={onClick}
    >
      <VuesaxBoldSend isActive={isActive} />
    </div>
  );
}

export default function MessageInput({ onSendMessage, onUploadFiles }: MessageInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (inputValue.trim() && !isSending) {
      setIsSending(true);
      
      // Send message animation
      const sendMessage = inputValue.trim();
      setInputValue('');
      
      // Call the parent's send message handler
      onSendMessage(sendMessage);
      
      // Reset sending state after animation
      setTimeout(() => {
        setIsSending(false);
        setIsFocused(false);
      }, 300);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    if (!inputValue.trim()) {
      setIsFocused(false);
    }
  };

  const handlePickFiles = () => {
    try { fileRef.current?.click(); } catch {}
  };

  const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onUploadFiles && onUploadFiles(files);
      // reset value so selecting the same file again still triggers change
      e.currentTarget.value = '';
    }
  };

  const isActive = isFocused || inputValue.trim().length > 0;
  const borderColor = isActive ? '#0088ff' : '#e5e5ea';

  return (
    <div className="bg-white relative rounded-[30px] size-full">
      <div 
        aria-hidden="true" 
        className="absolute border border-solid inset-0 pointer-events-none rounded-[30px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.13)] transition-colors duration-200" 
        style={{ borderColor }}
      />
      <div className="flex flex-row items-center justify-center relative size-full h-[46px]">
        <div className="box-border content-stretch flex gap-2 items-center justify-start pl-[22px] pr-4 py-0 relative w-full h-full">
          <div className="relative shrink-0 flex-1 flex items-center h-full">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onFocus={handleFocus}
              onBlur={handleBlur}
              onKeyPress={handleKeyPress}
              placeholder="Click to text..."
              className={`
                w-full h-full bg-transparent border-none outline-none resize-none
                font-['Instrument_Sans'] text-[16px] leading-[normal]
                transition-colors duration-200 flex items-center
                ${isActive 
                  ? 'text-[#050607] font-normal placeholder:text-transparent' 
                  : 'text-[#8e8e93] font-normal italic placeholder:text-[#8e8e93] placeholder:italic'
                }
              `}
              style={{ 
                fontVariationSettings: "'wdth' 100",
                fontFamily: "'Instrument Sans', sans-serif"
              }}
              disabled={isSending}
            />
            {isSending && (
              <div className="absolute left-0 flex items-center">
                <div className="w-2 h-2 bg-[#0088ff] rounded-full animate-pulse"></div>
              </div>
            )}
          </div>
          {/* Hidden file input for media upload */}
          <input
            ref={fileRef}
            type="file"
            accept="image/*,video/*"
            multiple
            className="hidden"
            onChange={handleFilesChange}
          />
          <div className="relative shrink-0 size-6 flex items-center justify-center cursor-pointer" data-name="ic:round-photo" onClick={handlePickFiles}>
            <IcRoundPhoto />
          </div>
          <div className="flex items-center justify-center">
            <VuesaxBoldSend1 isActive={isActive} onClick={handleSend} />
          </div>
        </div>
      </div>
    </div>
  );
} 