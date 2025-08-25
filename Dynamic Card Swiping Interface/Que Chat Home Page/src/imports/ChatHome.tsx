import svgPaths from "./svg-0oogqy1o34";
// Placeholder avatar URLs using DiceBear API
const imgAvatars3DAvatar1 = "https://api.dicebear.com/7.x/avataaars/svg?seed=avatar1";
const imgEllipse11 = "https://api.dicebear.com/7.x/avataaars/svg?seed=kevin";
const imgEllipse12 = "https://api.dicebear.com/7.x/avataaars/svg?seed=druids";
const imgEllipse13 = "https://api.dicebear.com/7.x/avataaars/svg?seed=minari";
const imgEllipse14 = "https://api.dicebear.com/7.x/avataaars/svg?seed=frankie";
const imgEllipse15 = "https://api.dicebear.com/7.x/avataaars/svg?seed=samuel";
const imgEllipse16 = "https://api.dicebear.com/7.x/avataaars/svg?seed=alex";

function PopupButton() {
  return (
    <div
      className="box-border content-stretch flex gap-[3px] items-start justify-center leading-[0] px-0 py-[13px] relative shrink-0 text-nowrap"
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

function Group() {
  return (
    <div className="absolute inset-[8.33%_12.05%_0.78%_8.34%]" data-name="Group">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 22">
        <g id="Group">
          <path clipRule="evenodd" d={svgPaths.p2992a100} fill="var(--fill-0, white)" fillRule="evenodd" id="Vector" />
          <path
            clipRule="evenodd"
            d={svgPaths.p3651e400}
            fill="var(--fill-0, black)"
            fillRule="evenodd"
            id="Vector_2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <Group />
    </div>
  );
}

function Icon1() {
  return (
    <div className="box-border content-stretch flex items-start justify-start p-0 relative shrink-0" data-name="<Icon>">
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

function Group1() {
  return (
    <div className="absolute inset-[8.33%_12.76%_0.78%_12.76%]" data-name="Group">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 22">
        <g id="Group">
          <path clipRule="evenodd" d={svgPaths.p36ad9000} fill="var(--fill-0, black)" fillRule="evenodd" id="Vector" />
          <path
            clipRule="evenodd"
            d={svgPaths.p3dc12500}
            fill="var(--fill-0, black)"
            fillRule="evenodd"
            id="Vector_2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon2() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <Group1 />
    </div>
  );
}

function Icon3() {
  return (
    <div className="box-border content-stretch flex items-start justify-start p-0 relative shrink-0" data-name="<Icon>">
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
    <div className="box-border content-stretch flex items-center justify-start p-0 relative shrink-0 w-[81px]">
      <IconButton />
      <IconButton1 />
    </div>
  );
}

function Frame16() {
  return (
    <div className="box-border content-stretch flex h-[52px] items-end justify-between p-0 relative shrink-0 w-[355px]">
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
      <div
        aria-hidden="true"
        className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none"
      />
    </div>
  );
}

function MaterialSymbolsRefreshRounded() {
  return (
    <div className="relative shrink-0 size-4" data-name="material-symbols:refresh-rounded">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:refresh-rounded">
          <path d={svgPaths.p17b74300} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function MaterialSymbolsCloseRounded() {
  return (
    <div className="relative shrink-0 size-4" data-name="material-symbols:close-rounded">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:close-rounded">
          <path d={svgPaths.p3a73d3a2} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame244() {
  return (
    <div className="absolute box-border content-stretch flex gap-1.5 items-center justify-start left-[314px] p-0 top-2.5">
      <MaterialSymbolsRefreshRounded />
      <MaterialSymbolsCloseRounded />
    </div>
  );
}

function Frame40() {
  return (
    <div className="bg-[#ffffff] h-[30px] relative shrink-0 w-[363px]">
      <div
        aria-hidden="true"
        className="absolute border-[#0088ff] border-[0px_0px_1px] border-solid bottom-[-1px] left-0 pointer-events-none right-0 top-0"
      />
      <div
        className="absolute flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-[26px] justify-end leading-[0] left-0 text-[#000000] text-[16px] top-[26px] translate-y-[-100%] w-[363px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">People You May Want to Know...</p>
      </div>
      <Frame244 />
    </div>
  );
}

function Frame39() {
  return (
    <div className="box-border content-stretch flex flex-col gap-4 items-center justify-start p-0 relative shrink-0">
      <Frame40 />
    </div>
  );
}

function Component3DAvatars1() {
  return (
    <div className="relative shrink-0 size-14" data-name="3D Avatars / 1">
      <div
        className="absolute bg-center bg-cover bg-no-repeat inset-0"
        data-name="Avatars / 3d_avatar_1"
        style={{ backgroundImage: `url('${imgAvatars3DAvatar1}')` }}
      />
    </div>
  );
}

function Frame241() {
  return (
    <div className="box-border content-stretch flex flex-col gap-1 items-center justify-center leading-[0] p-0 relative shrink-0 text-center">
      <div
        className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium justify-center relative shrink-0 text-[#000000] text-[16px] w-32"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">Hilima Bibi</p>
      </div>
      <div
        className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#666666] text-[12px] w-[138px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">Investor</p>
      </div>
    </div>
  );
}

function Tag() {
  return (
    <div
      className="bg-[#0088ff] box-border content-stretch flex gap-2.5 h-[29px] items-end justify-center px-[18px] py-2 relative rounded-[100px] shrink-0"
      data-name="Tag"
    >
      <div
        aria-hidden="true"
        className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[100px]"
      />
      <div
        className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold justify-center leading-[0] relative shrink-0 text-[#ffffff] text-[12px] text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal] whitespace-pre">check</p>
      </div>
    </div>
  );
}

function Component37() {
  return (
    <div className="bg-[#ffffff] h-[166px] relative rounded-xl shrink-0 w-[109px]" data-name="37">
      <div className="box-border content-stretch flex flex-col gap-2 h-[166px] items-center justify-center overflow-clip pb-6 pt-8 px-6 relative w-[109px]">
        <Component3DAvatars1 />
        <Frame241 />
        <Tag />
      </div>
      <div
        aria-hidden="true"
        className="absolute border-[#eceaf5] border-[5px] border-solid inset-[-5px] pointer-events-none rounded-[17px]"
      />
    </div>
  );
}

function Component3DAvatars2() {
  return (
    <div className="relative shrink-0 size-14" data-name="3D Avatars / 1">
      <div
        className="absolute bg-center bg-cover bg-no-repeat inset-0"
        data-name="Avatars / 3d_avatar_1"
        style={{ backgroundImage: `url('${imgAvatars3DAvatar1}')` }}
      />
    </div>
  );
}

function Frame242() {
  return (
    <div className="box-border content-stretch flex flex-col gap-1 items-center justify-center leading-[0] p-0 relative shrink-0 text-center">
      <div
        className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium justify-center relative shrink-0 text-[#000000] text-[16px] w-32"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">Hilima Bibi</p>
      </div>
      <div
        className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#666666] text-[12px] w-[138px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">Investor</p>
      </div>
    </div>
  );
}

function Tag1() {
  return (
    <div
      className="bg-[#0088ff] box-border content-stretch flex gap-2.5 h-[29px] items-end justify-center px-[18px] py-2 relative rounded-[100px] shrink-0"
      data-name="Tag"
    >
      <div
        aria-hidden="true"
        className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[100px]"
      />
      <div
        className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold justify-center leading-[0] relative shrink-0 text-[#ffffff] text-[12px] text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal] whitespace-pre">check</p>
      </div>
    </div>
  );
}

function Component36() {
  return (
    <div className="bg-[#ffffff] h-[166px] relative rounded-xl shrink-0 w-[109px]" data-name="36">
      <div className="box-border content-stretch flex flex-col gap-2 h-[166px] items-center justify-center overflow-clip pb-6 pt-8 px-6 relative w-[109px]">
        <Component3DAvatars2 />
        <Frame242 />
        <Tag1 />
      </div>
      <div
        aria-hidden="true"
        className="absolute border-[#eceaf5] border-[5px] border-solid inset-[-5px] pointer-events-none rounded-[17px]"
      />
    </div>
  );
}

function Component3DAvatars3() {
  return (
    <div className="relative shrink-0 size-14" data-name="3D Avatars / 1">
      <div
        className="absolute bg-center bg-cover bg-no-repeat inset-0"
        data-name="Avatars / 3d_avatar_1"
        style={{ backgroundImage: `url('${imgAvatars3DAvatar1}')` }}
      />
    </div>
  );
}

function Frame243() {
  return (
    <div className="box-border content-stretch flex flex-col gap-1 items-center justify-center leading-[0] p-0 relative shrink-0 text-center">
      <div
        className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium justify-center relative shrink-0 text-[#000000] text-[16px] w-32"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">Hilima Bibi</p>
      </div>
      <div
        className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#666666] text-[12px] w-[138px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">Investor</p>
      </div>
    </div>
  );
}

function Tag2() {
  return (
    <div
      className="bg-[#0088ff] box-border content-stretch flex gap-2.5 h-[29px] items-end justify-center px-[18px] py-2 relative rounded-[100px] shrink-0"
      data-name="Tag"
    >
      <div
        aria-hidden="true"
        className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[100px]"
      />
      <div
        className="flex flex-col font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold justify-center leading-[0] relative shrink-0 text-[#ffffff] text-[12px] text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal] whitespace-pre">check</p>
      </div>
    </div>
  );
}

function Component38() {
  return (
    <div className="bg-[#ffffff] h-[166px] relative rounded-xl shrink-0 w-[109px]" data-name="38">
      <div className="box-border content-stretch flex flex-col gap-2 h-[166px] items-center justify-center overflow-clip pb-6 pt-8 px-6 relative w-[109px]">
        <Component3DAvatars3 />
        <Frame243 />
        <Tag2 />
      </div>
      <div
        aria-hidden="true"
        className="absolute border-[#eceaf5] border-[5px] border-solid inset-[-5px] pointer-events-none rounded-[17px]"
      />
    </div>
  );
}

function Frame245() {
  return (
    <div className="box-border content-stretch flex gap-4 items-start justify-start p-0 relative shrink-0">
      <Component37 />
      <Component36 />
      <Component38 />
    </div>
  );
}

function Frame246() {
  return (
    <div className="box-border content-stretch flex flex-col gap-6 items-center justify-start p-0 relative shrink-0">
      <Frame39 />
      <Frame245 />
    </div>
  );
}

function MaterialSymbolsSortRounded() {
  return (
    <div className="absolute left-[336px] size-4 top-1.5" data-name="material-symbols:sort-rounded">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="material-symbols:sort-rounded">
          <path d={svgPaths.p32915380} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame38() {
  return (
    <div className="box-border content-stretch flex items-center justify-between p-0 relative shrink-0 w-[363px]">
      <div
        aria-hidden="true"
        className="absolute border-[#0088ff] border-[0px_0px_1px] border-solid bottom-[-1px] left-0 pointer-events-none right-0 top-0"
      />
      <MaterialSymbolsSortRounded />
      <div
        className="flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-[26px] justify-center leading-[0] relative shrink-0 text-[#000000] text-[16px] w-[363px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal]">Chats (4)</p>
      </div>
    </div>
  );
}

function Frame77() {
  return (
    <div className="box-border content-stretch flex flex-col gap-4 items-center justify-start p-0 relative shrink-0">
      <Frame38 />
    </div>
  );
}

function Frame45() {
  return <div className="absolute h-12 left-0 top-0 w-[215px]" />;
}

function Group7() {
  return (
    <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
      <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-12">
        <img className="block max-w-none size-full" height="48" src={imgEllipse11} width="48" />
      </div>
      <div className="[grid-area:1_/_1] ml-[37px] mt-px relative size-3">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 12">
          <circle cx="6" cy="6" fill="var(--fill-0, #00CC5E)" id="Ellipse 14" r="6" />
        </svg>
      </div>
    </div>
  );
}

function Frame44() {
  return (
    <div className="h-12 leading-[0] relative shrink-0 text-[16px] text-nowrap tracking-[-0.32px] w-[148px]">
      <div
        className="absolute font-['Instrument_Sans:Medium',_sans-serif] font-medium left-[0.5px] text-[#213241] top-0"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">kevin.eth</p>
      </div>
      <div
        className="absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal left-0 text-[#8593a8] top-6"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">haha</p>
      </div>
    </div>
  );
}

function Frame74() {
  return (
    <div className="box-border content-stretch flex gap-[9px] items-start justify-start p-0 relative shrink-0">
      <Group7 />
      <Frame44 />
    </div>
  );
}

function UnreadLabel() {
  return (
    <div
      className="grid-cols-[max-content] grid-rows-[max-content] inline-grid place-items-start relative shrink-0"
      data-name="unread-label"
    >
      <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-5">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
          <circle cx="10" cy="10" fill="var(--fill-0, #0573F3)" id="Ellipse 12" r="10" />
        </svg>
      </div>
      <div
        className="[grid-area:1_/_1] font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] ml-[7px] mt-0.5 relative text-[#f6fbff] text-[12px] text-nowrap tracking-[-0.24px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">1</p>
      </div>
    </div>
  );
}

function Frame73() {
  return (
    <div className="box-border content-stretch flex flex-col gap-1 items-end justify-start leading-[0] p-0 relative shrink-0">
      <div
        className="font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[#8593a8] text-[12px] text-nowrap tracking-[-0.24px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] whitespace-pre">14:28</p>
      </div>
      <UnreadLabel />
    </div>
  );
}

function Frame75() {
  return (
    <div className="absolute box-border content-stretch flex gap-[98px] items-start justify-start left-0 p-0 top-0">
      <Frame74 />
      <Frame73 />
    </div>
  );
}

function Chat01() {
  return (
    <div className="h-12 relative shrink-0 w-full" data-name="chat-01">
      <Frame45 />
      <Frame75 />
    </div>
  );
}

function Frame46() {
  return (
    <div className="box-border content-stretch flex flex-col items-start justify-start leading-[0] p-0 relative shrink-0 text-[16px] text-nowrap tracking-[-0.32px] w-[174px]">
      <div
        className="font-['Instrument_Sans:Medium',_sans-serif] font-medium relative shrink-0 text-[#213241]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">druids.eth</p>
      </div>
      <div
        className="font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[#8593a8]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">I thought it was you, lol</p>
      </div>
    </div>
  );
}

function Frame47() {
  return (
    <div className="absolute box-border content-stretch flex gap-2.5 items-start justify-start left-0 p-0 top-0 w-[232px]">
      <div className="relative shrink-0 size-12">
        <img className="block max-w-none size-full" height="48" src={imgEllipse12} width="48" />
      </div>
      <Frame46 />
    </div>
  );
}

function UnreadLabel1() {
  return (
    <div className="absolute contents left-[314px] top-7" data-name="unread-label">
      <div className="absolute left-[314px] size-5 top-7">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
          <circle cx="10" cy="10" fill="var(--fill-0, #0573F3)" id="Ellipse 12" r="10" />
        </svg>
      </div>
      <div
        className="absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] left-[321px] text-[#f6fbff] text-[12px] text-nowrap top-[30px] tracking-[-0.24px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">3</p>
      </div>
    </div>
  );
}

function Chat02() {
  return (
    <div className="h-12 relative shrink-0 w-full" data-name="chat-02">
      <Frame47 />
      <div
        className="absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] left-[281.5px] text-[#8593a8] text-[12px] top-0 tracking-[-0.24px] w-[53px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px]">yesterday</p>
      </div>
      <UnreadLabel1 />
    </div>
  );
}

function Frame48() {
  return (
    <div className="box-border content-stretch flex flex-col items-start justify-start leading-[0] p-0 relative shrink-0 text-[16px] text-nowrap tracking-[-0.32px]">
      <div
        className="font-['Instrument_Sans:Medium',_sans-serif] font-medium relative shrink-0 text-[#213241]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">minari.sol</p>
      </div>
      <div
        className="font-['Instrument_Sans:Italic',_sans-serif] font-normal italic relative shrink-0 text-[#0055f7]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">[Waiting for reply]</p>
      </div>
    </div>
  );
}

function Frame49() {
  return (
    <div className="absolute box-border content-stretch flex gap-2.5 items-start justify-start left-0 p-0 top-0 w-[215px]">
      <div className="relative shrink-0 size-12">
        <img className="block max-w-none size-full" height="48" src={imgEllipse13} width="48" />
      </div>
      <Frame48 />
    </div>
  );
}

function Chat03() {
  return (
    <div className="h-12 relative shrink-0 w-full" data-name="chat-03">
      <Frame49 />
      <div
        className="absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] left-[281.5px] text-[#8593a8] text-[12px] top-0 tracking-[-0.24px] w-[53px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px]">yesterday</p>
      </div>
    </div>
  );
}

function Frame50() {
  return (
    <div className="box-border content-stretch flex flex-col items-start justify-start leading-[0] p-0 relative shrink-0 text-[16px] text-nowrap tracking-[-0.32px]">
      <div
        className="font-['Instrument_Sans:Medium',_sans-serif] font-medium lowercase relative shrink-0 text-[#213241]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">0x71C7656EC7ab4...dFB7</p>
      </div>
      <div
        className="font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[#8593a8]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">
          Whats up Sam, it’s Frankie. 😏
        </p>
      </div>
    </div>
  );
}

function Frame51() {
  return (
    <div className="absolute box-border content-stretch flex gap-2.5 items-start justify-start left-0 p-0 top-1 w-[215px]">
      <div className="relative shrink-0 size-12">
        <img className="block max-w-none size-full" height="48" src={imgEllipse14} width="48" />
      </div>
      <Frame50 />
    </div>
  );
}

function Chat04() {
  return (
    <div className="h-[52px] relative shrink-0 w-full" data-name="chat-04">
      <Frame51 />
      <div
        className="absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] left-[299px] text-[#8593a8] text-[12px] text-nowrap top-0 tracking-[-0.24px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] whitespace-pre">Friday</p>
      </div>
    </div>
  );
}

function Frame52() {
  return (
    <div className="box-border content-stretch flex flex-col items-start justify-start leading-[0] p-0 relative shrink-0 text-[16px] text-nowrap tracking-[-0.32px]">
      <div
        className="font-['Instrument_Sans:Medium',_sans-serif] font-medium relative shrink-0 text-[#213241]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">Samuel Garry</p>
      </div>
      <div
        className="font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[#8593a8]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">Done, 😏</p>
      </div>
    </div>
  );
}

function Frame53() {
  return (
    <div className="absolute box-border content-stretch flex gap-2.5 items-start justify-start left-0 p-0 top-1 w-[215px]">
      <div className="relative shrink-0 size-12">
        <img className="block max-w-none size-full" height="48" src={imgEllipse15} width="48" />
      </div>
      <Frame52 />
    </div>
  );
}

function Chat05() {
  return (
    <div className="h-[52px] relative shrink-0 w-full" data-name="chat-05">
      <Frame53 />
      <div
        className="absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] left-[274.5px] text-[#8593a8] text-[12px] top-0 tracking-[-0.24px] w-[60px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px]">07/21/2022</p>
      </div>
    </div>
  );
}

function Frame54() {
  return (
    <div className="box-border content-stretch flex flex-col items-start justify-start leading-[0] p-0 relative shrink-0 text-[16px] text-nowrap tracking-[-0.32px]">
      <div
        className="font-['Instrument_Sans:Medium',_sans-serif] font-medium relative shrink-0 text-[#213241]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">Anthony (Web3.io)</p>
      </div>
      <div
        className="font-['Instrument_Sans:Regular',_sans-serif] font-normal relative shrink-0 text-[#8593a8]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] text-nowrap whitespace-pre">Lemme join ur club, buddy</p>
      </div>
    </div>
  );
}

function Frame55() {
  return (
    <div className="absolute box-border content-stretch flex gap-2.5 items-start justify-start left-0 p-0 top-1 w-[215px]">
      <div className="relative shrink-0 size-12">
        <img className="block max-w-none size-full" height="48" src={imgEllipse16} width="48" />
      </div>
      <Frame54 />
    </div>
  );
}

function Chat06() {
  return (
    <div className="h-[52px] relative shrink-0 w-full" data-name="chat-06">
      <Frame55 />
      <div
        className="absolute font-['Instrument_Sans:Regular',_sans-serif] font-normal leading-[0] left-[334px] text-[#8593a8] text-[12px] text-nowrap text-right top-0 tracking-[-0.24px] translate-x-[-100%]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="adjustLetterSpacing block leading-[24px] whitespace-pre">07/18/2022</p>
      </div>
    </div>
  );
}

function Frame76() {
  return (
    <div className="box-border content-stretch flex flex-col gap-6 items-start justify-start p-0 relative shrink-0 w-[334px]">
      <Chat01 />
      <Chat02 />
      <Chat03 />
      <Chat04 />
      <Chat05 />
      <Chat06 />
    </div>
  );
}

function Frame78() {
  return (
    <div className="box-border content-stretch flex flex-col gap-4 items-center justify-start p-0 relative shrink-0">
      <Frame77 />
      <Frame76 />
    </div>
  );
}

function Frame14() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-4 h-[663px] items-center justify-start left-[7px] pb-0 pt-[11px] px-0 top-0 w-[379px]">
      <Frame246 />
      <Frame78 />
    </div>
  );
}

function MdiContact() {
  return (
    <div className="absolute left-[15px] size-6 top-[15px]" data-name="mdi:contact">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="mdi:contact">
          <path d={svgPaths.p18e83d80} fill="var(--fill-0, white)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function VuesaxBoldMessageText() {
  return (
    <div className="absolute contents left-[15px] top-[15px]" data-name="vuesax/bold/message-text">
      <MdiContact />
    </div>
  );
}

function BtnNewChat() {
  return (
    <div className="absolute left-[316px] size-[54px] top-[587px]" data-name="__btn-new-chat">
      <VuesaxBoldMessageText />
    </div>
  );
}

function MainContent() {
  return (
    <div className="h-[663px] overflow-clip relative shrink-0 w-[393px]" data-name="main content">
      <Frame14 />
      <BtnNewChat />
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
              <path
                clipRule="evenodd"
                d={svgPaths.p11f24e80}
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

function Depth4Frame0() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center p-0 relative">
        <Depth5Frame0 />
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

function Group2() {
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
        <Group2 />
      </div>
    </div>
  );
}

function Depth4Frame1() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center p-0 relative">
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
      <Depth4Frame1 />
    </div>
  );
}

function Frame4() {
  return (
    <div className="box-border content-stretch flex items-center justify-center p-0 relative shrink-0">
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
              <path
                clipRule="evenodd"
                d={svgPaths.p19a90780}
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

function Depth4Frame2() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center p-0 relative">
        <Depth5Frame1 />
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
      <Depth4Frame2 />
    </div>
  );
}

function Depth5Frame2() {
  return (
    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0" data-name="Depth 5, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
        <div className="absolute left-0 size-6 top-0" data-name="Vector - 0">
          <div
            className="absolute inset-[9.36%_9.34%_12.43%_9.34%]"
            style={{ "--fill-0": "rgba(97, 108, 120, 1)" } as React.CSSProperties}
          >
            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
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

function Depth4Frame3() {
  return (
    <div className="h-8 relative shrink-0" data-name="Depth 4, Frame 0">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center p-0 relative">
        <Depth5Frame2 />
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
      <Depth4Frame3 />
    </div>
  );
}

function Frame5() {
  return (
    <div className="box-border content-stretch flex items-center justify-center p-0 relative shrink-0">
      <Depth3Frame3 />
      <Depth3Frame4 />
    </div>
  );
}

function Frame6() {
  return (
    <div className="absolute box-border content-stretch flex gap-[105px] items-center justify-start left-[13px] p-0 top-[32.5px]">
      <Frame4 />
      <Frame5 />
    </div>
  );
}

function Group3() {
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
      <Group3 />
    </div>
  );
}

function Icon4() {
  return (
    <div
      className="basis-0 box-border content-stretch flex grow items-center justify-center min-h-px min-w-px p-0 relative shrink-0 w-full"
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

export default function ChatHome() {
  return (
    <div className="relative size-full" data-name="chat-home">
      <Screen />
    </div>
  );
}