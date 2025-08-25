import { useState } from 'react';
import svgPaths from "../imports/svg-tqxitiqz9z";

interface NotificationSettingsPageProps {
  onBack: () => void;
}

function Toggle({ enabled, onToggle }: { enabled: boolean; onToggle: () => void }) {
  return (
    <button 
      onClick={onToggle}
      className={`h-[31px] overflow-clip relative rounded-[100px] shrink-0 w-[51px] transition-colors duration-200 ${
        enabled ? 'bg-[#0055f7]' : 'bg-[#cbced4]'
      }`}
    >
      <div 
        className={`absolute bg-[#ffffff] right-0.5 rounded-[100px] shadow-[0px_0px_0px_1px_rgba(0,0,0,0.04),0px_3px_8px_0px_rgba(0,0,0,0.15),0px_3px_1px_0px_rgba(0,0,0,0.06)] size-[27px] top-1/2 translate-y-[-50%] transition-transform duration-200 ${
          enabled ? 'translate-x-0' : 'translate-x-[-20px]'
        }`}
      />
    </button>
  );
}

export default function NotificationSettingsPage({ onBack }: NotificationSettingsPageProps) {
  const [alwaysReceive, setAlwaysReceive] = useState(true);

  return (
    <div className="bg-[#fcfcfd] flex flex-col gap-2 h-[844px] overflow-clip relative w-[393px]">
      {/* Upper Bar */}
      <div className="bg-neutral-50 h-[90px] relative shrink-0">
        <div className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative">
          <div className="box-border content-stretch flex h-[52px] items-end justify-between p-0 relative shrink-0 w-[355px]">
            <div className="content-stretch flex gap-[66px] items-center justify-start relative shrink-0">
              <button 
                onClick={onBack}
                className="relative shrink-0 size-6 hover:opacity-70 transition-opacity cursor-pointer"
              >
                <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
                  <g>
                    <path clipRule="evenodd" d={svgPaths.p32ad4a00} fill="#0055F7" fillRule="evenodd" />
                  </g>
                </svg>
              </button>
              <div className="flex flex-col font-['Instrument_Sans:Bold',_sans-serif] font-bold h-10 justify-center leading-[0] relative shrink-0 text-[#050607] text-[20px] w-[196px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[9px]">Notification Setting</p>
              </div>
            </div>
          </div>
        </div>
        <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden px-4">
        <div className="h-full overflow-y-auto py-4">
          <div className="bg-[#ffffff] rounded-lg border border-[#e8edf2]">
            <div className="box-border content-stretch flex flex-col gap-2.5 items-start justify-start overflow-clip px-[17px] py-[7px] relative w-full">
              <div className="content-stretch flex gap-[107px] items-center justify-between relative shrink-0 w-full">
                <div className="flex flex-col font-['Instrument_Sans:Medium',_sans-serif] font-medium h-10 justify-center leading-[0] relative shrink-0 text-[#050607] text-[16px] flex-1" style={{ fontVariationSettings: "'wdth' 100" }}>
                  <p className="leading-[9px]">Always receive notifications</p>
                </div>
                <Toggle enabled={alwaysReceive} onToggle={() => setAlwaysReceive(!alwaysReceive)} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Bar */}
      <div className="bg-neutral-50 h-[121px] relative shrink-0">
        <div className="h-[121px] overflow-clip relative w-[393px]">
          <div className="absolute content-stretch flex gap-[105px] items-center justify-start left-[13px] top-[32.5px]">
            <div className="content-stretch flex items-center justify-center relative shrink-0">
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative rounded-2xl shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0">
                          <div className="absolute inset-[9.38%_12.5%_12.5%_12.5%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 19">
                              <path clipRule="evenodd" d={svgPaths.p11f24e80} fill="#616C78" fillRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="relative shrink-0 size-6">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border overflow-clip relative size-6">
                        <div className="absolute inset-[4.17%_4.17%_11.98%_8.34%]">
                          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 21 21">
                            <path clipRule="evenodd" d={svgPaths.p11caffd0} fill="#616C78" fillRule="evenodd" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="content-stretch flex items-center justify-center relative shrink-0">
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0">
                          <div className="absolute inset-[9.39%_9.38%_9.37%_9.37%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                              <path clipRule="evenodd" d={svgPaths.p19a90780} fill="#0055F7" fillRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="content-stretch flex flex-col gap-1 items-center justify-end relative shrink-0 w-[65.2px]">
                <div className="h-8 relative shrink-0">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-8 items-center justify-center relative">
                    <div className="basis-0 grow h-6 min-h-px min-w-px relative shrink-0">
                      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-6 overflow-clip relative w-full">
                        <div className="absolute left-0 size-6 top-0">
                          <div className="absolute inset-[9.36%_9.34%_12.43%_9.34%]">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                              <path clipRule="evenodd" d={svgPaths.p3d54cd00} fill="#616C78" fillRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="absolute bg-[#0055f7] box-border content-stretch flex flex-col items-center justify-center left-[170px] overflow-clip p-[12px] rounded-[100px] shadow-[0px_1px_8px_0px_rgba(0,0,0,0.12),0px_3px_4px_0px_rgba(0,0,0,0.14),0px_3px_3px_-2px_rgba(0,0,0,0.2)] size-[53px] top-[21.5px] hover:scale-105 transition-transform cursor-pointer">
            <div className="basis-0 content-stretch flex grow items-center justify-center min-h-px min-w-px relative shrink-0 w-full">
              <div className="aspect-[24/24] basis-0 grow min-h-px min-w-px relative shrink-0">
                <div className="absolute contents inset-[10.417%]">
                  <div className="absolute inset-[10.417%]">
                    <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 23 23">
                      <path d={svgPaths.p3b63e500} fill="white" stroke="white" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div aria-hidden="true" className="absolute border-[#e8edf2] border-[1px_0px_0px] border-solid inset-0 pointer-events-none" />
      </div>
    </div>
  );
}