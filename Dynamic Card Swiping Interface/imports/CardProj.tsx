import svgPaths from "./svg-fko3i96u3r";

function PopupButton() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-[3px] items-start justify-center leading-[0] px-0 py-[13px] relative shrink-0 text-left text-nowrap"
      data-name="Popup Button"
    >
      <div
        className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic relative shrink-0 text-[#0055f7] text-[40px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[9px] text-nowrap whitespace-pre">Ques</p>
      </div>
      <div
        className="css-r804ei flex flex-col font-['SF_Pro:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#0088ff] text-[18px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[18px] text-nowrap whitespace-pre">􀆏</p>
      </div>
    </div>
  );
}

function Icon() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <g id="Vector">
            <path d={svgPaths.p3742bc80} fill="var(--fill-0, white)" />
            <path
              d={svgPaths.p1f60aa80}
              stroke="var(--stroke-0, black)"
              strokeLinecap="round"
              strokeMiterlimit="10"
              strokeWidth="1.5"
            />
          </g>
        </g>
      </svg>
    </div>
  );
}

function Icon1() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon />
    </div>
  );
}

function IconButton() {
  return (
    <div
      className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0"
      data-name="!!<IconButton>"
    >
      <Icon1 />
    </div>
  );
}

function Frame15() {
  return (
    <div className="box-border content-stretch flex flex-row items-center justify-between p-0 relative shrink-0 w-[354px]">
      <PopupButton />
      <IconButton />
    </div>
  );
}

function UpperBar() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-2.5 items-center justify-start overflow-clip px-[19px] py-2 relative shrink-0"
      data-name="upper bar"
    >
      <Frame15 />
    </div>
  );
}

function Depth5Frame0() {
  return (
    <div className="relative shrink-0 w-full" data-name="Depth 5, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
        <div className="css-ddnua5 font-['Inter:Bold',_sans-serif] font-bold leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[32px] text-left w-full">
          <p className="block leading-[36px]">
            The Greatest Project In the World
          </p>
        </div>
      </div>
    </div>
  );
}

function Depth7Frame0() {
  return (
    <div className="relative shrink-0 w-full" data-name="Depth 7, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
        <div className="css-ddnua5 font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[16px] text-left w-[310px]">
          <p className="leading-[24px]">
            <span>{`By `}</span>
            <span className="font-['Inter:Semi_Bold',_sans-serif] font-semibold not-italic">
              Alex
            </span>
            <span>{` · `}</span>
            <span className="font-['Inter:Semi_Bold',_sans-serif] font-semibold not-italic">
              3
            </span>
            <span className="font-['Inter:Medium',_sans-serif] font-medium not-italic">{` collaborators`}</span>
          </p>
        </div>
      </div>
    </div>
  );
}

function Depth4Frame1() {
  return (
    <div
      className="h-[124px] min-w-72 relative shrink-0 w-[359px]"
      data-name="Depth 4, Frame 1"
    >
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col gap-1 h-[124px] items-center justify-end min-w-inherit pb-6 pt-4 px-6 relative w-[359px]">
        <Depth5Frame0 />
        <Depth7Frame0 />
      </div>
    </div>
  );
}

function Card() {
  return (
    <div
      className="bg-[position:0%_0%,_50%_50%] bg-size-[auto,cover] box-border content-stretch flex flex-col gap-2.5 h-[614px] items-center justify-end overflow-clip p-0 relative rounded-[14px] shadow-[0px_4px_14.4px_0px_rgba(0,0,0,0.25)] shrink-0 w-[357px]"
      data-name="Card"
      style={{
        backgroundImage:
          "url('data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')",
      }}
    >
      <Depth4Frame1 />
    </div>
  );
}

function Depth5Frame2() {
  return (
    <div className="relative shrink-0 w-full" data-name="Depth 5, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
        <div className="css-o1kdnh font-['Inter:Bold',_sans-serif] font-bold leading-[0] not-italic relative shrink-0 text-[#000000] text-[18px] text-left w-full">
          <p className="block leading-[23px]">Best Project In the World</p>
        </div>
      </div>
    </div>
  );
}

function Depth7Frame2() {
  return (
    <div className="relative shrink-0 w-[113px]" data-name="Depth 7, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-[113px]">
        <div className="css-7oolnk font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#616c78] text-[16px] text-left w-full">
          <p className="block leading-[24px]">By Alex</p>
        </div>
      </div>
    </div>
  );
}

