import svgPaths from "./svg-v2kmhgi2av";
import imgRectangle1 from "figma:asset/05c3287327e822c4313850a12f564bd61005ae7d.png";
import imgRectangle3 from "figma:asset/646e6e574da44d69f040c49689e35e69950906dd.png";
import imgRectangle4 from "figma:asset/f93063da3f20e726044219bcd86ff65ba74da8d8.png";
import imgRectangle5 from "figma:asset/f48276e23db47a87f12e0d09a835f52022b449a4.png";
import imgEllipse1 from "figma:asset/404e22d1bb690ef8a9a7204b2a5171f9a486fc1a.png";

function MingcuteEditFill() {
  return (
    <div className="relative size-full" data-name="mingcute:edit-fill">
      <div className="absolute inset-[8.54%_8.54%_0.78%_12.5%]" data-name="Group">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 15">
          <g id="Group">
            <g id="Vector"></g>
            <path d={svgPaths.p2a78d000} fill="var(--fill-0, white)" id="Vector_2" />
          </g>
        </svg>
      </div>
    </div>
  );
}

function PopupButton() {
  return (
    <div className="box-border content-stretch flex gap-[3px] items-start justify-center leading-[0] px-0 py-[13px] relative shrink-0 text-nowrap" data-name="Popup Button">
      <div className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic relative shrink-0 text-[#0055f7] text-[40px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[9px] text-nowrap whitespace-pre">Ques</p>
      </div>
      <div className="css-r804ei flex flex-col font-['SF_Pro:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#0088ff] text-[18px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[18px] text-nowrap whitespace-pre">􀆏</p>
      </div>
    </div>
  );
}

function Icon() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Icon">
          <path d={svgPaths.p36c52800} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Icon1() {
  return (
    <div className="content-stretch flex items-start justify-start relative shrink-0" data-name="<Icon>">
      <Icon />
    </div>
  );
}

function IconButton() {
  return (
    <div className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0" data-name="!!<IconButton>">
      <Icon1 />
    </div>
  );
}

function Frame19() {
  return (
    <div className="content-stretch flex items-center justify-end relative shrink-0 w-10">
      <IconButton />
    </div>
  );
}

function Frame16() {
  return (
    <div className="content-stretch flex h-[52px] items-end justify-between relative shrink-0 w-[355px]">
      <PopupButton />
      <Frame19 />
    </div>
  );
}

function UpperBar() {
  return (
    <div className="bg-neutral-50 h-[90px] relative shrink-0" data-name="upper bar">
      <div className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative">
        <Frame16 />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function Group1() {
  return (
    <div className="absolute contents left-0 top-0">
      <div className="absolute bg-center bg-cover bg-no-repeat left-0 size-[393px] top-0" style={{ backgroundImage: `url('${imgRectangle1}')` }} />
      <div className="absolute bg-[rgba(0,0,0,0.5)] left-0 size-[393px] top-0" />
    </div>
  );
}

function Button() {
  return (
    <div className="basis-0 bg-[#0055f7] grow min-h-px min-w-px relative rounded-[8px] shrink-0" data-name="Button">
      <div className="flex flex-row items-center justify-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex gap-2 items-center justify-center p-[12px] relative w-full">
          <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[16px] text-neutral-100 text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
            <p className="leading-none whitespace-pre">Profile</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Button1() {
  return (
    <div className="basis-0 grow min-h-px min-w-px relative rounded-[8px] shrink-0" data-name="Button">
      <div className="flex flex-row items-center justify-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex gap-2 items-center justify-center p-[12px] relative w-full">
          <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold leading-[0] relative shrink-0 text-[#303030] text-[16px] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
            <p className="leading-none whitespace-pre">Project</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ButtonGroup() {
  return (
    <div className="content-stretch flex gap-4 items-center justify-start relative shrink-0 w-[297px]" data-name="Button Group">
      <Button />
      <Button1 />
    </div>
  );
}

function Group3() {
  return (
    <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
      <div className="[grid-area:1_/_1] flex flex-col font-['Instrument_Sans:Regular',_'Noto_Sans_JP:Regular',_'Noto_Sans_SC:Regular',_sans-serif] font-normal h-[88px] justify-center ml-3.5 mt-[74px] relative text-[12px] text-black tracking-[0.1px] translate-y-[-50%] w-[349px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.3]">
          👋 大家好，我是 李晨，一名热爱技术与创意的全栈开发者。
          <br aria-hidden="true" />
          {` 我擅长 React / Node.js / Python，有丰富的 移动端与Web应用开发经验。过去三年里，我参与过多个初创团队项目，主要负责前端架构设计、后端API开发以及用户体验优化。`}
        </p>
      </div>
      <div className="[grid-area:1_/_1] font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold h-[42px] ml-0 mt-0 relative text-[#0055f7] text-[80px] w-[41px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-none">“</p>
      </div>
    </div>
  );
}

function Frame13780() {
  return (
    <div className="content-stretch flex flex-col items-start justify-start leading-[0] relative shrink-0 text-black tracking-[0.1px] w-full">
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold h-[38px] justify-center relative shrink-0 text-[24px] w-full" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.3]">Objective</p>
      </div>
      <div className="flex flex-col font-['Instrument_Sans:Regular',_'Noto_Sans_JP:Regular',_'Noto_Sans_KR:Regular',_'Noto_Sans_SC:Regular',_sans-serif] font-normal h-[75px] justify-center relative shrink-0 text-[12px] w-[349px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.3]">
          和志同道合的伙伴一起，打造真正能解决问题、改变生活的产品。
          <br aria-hidden="true" />
          我特别关注教育科技 与 AI应用 领域，如果你也对这些方向有兴趣，欢迎一起交流！
        </p>
      </div>
    </div>
  );
}

function Frame13781() {
  return (
    <div className="content-stretch flex flex-col items-start justify-start leading-[0] relative shrink-0 text-black tracking-[0.1px] w-full">
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold h-[38px] justify-center relative shrink-0 text-[24px] w-full" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.3]">Looking For</p>
      </div>
      <div className="flex flex-col font-['Instrument_Sans:Regular',_'Noto_Sans_JP:Regular',_'Noto_Sans_SC:Regular',_sans-serif] font-normal h-[46px] justify-center relative shrink-0 text-[12px] w-[349px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.3]">能够让我持续成长，并与伙伴们一起从0到1打造产品的项目机会。</p>
      </div>
    </div>
  );
}

function Frame13782() {
  return (
    <div className="content-stretch flex flex-col items-start justify-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold h-[38px] justify-center leading-[0] relative shrink-0 text-[24px] text-black tracking-[0.1px] w-full" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[1.3]">Media</p>
      </div>
    </div>
  );
}

function Frame13787() {
  return (
    <div className="content-stretch flex flex-col gap-2 items-start justify-start relative shrink-0 w-[349px]">
      <Frame13780 />
      <Frame13781 />
      <Frame13782 />
    </div>
  );
}

function Frame13783() {
  return (
    <div className="content-stretch flex flex-col gap-px items-center justify-start relative shrink-0 w-full">
      <Group3 />
      <Frame13787 />
    </div>
  );
}

function Frame13784() {
  return (
    <div className="absolute content-stretch flex flex-col gap-2 items-center justify-start left-[15px] top-[13px] w-[363px]">
      <ButtonGroup />
      <Frame13783 />
    </div>
  );
}

function Frame13785() {
  return (
    <div className="content-stretch flex gap-2 items-center justify-start relative shrink-0 w-full">
      <div className="bg-center bg-cover bg-no-repeat h-[179px] rounded-[10px] shrink-0 w-[110px]" style={{ backgroundImage: `url('${imgRectangle3}')` }} />
      <div className="bg-center bg-cover bg-no-repeat h-[179px] rounded-[10px] shrink-0 w-[110px]" style={{ backgroundImage: `url('${imgRectangle4}')` }} />
      <div className="bg-center bg-cover bg-no-repeat h-[179px] rounded-[10px] shrink-0 w-[110px]" style={{ backgroundImage: `url('${imgRectangle5}')` }} />
    </div>
  );
}

function Frame13786() {
  return (
    <div className="absolute content-stretch flex flex-col gap-2 items-start justify-start left-[22px] top-[442px] w-[346px]">
      {[...Array(2).keys()].map((_, i) => (
        <Frame13785 key={i} />
      ))}
    </div>
  );
}

function Frame20() {
  return (
    <div className="absolute bg-white h-[830px] left-0 overflow-clip rounded-tl-[30px] rounded-tr-[30px] top-[352px] w-[393px]">
      <Frame13784 />
      <Frame13786 />
    </div>
  );
}

function Group2() {
  return (
    <div className="absolute contents left-0 top-[352px]">
      <Frame20 />
    </div>
  );
}

function MaterialSymbolsMaleRounded() {
  return (
    <div className="relative shrink-0 size-6" data-name="material-symbols:male-rounded">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="material-symbols:male-rounded">
          <path d={svgPaths.p36658800} fill="var(--fill-0, white)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame21() {
  return (
    <div className="content-stretch flex gap-1 items-center justify-start relative shrink-0 w-full">
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold h-[33px] justify-center leading-[0] relative shrink-0 text-[32px] text-white w-[203px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal]">John Doe, 20</p>
      </div>
      <MaterialSymbolsMaleRounded />
    </div>
  );
}

function MdiLocation() {
  return (
    <div className="relative shrink-0 size-6" data-name="mdi:location">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="mdi:location">
          <path d={svgPaths.p3aac8400} fill="var(--fill-0, white)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame13775() {
  return (
    <div className="content-stretch flex gap-[3px] items-center justify-start relative shrink-0">
      <MdiLocation />
      <div className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-6 justify-center leading-[0] relative shrink-0 text-[16px] text-white w-[142px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal]">Guangdong, China</p>
      </div>
    </div>
  );
}

function Frame13776() {
  return (
    <div className="content-stretch flex flex-col gap-1 items-center justify-start relative shrink-0 w-full">
      <Frame21 />
      <Frame13775 />
    </div>
  );
}

function TagToggle() {
  return (
    <div className="bg-[rgba(178,178,178,0.6)] box-border content-stretch flex gap-2 items-center justify-center p-[8px] relative rounded-[70px] shrink-0" data-name="Tag Toggle">
      <div className="flex flex-col font-['Inter:Medium',_sans-serif] font-medium justify-center leading-[0] not-italic relative shrink-0 text-[12px] text-neutral-100 text-nowrap">
        <p className="leading-none whitespace-pre">Investor</p>
      </div>
    </div>
  );
}

function TagToggle1() {
  return (
    <div className="bg-[rgba(178,178,178,0.6)] box-border content-stretch flex gap-2 items-center justify-center p-[8px] relative rounded-[70px] shrink-0" data-name="Tag Toggle">
      <div className="flex flex-col font-['Inter:Medium',_sans-serif] font-medium justify-center leading-[0] not-italic relative shrink-0 text-[12px] text-neutral-100 text-nowrap">
        <p className="leading-none whitespace-pre">Onlooker</p>
      </div>
    </div>
  );
}

function TagToggle2() {
  return (
    <div className="bg-[rgba(178,178,178,0.6)] box-border content-stretch flex gap-2 items-center justify-center p-[8px] relative rounded-[70px] shrink-0" data-name="Tag Toggle">
      <div className="flex flex-col font-['Inter:Medium',_sans-serif] font-medium justify-center leading-[0] not-italic relative shrink-0 text-[12px] text-neutral-100 text-nowrap">
        <p className="leading-none whitespace-pre">Looking for collaborators</p>
      </div>
    </div>
  );
}

function Frame13778() {
  return (
    <div className="content-stretch flex gap-2 items-start justify-start relative shrink-0">
      <TagToggle />
      <TagToggle1 />
      <TagToggle2 />
    </div>
  );
}

function TagToggle3() {
  return (
    <div className="bg-[rgba(178,178,178,0.6)] box-border content-stretch flex gap-2 items-center justify-center p-[8px] relative rounded-[70px] shrink-0" data-name="Tag Toggle">
      <div className="flex flex-col font-['Inter:Medium',_sans-serif] font-medium justify-center leading-[0] not-italic relative shrink-0 text-[12px] text-neutral-100 text-nowrap">
        <p className="leading-none whitespace-pre">Investor</p>
      </div>
    </div>
  );
}

function TagToggle4() {
  return (
    <div className="bg-[rgba(178,178,178,0.6)] box-border content-stretch flex gap-2 items-center justify-center p-[8px] relative rounded-[70px] shrink-0" data-name="Tag Toggle">
      <div className="flex flex-col font-['Inter:Medium',_sans-serif] font-medium justify-center leading-[0] not-italic relative shrink-0 text-[12px] text-neutral-100 text-nowrap">
        <p className="leading-none whitespace-pre">Developer</p>
      </div>
    </div>
  );
}

function TagToggle5() {
  return (
    <div className="bg-[rgba(178,178,178,0.6)] box-border content-stretch flex gap-2 items-center justify-center p-[8px] relative rounded-[70px] shrink-0" data-name="Tag Toggle">
      <div className="flex flex-col font-['Inter:Medium',_sans-serif] font-medium justify-center leading-[0] not-italic relative shrink-0 text-[12px] text-neutral-100 text-nowrap">
        <p className="leading-none whitespace-pre">AAAA</p>
      </div>
    </div>
  );
}

function Frame13774() {
  return (
    <div className="content-stretch flex gap-2 items-start justify-start relative shrink-0">
      <TagToggle3 />
      <TagToggle4 />
      <TagToggle5 />
    </div>
  );
}

function TagToggle6() {
  return (
    <div className="bg-[#0055f7] box-border content-stretch flex gap-2 h-7 items-center justify-center p-[8px] relative rounded-[70px] shrink-0 w-[203px]" data-name="Tag Toggle">
      <div className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold h-4 justify-center leading-[0] relative shrink-0 text-[12px] text-white w-[62px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-none">Edit Profile</p>
      </div>
      <div className="relative shrink-0 size-4" data-name="mingcute:edit-fill">
        <MingcuteEditFill />
      </div>
    </div>
  );
}

function Frame13777() {
  return (
    <div className="absolute content-stretch flex flex-col gap-2 items-center justify-start left-[81px] top-[175px] w-[231px]">
      <Frame13776 />
      <Frame13778 />
      <Frame13774 />
      <TagToggle6 />
    </div>
  );
}

function MainContent() {
  return (
    <div className="h-[1175px] overflow-clip relative shrink-0 w-[393px]" data-name="main content">
      <Group1 />
      <Group2 />
      <div className="absolute left-[137px] size-[120px] top-10">
        <div className="absolute inset-[-2.5%]">
          <img className="block max-w-none size-full" height="126" src={imgEllipse1} width="126" />
        </div>
      </div>
      <Frame13777 />
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

function Group4() {
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
        <Group4 />
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
              <path clipRule="evenodd" d={svgPaths.p19a90780} fill="var(--fill-0, #616C78)" fillRule="evenodd" id="Vector - 0" />
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
          <div className="absolute inset-[9.36%_9.34%_12.43%_9.34%]">
            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
              <path clipRule="evenodd" d={svgPaths.p3d54cd00} fill="var(--fill-0, #0055F7)" fillRule="evenodd" id="Vector - 0" />
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

function Group5() {
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
      <Group5 />
    </div>
  );
}

function Icon2() {
  return (
    <div className="basis-0 content-stretch flex grow items-center justify-center min-h-px min-w-px relative shrink-0 w-full" data-name="<Icon>">
      <MingcuteAddFill />
    </div>
  );
}

function IconButton1() {
  return (
    <div className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px]" data-name="!!<IconButton>">
      <Icon2 />
    </div>
  );
}

function NevigationBar() {
  return (
    <div className="bg-neutral-50 h-[121px] relative shrink-0 w-[393px]" data-name="nevigation bar">
      <div className="h-[121px] overflow-clip relative w-[393px]">
        <Frame6 />
        <IconButton1 />
      </div>
      <div aria-hidden="true" className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function ProfileMine() {
  return (
    <div className="absolute bg-white content-stretch flex flex-col inset-0 items-center justify-start overflow-clip" data-name="Profile-mine">
      <UpperBar />
      <MainContent />
      <NevigationBar />
    </div>
  );
}

export default function ProfileMine1() {
  return (
    <div className="relative size-full" data-name="Profile-mine">
      <ProfileMine />
    </div>
  );
}