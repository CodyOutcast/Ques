import { useState } from 'react';
import svgPaths from "../imports/svg-rxmtdc5uq4";
// Placeholder image URL
const imgRectangle2 = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop";

interface NotificationPageProps {
  onBack: () => void;
  onSettingsClick: () => void;
}

interface NotificationItem {
  id: string;
  user: string;
  action: string;
  project: string;
  avatar: string;
  projectImage: string;
}

const mockNotifications: NotificationItem[] = [
  {
    id: '1',
    user: 'Cody',
    action: 'liked your project!',
    project: 'Project Name',
    avatar: 'default',
    projectImage: imgRectangle2,
  },
  {
    id: '2',
    user: 'William',
    action: 'liked your project!',
    project: 'Project Name',
    avatar: 'default',
    projectImage: imgRectangle2,
  },
];

function GenericAvatar() {
  return (
    <div className="relative shrink-0 size-10">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 40 40">
        <g>
          <rect fill="#EADDFF" height="40" rx="20" width="40" />
          <g>
            <path clipRule="evenodd" d={svgPaths.p16400780} fill="#4F378A" fillRule="evenodd" />
            <path d={svgPaths.pfd6ae80} fill="#4F378A" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function NotificationCard({ notification, onDismiss }: { 
  notification: NotificationItem; 
  onDismiss: (id: string) => void;
}) {
  return (
    <div className="bg-[#ffffff] relative rounded shrink-0 w-full border border-[#0088ff]">
      <div className="box-border content-stretch flex gap-3 items-start justify-start pl-4 pr-2 py-3 relative w-full">
        <div className="content-stretch flex gap-3 items-start justify-start relative shrink-0">
          <GenericAvatar />
          <div className="content-stretch flex flex-col gap-1 items-start justify-start leading-[0] relative shrink-0 text-[14px] w-[213px]">
            <div className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold relative shrink-0 text-[#000000] text-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
              <p className="leading-[1.4] whitespace-pre">
                <span className="font-['Instrument_Sans:SemiBold',_sans-serif] font-semibold" style={{ fontVariationSettings: "'wdth' 100" }}>
                  {notification.user}
                </span>{" "}
                <span className="font-['Instrument_Sans:Medium',_sans-serif] font-medium" style={{ fontVariationSettings: "'wdth' 100" }}>
                  {notification.action}
                </span>
              </p>
            </div>
            <div className="font-['Instrument_Sans:Medium',_sans-serif] font-medium min-w-full relative shrink-0 text-[#0055f7]" style={{ width: "min-content", fontVariationSettings: "'wdth' 100" }}>
              <p className="leading-[1.4]">{notification.project}</p>
            </div>
          </div>
          <div className="bg-center bg-cover bg-no-repeat rounded-[10px] shrink-0 size-11" style={{ backgroundImage: `url('${notification.projectImage}')` }} />
        </div>
        <button 
          onClick={() => onDismiss(notification.id)}
          className="content-stretch flex items-start justify-start relative shrink-0 hover:opacity-70 transition-opacity"
        >
          <div className="relative shrink-0 size-6">
            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
              <g>
                <path d={svgPaths.pf007200} fill="black" />
              </g>
            </svg>
          </div>
        </button>
      </div>
    </div>
  );
}

export default function NotificationPage({ onBack, onSettingsClick }: NotificationPageProps) {
  const [notifications, setNotifications] = useState(mockNotifications);

  const handleDismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

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
                <div className="absolute inset-[21.88%_13.54%_21.8%_13.54%]">
                  <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 14">
                    <path clipRule="evenodd" d={svgPaths.p2de4e80} fill="#0055F7" fillRule="evenodd" />
                  </svg>
                </div>
              </button>
              <div className="flex flex-col font-['Instrument_Sans:Bold',_sans-serif] font-bold h-10 justify-center leading-[0] relative shrink-0 text-[#050607] text-[32px] w-[180px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                <p className="leading-[9px]">Notification</p>
              </div>
              <button 
                onClick={onSettingsClick}
                className="relative shrink-0 size-6 hover:opacity-70 transition-opacity cursor-pointer"
              >
                <div className="absolute inset-[8.333%]">
                  <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                    <path clipRule="evenodd" d={svgPaths.pff4bc00} fill="black" fillRule="evenodd" />
                  </svg>
                </div>
              </button>
            </div>
          </div>
        </div>
        <div aria-hidden="true" className="absolute border-[#e8edf2] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden px-4">
        <div className="h-full overflow-y-auto py-4">
          <div className="content-stretch flex flex-col gap-4 items-start justify-start relative shrink-0 w-full">
            {notifications.map((notification) => (
              <NotificationCard 
                key={notification.id} 
                notification={notification} 
                onDismiss={handleDismissNotification}
              />
            ))}
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