function Depth7Frame1() {
  return (
    <div className="relative shrink-0" data-name="Depth 7, Frame 1">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative">
        <div className="css-7oolnk font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#616c78] text-[16px] text-left text-nowrap w-full">
          <p className="block leading-[24px] whitespace-pre">3 collaborators</p>
        </div>
      </div>
    </div>
  );
}

function Depth6Frame0() {
  return (
    <div className="relative shrink-0" data-name="Depth 6, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col gap-1 items-start justify-start p-0 relative">
        <Depth7Frame2 />
        <Depth7Frame1 />
      </div>
    </div>
  );
}

function Depth5Frame1() {
  return (
    <div className="relative shrink-0 w-full" data-name="Depth 5, Frame 1">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-row items-end justify-between p-0 relative w-full">
        <Depth6Frame0 />
      </div>
    </div>
  );
}

function Depth4Frame2() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-1 h-[111px] items-start justify-center min-w-72 px-0 py-4 relative shrink-0 w-[358px]"
      data-name="Depth 4, Frame 1"
    >
      <Depth5Frame2 />
      <Depth5Frame1 />
    </div>
  );
}

function Frame14() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-1 items-center justify-start left-[7px] pb-0 pt-[11px] px-0 top-[-0.5px] w-[379px]">
      <Card />
      <Depth4Frame2 />
    </div>
  );
}

function MainContent() {
  return (
    <div
      className="h-[645px] overflow-clip relative shrink-0 w-[393px]"
      data-name="main content"
    >
      <Frame14 />
    </div>
  );
}

function Depth5Frame3() {
  return (
    <div
      className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0"
      data-name="Depth 5, Frame 0"
    >
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
          <div className="absolute bottom-[12.5%] left-[12.5%] right-[12.5%] top-[9.382%]">
            <svg
              className="block size-full"
              fill="none"
              preserveAspectRatio="none"
              viewBox="0 0 18 19"
            >
              <path
                clipRule="evenodd"
                d={svgPaths.p11f24e80}
                fill="var(--fill-0, #0055F7)"
                fillRule="evenodd"
                id="Vector - 0"
              />
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
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-row h-8 items-center justify-center p-0 relative">
        <Depth5Frame3 />
      </div>
    </div>
  );
}

function Depth3Frame0() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-1 items-center justify-end p-0 relative rounded-2xl shrink-0 w-[65.2px]"
      data-name="Depth 3, Frame 0"
    >
      <Depth4Frame0 />
    </div>
  );
}

function Group() {
  return (
    <div
      className="absolute bottom-[11.981%] left-[8.336%] right-[4.166%] top-[4.167%]"
      data-name="Group"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 21 21"
      >
        <g id="Group">
          <path
            clipRule="evenodd"
            d={svgPaths.p11caffd0}
            fill="var(--fill-0, #616C78)"
            fillRule="evenodd"
            id="Vector"
          />
        </g>
      </svg>
    </div>
  );
}

function MingcuteSearchAiLine() {
  return (
    <div
      className="relative shrink-0 size-6"
      data-name="mingcute:search-ai-line"
    >
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border overflow-clip relative size-6">
        <Group />
      </div>
    </div>
  );
}

function Depth4Frame3() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-row h-8 items-center justify-center p-0 relative">
        <MingcuteSearchAiLine />
      </div>
    </div>
  );
}

function Depth3Frame1() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-1 items-center justify-end p-0 relative shrink-0 w-[65.2px]"
      data-name="Depth 3, Frame 1"
    >
      <Depth4Frame3 />
    </div>
  );
}

function Frame4() {
  return (
    <div className="box-border content-stretch flex flex-row items-center justify-center p-0 relative shrink-0">
      <Depth3Frame0 />
      <Depth3Frame1 />
    </div>
  );
}

function Depth5Frame4() {
  return (
    <div
      className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0"
      data-name="Depth 5, Frame 0"
    >
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
          <div
            className="absolute bottom-[9.366%] left-[9.374%] right-[9.375%] top-[9.39%]"
            style={
              { "--fill-0": "rgba(97, 108, 120, 1)" } as React.CSSProperties
            }
          >
            <svg
              className="block size-full"
              fill="none"
              preserveAspectRatio="none"
              role="presentation"
              viewBox="0 0 20 20"
            >
              <path
                clipRule="evenodd"
                d={svgPaths.p19a90780}
                fill="var(--fill-0, #616C78)"
                fillRule="evenodd"
                id="Vector - 0"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

function Depth4Frame4() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-row h-8 items-center justify-center p-0 relative">
        <Depth5Frame4 />
      </div>
    </div>
  );
}

