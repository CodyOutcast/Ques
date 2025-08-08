import svgPaths from "./svg-e200e4shba";

function Time() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#000000] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery() {
  return (
    <div
      className="h-[13px] relative shrink-0 w-[27.328px]"
      data-name="Battery"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 28 13"
      >
        <g id="Battery">
          <rect
            height="12"
            id="Border"
            opacity="0.35"
            rx="3.8"
            stroke="var(--stroke-0, black)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, black)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, black)"
            height="9"
            id="Capacity"
            rx="2.5"
            width="21"
            x="2"
            y="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Levels() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-[7px] grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-px px-0 relative shrink-0"
      data-name="Levels"
    >
      <div
        className="h-[12.226px] relative shrink-0 w-[19.2px]"
        data-name="Cellular Connection"
      >
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          role="presentation"
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, black)"
            fillRule="evenodd"
            id="Cellular Connection"
          />
        </svg>
      </div>
      <div
        className="h-[12.328px] relative shrink-0 w-[17.142px]"
        data-name="Wifi"
      >
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          role="presentation"
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, black)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery />
    </div>
  );
}

function StatusBarIPhone() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-row gap-[154px] h-[47px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 top-0 w-[402px]"
      data-name="Status bar - iPhone"
    >
      <Time />
      <Levels />
    </div>
  );
}

function HomeIndicator() {
  return (
    <div
      className="absolute bottom-0 h-[34px] left-1 right-[5px]"
      data-name="Home Indicator"
    >
      <div
        className="absolute bottom-2 flex h-[5px] items-center justify-center translate-x-[-50%] w-36"
        style={{ left: "calc(50% + 0.5px)" }}
      >
        <div className="flex-none rotate-[180deg] scale-y-[-100%]">
          <div
            className="bg-[#000000] h-[5px] rounded-[100px] w-36"
            data-name="Home Indicator"
          />
        </div>
      </div>
    </div>
  );
}

export default function LuanchingPage() {
  return (
    <div className="bg-[#ffffff] relative size-full" data-name="luanching page">
      <div
        className="absolute flex flex-col font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold h-[75px] italic justify-center leading-[0] left-[200.5px] text-[#0055f7] text-[128px] text-center top-[333.5px] tracking-[-2px] translate-x-[-50%] translate-y-[-50%] w-[349px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[95px]">Ques</p>
      </div>
      <StatusBarIPhone />
      <HomeIndicator />
      <div className="absolute bottom-[42.91%] font-['Rubik:Bold',_sans-serif] font-bold leading-[normal] left-[14.93%] right-[32.59%] text-[#0055f7] text-[24px] text-left top-[47.48%]">
        <p className="block mb-0">Match.</p>
        <p className="block mb-0">Connect.</p>
        <p className="block">Collab.</p>
      </div>
    </div>
  );
}