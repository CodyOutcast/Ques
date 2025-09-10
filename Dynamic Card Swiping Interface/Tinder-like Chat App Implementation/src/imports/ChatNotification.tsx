import svgPaths from "./svg-0t24de4fcq";
import { ImageWithFallback } from '../components/figma/ImageWithFallback';

interface ChatNotificationProps {
  onNavigateBack: () => void;
}

function SolarArrowLeftOutline({ onClick }: { onClick?: () => void }) {
  return (
    <div 
      className="relative size-full cursor-pointer" 
      data-name="solar:arrow-left-outline"
      onClick={onClick}
    >
      <div className="absolute inset-[21.88%_13.54%_21.8%_13.54%]" data-name="Vector">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 14">
          <path clipRule="evenodd" d={svgPaths.p2de4e80} fill="var(--fill-0, #0055F7)" fillRule="evenodd" id="Vector" />
        </svg>
      </div>
    </div>
  );
}

function Frame251({ onNavigateBack }: { onNavigateBack: () => void }) {
  return (
    <div className="absolute content-stretch flex gap-[66px] items-center justify-start left-[17px] top-[25px]">
      <div className="relative shrink-0 size-6" data-name="solar:arrow-left-outline">
        <SolarArrowLeftOutline onClick={onNavigateBack} />
      </div>
      <div className="flex flex-col font-['Instrument_Sans:Bold',_sans-serif] font-bold h-10 justify-center leading-[0] relative shrink-0 text-[#050607] text-[32px] w-[180px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[9px]">Notification</p>
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

function GenericAvatar() {
  return (
    <div className="relative shrink-0 size-10" data-name="Generic avatar">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 40 40">
        <g id="Generic avatar">
          <rect fill="var(--fill-0, #EADDFF)" height="40" rx="20" width="40" />
          <g id="Avatar Placeholder">
            <path clipRule="evenodd" d={svgPaths.p16400780} fill="var(--fill-0, #4F378A)" fillRule="evenodd" />
            <path d={svgPaths.pfd6ae80} fill="var(--fill-0, #4F378A)" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function Text() {
  return (
    <div className="content-stretch flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium gap-1 items-start justify-start leading-[0] relative shrink-0 text-[14px] w-[269px]" data-name="Text">
      <div className="relative shrink-0 text-[#000000] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.4] whitespace-pre">You are matched with John Doe!</p>
      </div>
      <div className="min-w-full relative shrink-0 text-[#0055f7]" style={{ width: "min-content", fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.4]">John Doe right swiped your Project Name</p>
      </div>
    </div>
  );
}

function Frame253() {
  return (
    <div className="content-stretch flex gap-3 items-start justify-start relative shrink-0">
      <GenericAvatar />
      <Text />
    </div>
  );
}

function EpClose() {
  return (
    <div className="relative shrink-0 size-6" data-name="ep-close">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="ep-close">
          <path d={svgPaths.pf007200} fill="var(--fill-0, black)" id="icon" />
        </g>
      </svg>
    </div>
  );
}

function ButtonIcon() {
  return (
    <div className="content-stretch flex items-start justify-start relative shrink-0" data-name="Button Icon">
      <EpClose />
    </div>
  );
}

function SnackbarButCooler() {
  return (
    <div className="bg-[#ffffff] relative rounded-[4px] shrink-0 w-full" data-name="Snackbar but Cooler">
      <div aria-hidden="true" className="absolute border border-[#ffd400] border-solid inset-0 pointer-events-none rounded-[4px]" />
      <div className="relative size-full">
        <div className="box-border content-stretch flex gap-3 items-start justify-start pl-4 pr-2 py-3 relative w-full">
          <Frame253 />
          <ButtonIcon />
        </div>
      </div>
    </div>
  );
}

function GenericAvatar1() {
  return (
    <div className="relative shrink-0 size-10" data-name="Generic avatar">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 40 40">
        <g id="Generic avatar">
          <rect fill="var(--fill-0, #EADDFF)" height="40" rx="20" width="40" />
          <g id="Avatar Placeholder">
            <path clipRule="evenodd" d={svgPaths.p16400780} fill="var(--fill-0, #4F378A)" fillRule="evenodd" />
            <path d={svgPaths.pfd6ae80} fill="var(--fill-0, #4F378A)" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function Text1() {
  return (
    <div className="content-stretch flex flex-col gap-1 items-start justify-start leading-[0] relative shrink-0 text-[14px] w-[213px]" data-name="Text">
      <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold relative shrink-0 text-[#000000] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.4] whitespace-pre">
          <span className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold" style={{ fontVariationSettings: "'wdth' 100" }}>
            Cody
          </span>{" "}
          <span className="font-['Instrument_Sans:Medium',_sans-serif] font-medium" style={{ fontVariationSettings: "'wdth' 100" }}>
            liked your project!
          </span>
        </p>
      </div>
      <div className="font-['Instrument_Sans:Medium',_sans-serif] font-medium min-w-full relative shrink-0 text-[#0055f7]" style={{ width: "min-content", fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.4]">Mobile App Design</p>
      </div>
    </div>
  );
}

function Frame254() {
  return (
    <div className="content-stretch flex gap-3 items-start justify-start relative shrink-0">
      <GenericAvatar1 />
      <Text1 />
      <div className="relative shrink-0 size-11">
        <ImageWithFallback 
          className="size-11 rounded-[10px] object-cover" 
          src="https://images.unsplash.com/photo-1627757818592-ce2649563a6c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2JpbGUlMjBhcHAlMjBwcm9qZWN0JTIwZGVzaWdufGVufDF8fHx8MTc1NjMwMjExMnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Mobile App Design Project"
        />
      </div>
    </div>
  );
}

function EpClose1() {
  return (
    <div className="relative shrink-0 size-6" data-name="ep-close">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="ep-close">
          <path d={svgPaths.pf007200} fill="var(--fill-0, black)" id="icon" />
        </g>
      </svg>
    </div>
  );
}

function ButtonIcon1() {
  return (
    <div className="content-stretch flex items-start justify-start relative shrink-0" data-name="Button Icon">
      <EpClose1 />
    </div>
  );
}

function SnackbarButCooler1() {
  return (
    <div className="bg-[#ffffff] relative rounded-[4px] shrink-0 w-full" data-name="Snackbar but Cooler">
      <div aria-hidden="true" className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[4px]" />
      <div className="relative size-full">
        <div className="box-border content-stretch flex gap-3 items-start justify-start pl-4 pr-2 py-3 relative w-full">
          <Frame254 />
          <ButtonIcon1 />
        </div>
      </div>
    </div>
  );
}

function GenericAvatar2() {
  return (
    <div className="relative shrink-0 size-10" data-name="Generic avatar">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 40 40">
        <g id="Generic avatar">
          <rect fill="var(--fill-0, #EADDFF)" height="40" rx="20" width="40" />
          <g id="Avatar Placeholder">
            <path clipRule="evenodd" d={svgPaths.p16400780} fill="var(--fill-0, #4F378A)" fillRule="evenodd" />
            <path d={svgPaths.pfd6ae80} fill="var(--fill-0, #4F378A)" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function Text2() {
  return (
    <div className="content-stretch flex flex-col gap-1 items-start justify-start leading-[0] relative shrink-0 text-[14px] w-[213px]" data-name="Text">
      <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold relative shrink-0 text-[#000000] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.4] whitespace-pre">
          <span>{`William `}</span>
          <span className="font-['Instrument_Sans:Medium',_sans-serif] font-medium" style={{ fontVariationSettings: "'wdth' 100" }}>
            liked your project!
          </span>
        </p>
      </div>
      <div className="font-['Instrument_Sans:Medium',_sans-serif] font-medium min-w-full relative shrink-0 text-[#0055f7]" style={{ width: "min-content", fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.4]">Web Platform</p>
      </div>
    </div>
  );
}

function Frame255() {
  return (
    <div className="content-stretch flex gap-3 items-start justify-start relative shrink-0">
      <GenericAvatar2 />
      <Text2 />
      <div className="relative shrink-0 size-11">
        <ImageWithFallback 
          className="size-11 rounded-[10px] object-cover" 
          src="https://images.unsplash.com/photo-1649451844813-3130d6f42f8a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3ZWIlMjBkZXZlbG9wbWVudCUyMHByb2plY3QlMjBtb2NrdXB8ZW58MXx8fHwxNzU2Mjc4MjExfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Web Development Project"
        />
      </div>
    </div>
  );
}

function EpClose2() {
  return (
    <div className="relative shrink-0 size-6" data-name="ep-close">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="ep-close">
          <path d={svgPaths.pf007200} fill="var(--fill-0, black)" id="icon" />
        </g>
      </svg>
    </div>
  );
}

function ButtonIcon2() {
  return (
    <div className="content-stretch flex items-start justify-start relative shrink-0" data-name="Button Icon">
      <EpClose2 />
    </div>
  );
}

function SnackbarButCooler2() {
  return (
    <div className="bg-[#ffffff] relative rounded-[4px] shrink-0 w-full" data-name="Snackbar but Cooler">
      <div aria-hidden="true" className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[4px]" />
      <div className="relative size-full">
        <div className="box-border content-stretch flex gap-3 items-start justify-start pl-4 pr-2 py-3 relative w-full">
          <Frame255 />
          <ButtonIcon2 />
        </div>
      </div>
    </div>
  );
}

function Frame252() {
  return (
    <div className="content-stretch flex flex-col gap-4 items-start justify-start relative shrink-0 w-full">
      <SnackbarButCooler />
      <SnackbarButCooler1 />
      <SnackbarButCooler2 />
    </div>
  );
}

function Frame14() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-4 h-[663px] items-center justify-start left-[7px] pb-0 pt-[11px] px-0 top-0 w-[379px]">
      <Frame252 />
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

export default function ChatNotification({ onNavigateBack }: ChatNotificationProps) {
  return (
    <div className="relative size-full" data-name="chat-notification">
      <Screen onNavigateBack={onNavigateBack} />
    </div>
  );
}