function Depth3Frame3() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-1 items-center justify-end p-0 relative shrink-0 w-[65.2px]"
      data-name="Depth 3, Frame 3"
    >
      <Depth4Frame4 />
    </div>
  );
}

function Depth5Frame5() {
  return (
    <div
      className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0"
      data-name="Depth 5, Frame 0"
    >
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
          <div
            className="absolute bottom-[12.429%] left-[9.336%] right-[9.336%] top-[9.364%]"
            style={
              { "--fill-0": "rgba(97, 108, 120, 1)" } as React.CSSProperties
            }
          >
            <svg
              className="block size-full"
              fill="none"
              preserveAspectRatio="none"
              role="presentation"
              viewBox="0 0 20 20"
            >
              <path
                clipRule="evenodd"
                d={svgPaths.p3d54cd00}
                fill="var(--fill-0, #616C78)"
                fillRule="evenodd"
                id="Vector - 0"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

function Depth4Frame5() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-row h-8 items-center justify-center p-0 relative">
        <Depth5Frame5 />
      </div>
    </div>
  );
}

function Depth3Frame4() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-1 items-center justify-end p-0 relative shrink-0 w-[65.2px]"
      data-name="Depth 3, Frame 4"
    >
      <Depth4Frame5 />
    </div>
  );
}

function Frame5() {
  return (
    <div className="box-border content-stretch flex flex-row items-center justify-center p-0 relative shrink-0">
      <Depth3Frame3 />
      <Depth3Frame4 />
    </div>
  );
}

function Frame6() {
  return (
    <div className="absolute box-border content-stretch flex flex-row gap-[105px] items-center justify-start left-[13px] p-0 top-[32.5px]">
      <Frame4 />
      <Frame5 />
    </div>
  );
}

function Group1() {
  return (
    <div className="absolute contents inset-[10.417%]" data-name="Group">
      <div className="absolute inset-[10.417%]" data-name="Vector">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 23 23"
        >
          <path
            d={svgPaths.p3b63e500}
            fill="var(--fill-0, white)"
            id="Vector"
            stroke="var(--stroke-0, white)"
          />
        </svg>
      </div>
    </div>
  );
}

function MingcuteAddFill() {
  return (
    <div
      className="aspect-[24/24] basis-0 grow min-h-px min-w-px relative shrink-0"
      data-name="mingcute:add-fill"
    >
      <Group1 />
    </div>
  );
}

function Icon2() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row grow items-center justify-center min-h-px min-w-px p-0 relative shrink-0 w-full"
      data-name="<Icon>"
    >
      <MingcuteAddFill />
    </div>
  );
}

function IconButton1() {
  return (
    <div
      className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px]"
      data-name="!!<IconButton>"
    >
      <Icon2 />
    </div>
  );
}

function HomeIndicator() {
  return (
    <div
      className="absolute bottom-0 h-[34px] left-px right-[-1px]"
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

function NevigationBar() {
  return (
    <div
      className="bg-neutral-50 h-[126px] relative shrink-0 w-[393px]"
      data-name="nevigation bar"
    >
      <div className="h-[126px] overflow-clip relative w-[393px]">
        <Frame6 />
        <IconButton1 />
        <HomeIndicator />
      </div>
      <div className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function Screen() {
  return (
    <div
      className="absolute bg-[#ffffff] bottom-0 box-border content-stretch flex flex-col items-center justify-start left-1 overflow-clip pb-0 pt-[47px] px-0 right-[5px] top-0"
      data-name="Screen"
    >
      <UpperBar />
      <MainContent />
      <NevigationBar />
    </div>
  );
}

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
      className="absolute box-border content-stretch flex flex-row gap-[154px] h-[47px] items-center justify-center left-[-5px] pb-[19px] pt-[21px] px-4 top-0 w-[402px]"
      data-name="Status bar - iPhone"
    >
      <Time />
      <Levels />
    </div>
  );
}

export default function CardProj() {
  return (
    <div className="relative size-full" data-name="Card-proj">
      <Screen />
      <StatusBarIPhone />
    </div>
  );
}