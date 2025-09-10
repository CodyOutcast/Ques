import svgPaths from "./svg-wrzolz7w55";

interface ChatSettingsProps {
  onNavigateBack: () => void;
}

function SolarArrowLeftOutline({ onClick }: { onClick?: () => void }) {
  return (
    <div 
      className="relative shrink-0 size-6 cursor-pointer" 
      data-name="solar:arrow-left-outline"
      onClick={onClick}
    >
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="solar:arrow-left-outline">
          <path clipRule="evenodd" d={svgPaths.p32ad4a00} fill="var(--fill-0, #0055F7)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame251({ onNavigateBack }: { onNavigateBack: () => void }) {
  return (
    <div className="absolute content-stretch flex gap-[68px] items-center justify-start left-[17px] top-[25px] w-[359px]">
      <SolarArrowLeftOutline onClick={onNavigateBack} />
      <div className="flex flex-col font-['Instrument_Sans:Bold',_sans-serif] font-bold h-10 justify-center leading-[0] relative shrink-0 text-[#050607] text-[32px] w-[197px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[9px]">Chat Setting</p>
      </div>
    </div>
  );
}

function UpperBar({ onNavigateBack }: { onNavigateBack: () => void }) {
  return (
    <div className="bg-neutral-50 h-[90px] relative shrink-0 w-full" data-name="upper bar">
      <div className="h-[90px] overflow-clip relative w-full">
        <Frame251 onNavigateBack={onNavigateBack} />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function Knob() {
  return <div className="absolute bg-[#ffffff] right-0.5 rounded-[100px] shadow-[0px_0px_0px_1px_rgba(0,0,0,0.04),0px_3px_8px_0px_rgba(0,0,0,0.15),0px_3px_1px_0px_rgba(0,0,0,0.06)] size-[27px] top-1/2 translate-y-[-50%]" data-name="Knob" />;
}

function Toggle() {
  return (
    <div className="bg-[#0055f7] h-[31px] overflow-clip relative rounded-[100px] shrink-0 w-[51px]" data-name="Toggle">
      <Knob />
    </div>
  );
}

function Frame252() {
  return (
    <div className="content-stretch flex gap-[107px] items-center justify-start relative shrink-0 w-[376px]">
      <div className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium h-10 justify-center leading-[0] relative shrink-0 text-[#050607] text-[16px] w-[207px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[9px]">Always recive notifications</p>
      </div>
      <Toggle />
    </div>
  );
}

function UpperBar1() {
  return (
    <div className="absolute bg-[#ffffff] left-0 top-0 w-[393px]" data-name="upper bar">
      <div className="box-border content-stretch flex flex-col gap-2.5 items-start justify-start overflow-clip px-[17px] py-[7px] relative w-[393px]">
        <Frame252 />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function Knob1() {
  return <div className="absolute bg-[#ffffff] right-0.5 rounded-[100px] shadow-[0px_0px_0px_1px_rgba(0,0,0,0.04),0px_3px_8px_0px_rgba(0,0,0,0.15),0px_3px_1px_0px_rgba(0,0,0,0.06)] size-[27px] top-1/2 translate-y-[-50%]" data-name="Knob" />;
}

function Toggle1() {
  return (
    <div className="bg-[#0055f7] h-[31px] overflow-clip relative rounded-[100px] shrink-0 w-[51px]" data-name="Toggle">
      <Knob1 />
    </div>
  );
}

function Frame253() {
  return (
    <div className="content-stretch flex gap-[107px] items-center justify-start relative shrink-0 w-[376px]">
      <div className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium h-10 justify-center leading-[0] relative shrink-0 text-[#050607] text-[16px] w-[207px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[9px]">Enable default greeting</p>
      </div>
      <Toggle1 />
    </div>
  );
}

function Frame255() {
  return (
    <div className="h-[41px] relative shrink-0 w-[359px]">
      <div className="absolute bg-[#ffffff] h-[41px] left-0 rounded-[10px] top-0 w-[359px]">
        <div aria-hidden="true" className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]" />
      </div>
      <div className="absolute font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-2.5 text-[14px] text-[rgba(31,31,31,0.43)] text-nowrap top-[11px]">
        <p className="leading-[normal] whitespace-pre">Click to enter my default greeting...</p>
      </div>
    </div>
  );
}

function UpperBar2() {
  return (
    <div className="absolute bg-[#ffffff] h-[120px] left-0 top-[54px] w-[393px]" data-name="upper bar">
      <div className="box-border content-stretch flex flex-col gap-2.5 h-[120px] items-start justify-start overflow-clip px-[17px] py-[7px] relative w-[393px]">
        <Frame253 />
        <Frame255 />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function MainContent() {
  return (
    <div className="h-[663px] overflow-clip relative shrink-0 w-[393px]" data-name="main content">
      <UpperBar1 />
      <UpperBar2 />
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

function Group() {
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
        <Group />
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

function Icon() {
  return (
    <div className="basis-0 content-stretch flex grow items-center justify-center min-h-px min-w-px relative shrink-0 w-full" data-name="<Icon>">
      <MingcuteAddFill />
    </div>
  );
}

function IconButton() {
  return (
    <div className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px]" data-name="!!<IconButton>">
      <Icon />
    </div>
  );
}

function NevigationBar() {
  return (
    <div className="bg-neutral-50 h-[121px] relative shrink-0 w-[393px]" data-name="nevigation bar">
      <div className="h-[121px] overflow-clip relative w-[393px]">
        <Frame6 />
        <IconButton />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function Screen({ onNavigateBack }: { onNavigateBack: () => void }) {
  return (
    <div className="absolute bg-[#ffffff] content-stretch flex flex-col inset-0 items-center justify-start overflow-clip" data-name="Screen">
      <UpperBar onNavigateBack={onNavigateBack} />
      <MainContent />
      <NevigationBar />
    </div>
  );
}

export default function ChatSettings({ onNavigateBack }: ChatSettingsProps) {
  return (
    <div className="relative size-full" data-name="chat settings">
      <Screen onNavigateBack={onNavigateBack} />
    </div>
  );
}