import svgPaths from "./svg-kxghleytwc";
import { useState } from 'react';

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
        <p className="block leading-[normal]">Get to it !</p>
      </div>
      <div className="font-['Nunito:Bold',_sans-serif] relative shrink-0 text-[16px] text-nowrap">
        <p className="block leading-[normal] whitespace-pre">
          Send a greeting message to start chat now!
        </p>
      </div>
    </div>
  );
}

function Frame35() {
  return (
    <div className="bg-[#ffffff] box-border content-stretch flex flex-row gap-2.5 h-14 items-center justify-start pl-[22px] pr-0 py-0 relative rounded-[30px] shrink-0 w-[477px]">
      <div
        aria-hidden="true"
        className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[30px] shadow-[5px_4px_20px_0px_rgba(0,0,0,0.13)]"
      />
      <div className="font-['Nunito:Bold',_sans-serif] font-bold leading-[0] relative shrink-0 text-[#3369ff] text-[13px] text-left text-nowrap">
        <p className="block leading-[normal] whitespace-pre">{`Hi! 👋 I’m interested in your project! Would like to know more. `}</p>
      </div>
      <div
        className="absolute left-[439px] size-6 top-4"
        data-name="vuesax/bold/send"
      >
        <VuesaxBoldSend />
      </div>
    </div>
  );
}

function Frame13771() {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0">
      <Frame13770 />
      <Frame35 />
    </div>
  );
}

function StateLayer() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-center justify-center p-[11px] relative rounded-[100px] shrink-0"
      data-name="state-layer"
    >
      <div
        className="relative rounded-sm shrink-0 size-[18px]"
        data-name="container"
      >
        <div
          aria-hidden="true"
          className="absolute border-2 border-[#49454f] border-solid inset-0 pointer-events-none rounded-sm"
        />
      </div>
    </div>
  );
}

function Checkboxes() {
  return (
    <div
      className="box-border content-stretch flex flex-col items-center justify-center p-[4px] relative shrink-0"
      data-name="Checkboxes"
    >
      <StateLayer />
    </div>
  );
}

function Frame13772() {
  return (
    <div className="box-border content-stretch flex flex-row items-center justify-center p-0 relative shrink-0">
      <Checkboxes />
      <div className="font-['Nunito:Bold',_sans-serif] font-bold h-[38px] leading-[0] relative shrink-0 text-[#000000] text-[13px] text-left w-[148px]">
        <p className="block leading-[normal]">
          set as default greeting not displayed recently
        </p>
      </div>
    </div>
  );
}

function Frame13773() {
  return (
    <div className="box-border content-stretch flex flex-row gap-[147px] items-start justify-start p-0 relative shrink-0 w-[477px]">
      <Frame13772 />
      <div className="flex flex-col font-['Nunito:Bold',_sans-serif] font-bold h-12 justify-end leading-[0] relative shrink-0 text-[#b1bccd] text-[15px] text-left w-[134px]">
        <p className="[text-decoration-line:underline] [text-decoration-style:solid] [text-underline-position:from-font] block leading-[normal]">
          I’ll back to it later
        </p>
      </div>
    </div>
  );
}

function AutoLayout4() {
  return (
    <div
      className="absolute bg-[#ffffff] box-border content-stretch flex flex-col gap-[7px] h-[268px] items-start justify-start left-0 overflow-clip pb-12 pl-8 pr-0 pt-[22px] rounded-[48px] shadow-[0px_15px_28px_0px_rgba(171,178,187,0.25)] top-0 w-[548px]"
      data-name="Auto layout 4"
    >
      <Frame13771 />
      <Frame13773 />
    </div>
  );
}

export default function Frame13774({ onClose }: { onClose?: () => void }) {
  const [message, setMessage] = useState("Hi! 👋 I’m interested in your project! Would like to know more.");
  const [isChecked, setIsChecked] = useState(false);

  const handleSend = () => {
    alert("Message sent: " + message);
    if (onClose) onClose();
  };

  const handleBackLater = () => {
    alert("We'll remind you later!");
    if (onClose) onClose();
  };

  return (
    <div className="popup-frame">
      <div className="popup-emoji">🫵</div>
      <div style={{ width: '100%' }}>
        <div className="popup-title">Get to it !</div>
        <div className="popup-subtitle">Send a greeting message to start chat now!</div>
        <div className="popup-input-row">
          <input
            type="text"
            value={message}
            onChange={e => setMessage(e.target.value)}
            placeholder="Hi! 👋 I’m interested in your project! Would like to know more."
          />
          <button className="popup-send-btn" onClick={handleSend}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill="#3369FF" />
            </svg>
          </button>
        </div>
        <div className="popup-checkbox-row">
          <label className="popup-checkbox-label">
            <input
              type="checkbox"
              className="custom-checkbox"
              checked={isChecked}
              onChange={e => setIsChecked(e.target.checked)}
            />
            set as default greeting<br />not displayed recently
          </label>
          <span className="popup-later" onClick={handleBackLater} style={{ cursor: 'pointer' }}>
            I’ll back to it later
          </span>
        </div>
      </div>
    </div>
  );
}