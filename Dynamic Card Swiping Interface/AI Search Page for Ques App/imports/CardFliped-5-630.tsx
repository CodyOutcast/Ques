import svgPaths from "./svg-99bqa62khj";
// Placeholder card image URL
const imgCard = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=600&fit=crop";

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
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Icon">
          <path d={svgPaths.p345e5800} fill="var(--fill-0, black)" id="Vector" />
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

function Icon2() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
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

function Icon3() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon2 />
    </div>
  );
}

function IconButton1() {
  return (
    <div
      className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0"
      data-name="!!<IconButton>"
    >
      <Icon3 />
    </div>
  );
}

function Frame19() {
  return (
    <div className="box-border content-stretch flex flex-row items-center justify-start p-0 relative shrink-0 w-[81px]">
      <IconButton />
      <IconButton1 />
    </div>
  );
}

function Frame16() {
  return (
    <div className="box-border content-stretch flex flex-row h-[52px] items-end justify-between p-0 relative shrink-0 w-[355px]">
      <PopupButton />
      <Frame19 />
    </div>
  );
}

function UpperBar() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative shrink-0"
      data-name="upper bar"
    >
      <Frame16 />
    </div>
  );
}

function Depth5Frame0() {
  return (
    <div className="relative shrink-0 w-full" data-name="Depth 5, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
        <div className="css-ddnua5 font-['Inter:Bold',_sans-serif] font-bold leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[32px] text-left w-full">
          <p className="block leading-[36px]">The Greatest Project In the World</p>
        </div>
      </div>
    </div>
  );
}

function Depth7Frame1() {
  return (
    <div className="relative shrink-0 w-full" data-name="Depth 7, Frame 1">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
        <div className="css-ddnua5 font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[14px] text-left w-[310px]">
          <p className="block leading-[24px]">Revolutionary AI-powered platform for finding collaborator</p>
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
            <span className="font-['Inter:Semi_Bold',_sans-serif] font-semibold not-italic">Alex</span>
            <span>{` · `}</span>
            <span className="font-['Inter:Semi_Bold',_sans-serif] font-semibold not-italic">3</span>
            <span className="font-['Inter:Medium',_sans-serif] font-medium not-italic">{` collaborators`}</span>
          </p>
        </div>
      </div>
    </div>
  );
}

function Depth4Frame1() {
  return (
    <div className="h-[124px] min-w-72 relative shrink-0 w-[359px]" data-name="Depth 4, Frame 1">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col gap-1 h-[124px] items-center justify-end min-w-inherit pb-6 pt-4 px-6 relative w-[359px]">
        <Depth5Frame0 />
        <Depth7Frame1 />
        <Depth7Frame0 />
      </div>
    </div>
  );
}

function Card() {
  return (
    <div
      className="bg-[position:0%_0%,_50%_50%] bg-size-[auto,cover] box-border content-stretch flex flex-col gap-2.5 h-[642px] items-center justify-end overflow-clip p-0 relative rounded-[14px] shadow-[0px_4px_14.4px_0px_rgba(0,0,0,0.25)] shrink-0 w-[357px]"
      data-name="Card"
      style={{ backgroundImage: `url('${imgCard}')` }}
    >
      <Depth4Frame1 />
    </div>
  );
}

function Frame14() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-1 h-[663px] items-center justify-start left-[7px] pb-0 pt-[11px] px-0 top-0 w-[379px]">
      <Card />
    </div>
  );
}

function MainContent() {
  return (
    <div className="h-[663px] overflow-clip relative shrink-0 w-[393px]" data-name="main content">
      <Frame14 />
    </div>
  );
}

function Depth5Frame1() {
  return (
    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0" data-name="Depth 5, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
          <div className="absolute inset-[9.38%_12.5%_12.5%_12.5%]">
            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 19">
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
        <Depth5Frame1 />
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
    <div className="absolute inset-[4.17%_4.17%_11.98%_8.34%]" data-name="Group">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 21 21">
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
    <div className="relative shrink-0 size-6" data-name="mingcute:search-ai-line">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border overflow-clip relative size-6">
        <Group />
      </div>
    </div>
  );
}

function Depth4Frame2() {
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
      <Depth4Frame2 />
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

function Depth5Frame2() {
  return (
    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0" data-name="Depth 5, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
          <div
            className="absolute inset-[9.39%_9.38%_9.37%_9.37%]"
            style={{ "--fill-0": "rgba(97, 108, 120, 1)" } as React.CSSProperties}
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

function Depth4Frame3() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-row h-8 items-center justify-center p-0 relative">
        <Depth5Frame2 />
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
      <Depth4Frame3 />
    </div>
  );
}

function Depth5Frame3() {
  return (
    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0" data-name="Depth 5, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
          <div
            className="absolute inset-[9.36%_9.34%_12.43%_9.34%]"
            style={{ "--fill-0": "rgba(97, 108, 120, 1)" } as React.CSSProperties}
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

function Depth4Frame4() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-row h-8 items-center justify-center p-0 relative">
        <Depth5Frame3 />
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
      <Depth4Frame4 />
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
      <Group1 />
    </div>
  );
}

function Icon4() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row grow items-center justify-center min-h-px min-w-px p-0 relative shrink-0 w-full"
      data-name="<Icon>"
    >
      <MingcuteAddFill />
    </div>
  );
}

function IconButton2() {
  return (
    <div
      className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px]"
      data-name="!!<IconButton>"
    >
      <Icon4 />
    </div>
  );
}

function NevigationBar() {
  return (
    <div className="bg-neutral-50 h-[121px] relative shrink-0 w-[393px]" data-name="nevigation bar">
      <div className="h-[121px] overflow-clip relative w-[393px]">
        <Frame6 />
        <IconButton2 />
      </div>
      <div
        aria-hidden="true"
        className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none"
      />
    </div>
  );
}

function Screen() {
  return (
    <div
      className="absolute bg-[#ffffff] bottom-0 box-border content-stretch flex flex-col items-center justify-start left-1 overflow-clip p-0 right-[5px] top-0"
      data-name="Screen"
    >
      <UpperBar />
      <MainContent />
      <NevigationBar />
    </div>
  );
}

export default function CardFliped() {
  return (
    <div className="relative size-full" data-name="Card-fliped">
      <Screen />
    </div>
  );
}