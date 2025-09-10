import svgPaths from "./svg-c0f9xmwnwg";

function IcRoundPhoto() {
  return (
    <div className="relative size-full" data-name="ic:round-photo">
      <div className="absolute inset-[12.5%]" data-name="Vector">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 18">
          <path d={svgPaths.p22924f00} fill="var(--fill-0, #616C78)" id="Vector" />
        </svg>
      </div>
    </div>
  );
}

function Frame248() {
  return (
    <div className="h-[18px] relative shrink-0 w-[250px]">
      <div className="absolute flex flex-col font-['Instrument_Sans:Regular',_sans-serif] font-normal h-6 justify-center leading-[0] left-0 text-[#050607] text-[16px] top-2 translate-y-[-50%] w-[98px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal]">This is a text.|</p>
      </div>
    </div>
  );
}

function VuesaxBoldSend() {
  return (
    <div className="absolute contents inset-0" data-name="vuesax/bold/send">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="send">
          <path d={svgPaths.p3b62cd80} fill="var(--fill-0, #3369FF)" id="Vector" />
          <g id="Vector_2" opacity="0"></g>
        </g>
      </svg>
    </div>
  );
}

function VuesaxBoldSend1() {
  return (
    <div className="relative shrink-0 size-6" data-name="vuesax/bold/send">
      <VuesaxBoldSend />
    </div>
  );
}

export default function Frame35() {
  return (
    <div className="bg-white relative rounded-[30px] size-full">
      <div aria-hidden="true" className="absolute border border-[#0088ff] border-solid inset-0 pointer-events-none rounded-[30px] shadow-[0px_0px_20px_0px_rgba(0,0,0,0.13)]" />
      <div className="flex flex-row items-center relative size-full">
        <div className="box-border content-stretch flex gap-2 items-center justify-start pl-[22px] pr-0 py-0 relative size-full">
          <Frame248 />
          <div className="relative shrink-0 size-6" data-name="ic:round-photo">
            <IcRoundPhoto />
          </div>
          <VuesaxBoldSend1 />
        </div>
      </div>
    </div>
  );
}