import svgPaths from "./svg-mqahwcz8hx";
// Placeholder background image URL
const imgBg = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=600&fit=crop";

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
        <div
          className="absolute inset-0"
          style={{ "--fill-0": "rgba(0, 0, 0, 1)" } as React.CSSProperties}
        />
      </div>
      <div
        className="h-[12.328px] relative shrink-0 w-[17.142px]"
        data-name="Wifi"
      >
        <div
          className="absolute inset-0"
          style={{ "--fill-0": "rgba(0, 0, 0, 1)" } as React.CSSProperties}
        />
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

function LuanchingPage() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[246px] overflow-clip top-[250px] w-[402px]"
      data-name="luanching page"
    >
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

function JoinButton() {
  return (
    <div
      className="bg-[#0055f7] box-border content-stretch flex flex-row gap-2.5 h-[49px] items-center justify-center px-[113px] py-[18px] relative rounded-2xl shrink-0 w-[343px]"
      data-name="Join Button"
    >
      <div className="font-['Rubik:Bold',_sans-serif] font-bold leading-[0] relative shrink-0 text-[#ffffff] text-[16px] text-center w-[161px]">
        <p className="block leading-[normal]">Join</p>
      </div>
    </div>
  );
}

function LoginButton() {
  return (
    <div
      className="bg-[#1a1a1a] box-border content-stretch flex flex-row gap-2.5 h-[49px] items-center justify-center px-[113px] py-[18px] relative rounded-2xl shrink-0 w-[343px]"
      data-name="Login Button"
    >
      <div
        aria-hidden="true"
        className="absolute border border-[#8e8e8e] border-solid inset-0 pointer-events-none rounded-2xl"
      />
      <div className="font-['Rubik:Bold',_sans-serif] font-bold h-[21px] leading-[0] relative shrink-0 text-[#ffffff] text-[16px] text-center w-[165px]">
        <p className="block leading-[normal]">Log in</p>
      </div>
    </div>
  );
}

function Buttons() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col gap-2.5 items-start justify-start left-[29px] p-0 top-[671px]"
      data-name="Buttons"
    >
      <JoinButton />
      <LoginButton />
    </div>
  );
}

function Header() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col gap-2.5 items-center justify-center leading-[0] left-[26px] p-0 text-[#ffffff] text-center top-[113px]"
      data-name="Header"
    >
      <div
        className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic relative shrink-0 text-[64px] text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[normal] whitespace-pre">Ques</p>
      </div>
      <div className="font-['Inria_Sans:Bold',_sans-serif] not-italic relative shrink-0 text-[32px] w-[341px]">
        <p className="block leading-[normal]">Find your partner now.</p>
      </div>
    </div>
  );
}

function Time1() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#ffffff] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery1() {
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
            stroke="var(--stroke-0, white)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, white)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, white)"
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

function Levels1() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, white)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, white)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery1 />
    </div>
  );
}

function StatusBarIPhone1() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-row gap-[154px] h-[47px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 top-0 w-[402px]"
      data-name="Status bar - iPhone"
    >
      <Time1 />
      <Levels1 />
    </div>
  );
}

function HomeIndicator1() {
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
            className="bg-[#ffffff] h-[5px] rounded-[100px] w-36"
            data-name="Home Indicator"
          />
        </div>
      </div>
    </div>
  );
}

function Register1() {
  return (
    <div
      className="absolute bg-[#000000] h-[874px] left-[735px] overflow-clip top-[250px] w-[402px]"
      data-name="Register_1"
    >
      <div
        className="absolute bg-no-repeat bg-size-[156.61%_100%] bg-top h-[874px] left-[-266px] top-0 w-[837px]"
        data-name="BG"
        style={{ backgroundImage: `url('${imgBg}')` }}
      />
      <div className="absolute bg-[rgba(26,26,26,0.57)] h-[874px] left-0 top-0 w-[402px]" />
      <div className="absolute font-['Rubik:Medium',_sans-serif] font-medium leading-[0] left-[196px] text-[#ffffff] text-[12px] text-center top-[803px] translate-x-[-50%] w-[290px]">
        <p className="leading-[16px]">
          <span className="font-['Rubik:Medium',_sans-serif] font-medium text-[#bcbcbc]">
            By joining Ques, you agreed to our
          </span>{" "}
          <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold">
            Terms of service
          </span>{" "}
          <span className="font-['Rubik:Medium',_sans-serif] font-medium text-[#bcbcbc]">
            and
          </span>{" "}
          <span className="font-['Rubik:SemiBold',_sans-serif] font-semibold">
            Privacy policy
          </span>
        </p>
      </div>
      <Buttons />
      <Header />
      <StatusBarIPhone1 />
      <HomeIndicator1 />
    </div>
  );
}

function Time2() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery2() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels2() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery2 />
    </div>
  );
}

function StatusBarIPhone2() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time2 />
      <Levels2 />
    </div>
  );
}

function Group93() {
  return (
    <div className="absolute bottom-[2.17%] contents font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[21.14%] right-[21.39%] text-[14px] text-left top-[93.59%]">
      <div className="absolute bottom-[2.17%] left-[21.14%] right-[38.06%] text-[#999ea1] top-[93.59%]">
        <p className="block leading-[normal]">{`Don’t have an account ? `}</p>
      </div>
      <div className="absolute bottom-[2.17%] left-[63.93%] right-[21.39%] text-[#0055f7] top-[93.59%]">
        <p className="block leading-[normal]">Sign Up</p>
      </div>
    </div>
  );
}

function EmailInput() {
  return (
    <div className="h-[67px] relative shrink-0 w-full" data-name="email input">
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[89.97%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Email
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[3.62%] right-[63.51%] text-[14px] text-[rgba(31,31,31,0.43)] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">
          Your Email Adress
        </p>
      </div>
    </div>
  );
}

function EyeOff() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[91.74%] right-[3.81%] top-[58.7%]"
      data-name="Eye off"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g clipPath="url(#clip0_3_1600)" id="Eye off">
          <path
            d={svgPaths.p3f1807e0}
            id="Icon"
            stroke="var(--stroke-0, #757575)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.6"
          />
        </g>
        <defs>
          <clipPath id="clip0_3_1600">
            <rect fill="white" height="16" width="16" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function PasswordInput() {
  return (
    <div
      className="h-[67px] relative shrink-0 w-full"
      data-name="password input"
    >
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[81.89%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <EyeOff />
      <div className="absolute bottom-[17.91%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[3.62%] right-[69.36%] text-[14px] text-[rgba(31,31,31,0.43)] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">Your Password</p>
      </div>
    </div>
  );
}

function Frame1() {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full">
      <EmailInput />
      <PasswordInput />
    </div>
  );
}

function Check() {
  return (
    <div className="absolute inset-0" data-name="check">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 20 20"
      >
        <g id="check">
          <rect
            fill="var(--fill-0, white)"
            height="19"
            id="Rectangle 16"
            rx="4.5"
            stroke="var(--stroke-0, #CDD1E0)"
            width="19"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p1f7581a8}
            id="Vector 3"
            stroke="var(--stroke-0, #000C14)"
            strokeWidth="1.5"
          />
        </g>
      </svg>
    </div>
  );
}

function RememberMe() {
  return (
    <div className="relative shrink-0 size-5" data-name="remember me">
      <div className="absolute bottom-[5%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-[135%] right-[-515%] text-[#000c14] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Remember Me
        </p>
      </div>
      <Check />
    </div>
  );
}

function ForgotPassword() {
  return (
    <div
      className="h-[19px] relative shrink-0 w-[120px]"
      data-name="Forgot Password"
    >
      <div className="absolute bottom-0 font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-0 right-[-2.5%] text-[#007aff] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="[text-decoration-line:underline] [text-decoration-skip-ink:none] [text-decoration-style:solid] [text-underline-position:from-font] adjustLetterSpacing block leading-[normal] whitespace-pre">
          Forgot Password?
        </p>
      </div>
    </div>
  );
}

function Frame2() {
  return (
    <div className="box-border content-stretch flex flex-row items-end justify-between p-0 relative shrink-0 w-full">
      <RememberMe />
      <ForgotPassword />
    </div>
  );
}

function Frame3() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[17px] items-start justify-start p-0 relative shrink-0 w-full">
      <Frame1 />
      <Frame2 />
    </div>
  );
}

function BigButton() {
  return (
    <div className="absolute inset-0" data-name="Big Button">
      <div className="absolute bg-[rgba(0,85,247,0.4)] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[42.9%] right-[42.9%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Log in</p>
      </div>
    </div>
  );
}

function LoginButton1() {
  return (
    <div className="h-[45px] relative shrink-0 w-full" data-name="Login Button">
      <BigButton />
    </div>
  );
}

function Frame4() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-start justify-start left-[27px] p-0 top-[196px] w-[359px]">
      <Frame3 />
      <LoginButton1 />
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
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
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
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon1 />
    </div>
  );
}

function Login() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[1212px] overflow-clip top-[250px] w-[402px]"
      data-name="Login"
    >
      <StatusBarIPhone2 />
      <Group93 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[36.32%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="block leading-[normal]">
          Hello again, you’ve been missed!
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Hi, Wecome Back! 👋</p>
      </div>
      <Frame4 />
      <IconButton />
    </div>
  );
}

function Time3() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery3() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels3() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery3 />
    </div>
  );
}

function StatusBarIPhone3() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time3 />
      <Levels3 />
    </div>
  );
}

function Group94() {
  return (
    <div className="absolute bottom-[2.17%] contents font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[18.16%] right-[21.39%] text-[14px] text-left top-[93.59%]">
      <div className="absolute bottom-[2.17%] left-[18.16%] right-[38.06%] text-[#999ea1] top-[93.59%]">
        <p className="block leading-[normal]">{`Already have an account ? `}</p>
      </div>
      <div className="absolute bottom-[2.17%] left-[63.93%] right-[21.39%] text-[#0055f7] top-[93.59%]">
        <p className="block leading-[normal]">Log in</p>
      </div>
    </div>
  );
}

function EmailInput1() {
  return (
    <div
      className="h-[67px] relative shrink-0 w-[329px]"
      data-name="email input"
    >
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[89.06%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Email
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[3.62%] right-[60.51%] text-[14px] text-[rgba(31,31,31,0.43)] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">
          Your Email Adress
        </p>
      </div>
    </div>
  );
}

function EyeOff1() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[91.74%] right-[3.81%] top-[58.7%]"
      data-name="Eye off"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 15 16"
      >
        <g clipPath="url(#clip0_3_1626)" id="Eye off">
          <path
            d={svgPaths.p3b7f4f80}
            id="Icon"
            stroke="var(--stroke-0, #757575)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.6"
          />
        </g>
        <defs>
          <clipPath id="clip0_3_1626">
            <rect fill="white" height="16" width="14.663" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function PasswordInput1() {
  return (
    <div
      className="h-[67px] relative shrink-0 w-[329px]"
      data-name="password input"
    >
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[80.24%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <EyeOff1 />
      <div className="absolute bottom-[17.91%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[3.62%] right-[66.9%] text-[14px] text-[rgba(31,31,31,0.43)] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">Your Password</p>
      </div>
    </div>
  );
}

function EyeOff2() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[91.74%] right-[3.81%] top-[58.7%]"
      data-name="Eye off"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 15 16"
      >
        <g clipPath="url(#clip0_3_1626)" id="Eye off">
          <path
            d={svgPaths.p3b7f4f80}
            id="Icon"
            stroke="var(--stroke-0, #757575)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.6"
          />
        </g>
        <defs>
          <clipPath id="clip0_3_1626">
            <rect fill="white" height="16" width="14.663" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function Group96() {
  return (
    <div className="h-[67px] relative shrink-0 w-[329px]">
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[63.22%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Confirm Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <EyeOff2 />
      <div className="absolute bottom-[17.91%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[3.62%] right-[66.9%] text-[14px] text-[rgba(31,31,31,0.43)] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">Your Password</p>
      </div>
    </div>
  );
}

function Frame9() {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full">
      <EmailInput1 />
      <PasswordInput1 />
      <Group96 />
    </div>
  );
}

function Check1() {
  return (
    <div className="absolute inset-0" data-name="check">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 20 20"
      >
        <g id="check">
          <rect
            fill="var(--fill-0, white)"
            height="19"
            id="Rectangle 16"
            rx="4.5"
            stroke="var(--stroke-0, #CDD1E0)"
            width="19"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p1f7581a8}
            id="Vector 3"
            stroke="var(--stroke-0, #000C14)"
            strokeWidth="1.5"
          />
        </g>
      </svg>
    </div>
  );
}

function RememberMe1() {
  return (
    <div className="relative shrink-0 size-5" data-name="remember me">
      <div className="absolute bottom-[5%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-[135%] right-[-515%] text-[#000c14] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Remember Me
        </p>
      </div>
      <Check1 />
    </div>
  );
}

function ForgotPassword1() {
  return (
    <div className="h-[19px] shrink-0 w-[120px]" data-name="Forgot Password" />
  );
}

function Frame10() {
  return (
    <div className="box-border content-stretch flex flex-row items-end justify-between p-0 relative shrink-0 w-full">
      <RememberMe1 />
      <ForgotPassword1 />
    </div>
  );
}

function Frame11() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[17px] items-start justify-start p-0 relative shrink-0 w-full">
      <Frame9 />
      <Frame10 />
    </div>
  );
}

function BigButton1() {
  return (
    <div className="absolute inset-0" data-name="Big Button">
      <div className="absolute bg-[rgba(0,85,247,0.4)] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[40.95%] right-[41.23%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Sign up</p>
      </div>
    </div>
  );
}

function LoginButton2() {
  return (
    <div className="h-[45px] relative shrink-0 w-full" data-name="Login Button">
      <BigButton1 />
    </div>
  );
}

function Frame12() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-start justify-start left-[27px] p-0 top-[196px] w-[359px]">
      <Frame11 />
      <LoginButton2 />
    </div>
  );
}

function Icon2() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
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
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon3 />
    </div>
  );
}

function SignUp() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[2166px] overflow-clip top-[250px] w-[402px]"
      data-name="Sign up"
    >
      <StatusBarIPhone3 />
      <Group94 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[36.32%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="block leading-[normal]">
          Turn your ideas into reality today!
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Join Ques Now</p>
      </div>
      <Frame12 />
      <IconButton1 />
    </div>
  );
}

function Time4() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery4() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels4() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery4 />
    </div>
  );
}

function StatusBarIPhone4() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time4 />
      <Levels4 />
    </div>
  );
}

function Group95() {
  return (
    <div className="absolute bottom-[2.17%] contents font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[18.16%] right-[21.39%] text-[14px] text-left top-[93.59%]">
      <div className="absolute bottom-[2.17%] left-[18.16%] right-[38.06%] text-[#999ea1] top-[93.59%]">
        <p className="block leading-[normal]">{`Already have an account ? `}</p>
      </div>
      <div className="absolute bottom-[2.17%] left-[63.93%] right-[21.39%] text-[#0055f7] top-[93.59%]">
        <p className="block leading-[normal]">Log in</p>
      </div>
    </div>
  );
}

function EmailInput2() {
  return (
    <div
      className="h-[67px] relative shrink-0 w-[359px]"
      data-name="email input"
    >
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[89.97%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Email
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:Medium',_sans-serif] font-medium leading-[0] left-[3.62%] right-[67.41%] text-[#050607] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">aaa@gmail.com</p>
      </div>
    </div>
  );
}

function Eye() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[91.74%] right-[3.81%] top-[58.7%]"
      data-name="Eye"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g clipPath="url(#clip0_3_1608)" id="Eye">
          <g id="Icon">
            <path
              d={svgPaths.p2c282180}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
            <path
              d={svgPaths.p28db2b80}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
          </g>
        </g>
        <defs>
          <clipPath id="clip0_3_1608">
            <rect fill="white" height="16" width="16" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function PasswordInput2() {
  return (
    <div
      className="h-[67px] relative shrink-0 w-full"
      data-name="password input"
    >
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[81.89%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <Eye />
      <div className="absolute bottom-[17.91%] font-['Manrope:Medium',_sans-serif] font-medium leading-[0] left-[3.62%] right-[81.34%] text-[#050607] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">1234567</p>
      </div>
    </div>
  );
}

function Eye1() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[92.02%] right-[3.53%] top-[58.7%]"
      data-name="Eye"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g clipPath="url(#clip0_3_1608)" id="Eye">
          <g id="Icon">
            <path
              d={svgPaths.p2c282180}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
            <path
              d={svgPaths.p28db2b80}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
          </g>
        </g>
        <defs>
          <clipPath id="clip0_3_1608">
            <rect fill="white" height="16" width="16" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function Group97() {
  return (
    <div className="h-[67px] relative shrink-0 w-[359px]">
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[66.3%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Confirm Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 pointer-events-none right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#0055f7] border-solid inset-[-0.5px] rounded-[10.5px]"
        />
        <div className="absolute inset-0 shadow-[0px_0px_9.1px_0px_inset_rgba(0,85,247,0.22)]" />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-[3.62%] right-[81.34%] text-[#000000] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">1234567</p>
      </div>
      <Eye1 />
    </div>
  );
}

function Frame15() {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full">
      <EmailInput2 />
      <PasswordInput2 />
      <Group97 />
    </div>
  );
}

function Check2() {
  return (
    <div className="absolute inset-0" data-name="check">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 20 20"
      >
        <g id="check">
          <rect
            fill="var(--fill-0, white)"
            height="19"
            id="Rectangle 16"
            rx="4.5"
            stroke="var(--stroke-0, #CDD1E0)"
            width="19"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p1f7581a8}
            id="Vector 3"
            stroke="var(--stroke-0, #000C14)"
            strokeWidth="1.5"
          />
        </g>
      </svg>
    </div>
  );
}

function RememberMe2() {
  return (
    <div className="relative shrink-0 size-5" data-name="remember me">
      <div className="absolute bottom-[5%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-[135%] right-[-515%] text-[#000c14] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Remember Me
        </p>
      </div>
      <Check2 />
    </div>
  );
}

function ForgotPassword2() {
  return (
    <div className="h-[19px] shrink-0 w-[120px]" data-name="Forgot Password" />
  );
}

function Frame16() {
  return (
    <div className="box-border content-stretch flex flex-row items-end justify-between p-0 relative shrink-0 w-full">
      <RememberMe2 />
      <ForgotPassword2 />
    </div>
  );
}

function Frame17() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[17px] items-start justify-start p-0 relative shrink-0 w-full">
      <Frame15 />
      <Frame16 />
    </div>
  );
}

function BigButton2() {
  return (
    <div
      className="h-[45px] relative shrink-0 w-[359px]"
      data-name="Big Button"
    >
      <div className="absolute bg-[#0055f7] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[40.95%] right-[41.23%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Sign up</p>
      </div>
    </div>
  );
}

function Frame18() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-start justify-start left-[27px] p-0 top-[196px] w-[359px]">
      <Frame17 />
      <BigButton2 />
    </div>
  );
}

function Icon4() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon5() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon4 />
    </div>
  );
}

function IconButton2() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon5 />
    </div>
  );
}

function SignUp1() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[2626px] overflow-clip top-[250px] w-[402px]"
      data-name="Sign up"
    >
      <StatusBarIPhone4 />
      <Group95 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[36.32%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="block leading-[normal]">
          Turn your ideas into reality today!
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Join Ques Now</p>
      </div>
      <Frame18 />
      <IconButton2 />
    </div>
  );
}

function Time5() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery5() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels5() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery5 />
    </div>
  );
}

function StatusBarIPhone5() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time5 />
      <Levels5 />
    </div>
  );
}

function Eye2() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[91.74%] right-[3.81%] top-[58.7%]"
      data-name="Eye"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g clipPath="url(#clip0_3_1608)" id="Eye">
          <g id="Icon">
            <path
              d={svgPaths.p2c282180}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
            <path
              d={svgPaths.p28db2b80}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
          </g>
        </g>
        <defs>
          <clipPath id="clip0_3_1608">
            <rect fill="white" height="16" width="16" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function PasswordInput3() {
  return (
    <div
      className="h-[67px] relative shrink-0 w-full"
      data-name="password input"
    >
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[81.89%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <Eye2 />
      <div className="absolute bottom-[17.91%] font-['Manrope:Medium',_sans-serif] font-medium leading-[0] left-[3.62%] right-[81.34%] text-[#050607] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">1234567</p>
      </div>
    </div>
  );
}

function Eye3() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[92.02%] right-[3.53%] top-[58.7%]"
      data-name="Eye"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g clipPath="url(#clip0_3_1608)" id="Eye">
          <g id="Icon">
            <path
              d={svgPaths.p2c282180}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
            <path
              d={svgPaths.p28db2b80}
              stroke="var(--stroke-0, #757575)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.6"
            />
          </g>
        </g>
        <defs>
          <clipPath id="clip0_3_1608">
            <rect fill="white" height="16" width="16" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function Group98() {
  return (
    <div className="h-[67px] relative shrink-0 w-[359px]">
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[66.3%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Confirm Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 pointer-events-none right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#0055f7] border-solid inset-[-0.5px] rounded-[10.5px]"
        />
        <div className="absolute inset-0 shadow-[0px_0px_9.1px_0px_inset_rgba(0,85,247,0.22)]" />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-[3.62%] right-[81.34%] text-[#000000] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">1234567</p>
      </div>
      <Eye3 />
    </div>
  );
}

function Frame19() {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full">
      <PasswordInput3 />
      <Group98 />
    </div>
  );
}

function Frame20() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[17px] items-start justify-start p-0 relative shrink-0 w-full">
      <Frame19 />
    </div>
  );
}

function BigButton3() {
  return (
    <div
      className="h-[45px] relative shrink-0 w-[359px]"
      data-name="Big Button"
    >
      <div className="absolute bg-[#0055f7] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[29.25%] right-[29.53%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Update Password</p>
      </div>
    </div>
  );
}

function Frame21() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-start justify-start left-[27px] p-0 top-[196px] w-[359px]">
      <Frame20 />
      <BigButton3 />
    </div>
  );
}

function Icon6() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon7() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon6 />
    </div>
  );
}

function IconButton3() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon7 />
    </div>
  );
}

function ForgotPassword3() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[4505px] overflow-clip top-[250px] w-[402px]"
      data-name="Forgot Password"
    >
      <StatusBarIPhone5 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[9.7%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="block leading-[normal]">
          Ensure it differs from the previous one for security
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Set A New Password</p>
      </div>
      <Frame21 />
      <IconButton3 />
    </div>
  );
}

function Time6() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery6() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels6() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery6 />
    </div>
  );
}

function StatusBarIPhone6() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time6 />
      <Levels6 />
    </div>
  );
}

function Icon8() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon9() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon8 />
    </div>
  );
}

function IconButton4() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon9 />
    </div>
  );
}

function ForgotPassword4() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[4999px] overflow-clip top-[250px] w-[402px]"
      data-name="Forgot Password"
    >
      <StatusBarIPhone6 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[9.7%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="leading-[normal]">
          <span>{`Congratulations! Your password has already been updated. Continue to `}</span>
          <span className="text-[#0055f7]">log in</span>
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Success! 🎉</p>
      </div>
      <IconButton4 />
    </div>
  );
}

function Time7() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery7() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels7() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery7 />
    </div>
  );
}

function StatusBarIPhone7() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time7 />
      <Levels7 />
    </div>
  );
}

function Group99() {
  return (
    <div className="absolute bottom-[2.17%] contents font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[18.16%] right-[21.39%] text-[14px] text-left top-[93.59%]">
      <div className="absolute bottom-[2.17%] left-[18.16%] right-[38.06%] text-[#999ea1] top-[93.59%]">
        <p className="block leading-[normal]">{`Already have an account ? `}</p>
      </div>
      <div className="absolute bottom-[2.17%] left-[63.93%] right-[21.39%] text-[#0055f7] top-[93.59%]">
        <p className="block leading-[normal]">Log in</p>
      </div>
    </div>
  );
}

function EmailInput3() {
  return (
    <div className="h-[67px] relative shrink-0 w-full" data-name="email input">
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[89.97%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Email
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:Medium',_sans-serif] font-medium leading-[0] left-[3.62%] right-[67.41%] text-[#050607] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">aaa@gmail.com</p>
      </div>
    </div>
  );
}

function Frame22() {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full">
      <EmailInput3 />
    </div>
  );
}

function Frame23() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[17px] items-start justify-start p-0 relative shrink-0 w-full">
      <Frame22 />
    </div>
  );
}

function BigButton4() {
  return (
    <div
      className="h-[45px] relative shrink-0 w-[359px]"
      data-name="Big Button"
    >
      <div className="absolute bg-[#0055f7] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[44.29%] right-[44.57%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Next</p>
      </div>
    </div>
  );
}

function Frame24() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-start justify-start left-[27px] p-0 top-[196px] w-[359px]">
      <Frame23 />
      <BigButton4 />
    </div>
  );
}

function Icon10() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon11() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon10 />
    </div>
  );
}

function IconButton5() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon11 />
    </div>
  );
}

function ForgotPassword5() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[3086px] overflow-clip top-[250px] w-[402px]"
      data-name="Forgot Password"
    >
      <StatusBarIPhone7 />
      <Group99 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[11.44%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="block leading-[normal]">
          Please enter your email to reset the password
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Forgot Password?</p>
      </div>
      <Frame24 />
      <IconButton5 />
    </div>
  );
}

function Time8() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery8() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels8() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery8 />
    </div>
  );
}

function StatusBarIPhone8() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time8 />
      <Levels8 />
    </div>
  );
}

function Frame14() {
  return (
    <div className="absolute box-border content-stretch flex flex-row font-['Manrope:SemiBold',_sans-serif] font-semibold gap-2 items-center justify-start leading-[0] left-[63px] p-0 text-[14px] top-[362px] w-[276px]">
      <div className="h-[37px] relative shrink-0 text-[#999ea1] text-right w-44">
        <p className="block leading-[normal]">{`Haven’t got the email yet? `}</p>
      </div>
      <div className="h-[37px] relative shrink-0 text-[#0055f7] text-left w-[93px]">
        <p className="[text-decoration-line:underline] [text-decoration-skip-ink:none] [text-decoration-style:solid] [text-underline-position:from-font] block leading-[normal]">
          Resend Email
        </p>
      </div>
    </div>
  );
}

function Group100() {
  return (
    <div className="absolute contents left-[63px] top-[362px]">
      <Frame14 />
    </div>
  );
}

function Rectangle13() {
  return (
    <div className="relative shrink-0 size-14">
      <div className="absolute inset-0 rounded-xl">
        <div
          aria-hidden="true"
          className="absolute border-2 border-[#e1e1e1] border-solid inset-[-1px] pointer-events-none rounded-[13px]"
        />
      </div>
    </div>
  );
}

function Frame25() {
  return (
    <div className="box-border content-stretch flex flex-row gap-6 items-start justify-center p-0 relative shrink-0 w-[380px]">
      {[...Array(5).keys()].map((_, i) => (
        <Rectangle13 key={i} />
      ))}
    </div>
  );
}

function BigButton5() {
  return (
    <div
      className="h-[45px] relative shrink-0 w-[359px]"
      data-name="Big Button"
    >
      <div className="absolute bg-[#0055f7] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[44.29%] right-[44.57%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Next</p>
      </div>
    </div>
  );
}

function Frame26() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-center justify-start left-[25px] p-0 top-[211px] w-[359px]">
      <Frame25 />
      <BigButton5 />
    </div>
  );
}

function Icon12() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon13() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon12 />
    </div>
  );
}

function IconButton6() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon13 />
    </div>
  );
}

function ForgotPassword6() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[3559px] overflow-clip top-[250px] w-[402px]"
      data-name="Forgot Password"
    >
      <StatusBarIPhone8 />
      <Group100 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[normal] left-[6.96%] right-[8.71%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="mb-0 whitespace-pre-wrap">
          <span>{`We sent a verification code to  `}</span>
          <span className="text-[#050607]">{`aaa@gmail.com  `}</span>
        </p>
        <p className="block">
          Please check your email and enter the code below
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Forgot Password?</p>
      </div>
      <Frame26 />
      <IconButton6 />
    </div>
  );
}

function Time9() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery9() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels9() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery9 />
    </div>
  );
}

function StatusBarIPhone9() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time9 />
      <Levels9 />
    </div>
  );
}

function Frame27() {
  return (
    <div className="absolute box-border content-stretch flex flex-row font-['Manrope:SemiBold',_sans-serif] font-semibold gap-2 items-center justify-start leading-[0] left-[63px] p-0 text-[14px] top-[362px] w-[276px]">
      <div className="h-[37px] relative shrink-0 text-[#999ea1] text-right w-44">
        <p className="block leading-[normal]">{`Haven’t got the email yet? `}</p>
      </div>
      <div className="h-[37px] relative shrink-0 text-[#0055f7] text-left w-[93px]">
        <p className="[text-decoration-line:underline] [text-decoration-skip-ink:none] [text-decoration-style:solid] [text-underline-position:from-font] block leading-[normal]">
          Resend Email
        </p>
      </div>
    </div>
  );
}

function Group101() {
  return (
    <div className="absolute contents left-[63px] top-[362px]">
      <Frame27 />
    </div>
  );
}

function Rectangle18() {
  return (
    <div className="relative shrink-0 size-14">
      <div className="absolute inset-0 rounded-xl">
        <div
          aria-hidden="true"
          className="absolute border-2 border-[#0055f7] border-solid inset-[-1px] pointer-events-none rounded-[13px]"
        />
      </div>
      <div className="absolute bottom-[26.79%] flex flex-col font-['Manrope:SemiBold',_sans-serif] font-semibold justify-center leading-[0] left-[21.43%] right-[21.43%] text-[#000000] text-[24px] text-center top-1/4">
        <p className="block leading-[normal]">8</p>
      </div>
      <div className="absolute inset-0 pointer-events-none shadow-[0px_4px_4px_0px_inset_rgba(0,0,0,0.25)]" />
    </div>
  );
}

function Rectangle19() {
  return (
    <div className="relative shrink-0 size-14">
      <div className="absolute inset-0 rounded-xl">
        <div
          aria-hidden="true"
          className="absolute border-2 border-[#0055f7] border-solid inset-[-1px] pointer-events-none rounded-[13px]"
        />
      </div>
      <div className="absolute bottom-[26.79%] flex flex-col font-['Manrope:SemiBold',_sans-serif] font-semibold justify-center leading-[0] left-[21.43%] right-[21.43%] text-[#000000] text-[24px] text-center top-1/4">
        <p className="block leading-[normal]">7</p>
      </div>
      <div className="absolute inset-0 pointer-events-none shadow-[0px_4px_4px_0px_inset_rgba(0,0,0,0.25)]" />
    </div>
  );
}

function Rectangle20() {
  return (
    <div className="relative shrink-0 size-14">
      <div className="absolute inset-0 rounded-xl">
        <div
          aria-hidden="true"
          className="absolute border-2 border-[#e1e1e1] border-solid inset-[-1px] pointer-events-none rounded-[13px]"
        />
      </div>
    </div>
  );
}

function Frame28() {
  return (
    <div className="box-border content-stretch flex flex-row gap-6 items-start justify-center p-0 relative shrink-0 w-[380px]">
      <Rectangle18 />
      <Rectangle19 />
      {[...Array(3).keys()].map((_, i) => (
        <Rectangle20 key={i} />
      ))}
    </div>
  );
}

function BigButton6() {
  return (
    <div
      className="h-[45px] relative shrink-0 w-[359px]"
      data-name="Big Button"
    >
      <div className="absolute bg-[#0055f7] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[44.29%] right-[44.57%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Next</p>
      </div>
    </div>
  );
}

function Frame29() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-center justify-start left-[25px] p-0 top-[211px] w-[359px]">
      <Frame28 />
      <BigButton6 />
    </div>
  );
}

function Icon14() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon15() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon14 />
    </div>
  );
}

function IconButton7() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon15 />
    </div>
  );
}

function ForgotPassword7() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[4032px] overflow-clip top-[250px] w-[402px]"
      data-name="Forgot Password"
    >
      <StatusBarIPhone9 />
      <Group101 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[normal] left-[6.96%] right-[8.71%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="mb-0 whitespace-pre-wrap">
          <span>{`We sent a verification code to  `}</span>
          <span className="text-[#050607]">{`aaa@gmail.com  `}</span>
        </p>
        <p className="block">
          Please check your email and enter the code below
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Forgot Password?</p>
      </div>
      <Frame29 />
      <IconButton7 />
    </div>
  );
}

function Time10() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2.5 grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-0.5 px-0 relative shrink-0"
      data-name="Time"
    >
      <div
        className="font-['SF_Pro:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#050607] text-[17px] text-center text-nowrap"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[22px] whitespace-pre">9:41</p>
      </div>
    </div>
  );
}

function Battery10() {
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
            stroke="var(--stroke-0, #050607)"
            width="24"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p3bbd9700}
            fill="var(--fill-0, #050607)"
            id="Cap"
            opacity="0.4"
          />
          <rect
            fill="var(--fill-0, #050607)"
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

function Levels10() {
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
          viewBox="0 0 20 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1e09e400}
            fill="var(--fill-0, #050607)"
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
          viewBox="0 0 18 13"
        >
          <path
            clipRule="evenodd"
            d={svgPaths.p1fac3f80}
            fill="var(--fill-0, #050607)"
            fillRule="evenodd"
            id="Wifi"
          />
        </svg>
      </div>
      <Battery10 />
    </div>
  );
}

function StatusBarIPhone10() {
  return (
    <div
      className="absolute bottom-[94.47%] box-border content-stretch flex flex-row gap-[154px] items-center justify-center left-0 pb-[19px] pt-[21px] px-4 right-0 top-[0.16%]"
      data-name="Status bar - iPhone"
    >
      <Time10 />
      <Levels10 />
    </div>
  );
}

function Group102() {
  return (
    <div className="absolute bottom-[2.17%] contents font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[21.14%] right-[21.39%] text-[14px] text-left top-[93.59%]">
      <div className="absolute bottom-[2.17%] left-[21.14%] right-[38.06%] text-[#999ea1] top-[93.59%]">
        <p className="block leading-[normal]">{`Don’t have an account ? `}</p>
      </div>
      <div className="absolute bottom-[2.17%] left-[63.93%] right-[21.39%] text-[#0055f7] top-[93.59%]">
        <p className="block leading-[normal]">Sign Up</p>
      </div>
    </div>
  );
}

function EmailInput4() {
  return (
    <div className="h-[67px] relative shrink-0 w-full" data-name="email input">
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[89.97%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Email
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#c6c6c6] border-solid inset-0 pointer-events-none rounded-[10px]"
        />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:Medium',_sans-serif] font-medium leading-[0] left-[3.62%] right-[67.41%] text-[#050607] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">aaa@gmail.com</p>
      </div>
    </div>
  );
}

function EyeOff3() {
  return (
    <div
      className="absolute bottom-[17.41%] left-[92.02%] right-[3.53%] top-[58.7%]"
      data-name="Eye off"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g clipPath="url(#clip0_3_1600)" id="Eye off">
          <path
            d={svgPaths.p3f1807e0}
            id="Icon"
            stroke="var(--stroke-0, #757575)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.6"
          />
        </g>
        <defs>
          <clipPath id="clip0_3_1600">
            <rect fill="white" height="16" width="16" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function PasswordInput4() {
  return (
    <div
      className="h-[67px] relative shrink-0 w-full"
      data-name="password input"
    >
      <div className="absolute bottom-[71.64%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-0 right-[81.89%] text-[#050607] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Password
        </p>
      </div>
      <div className="absolute bg-[#ffffff] bottom-0 left-0 pointer-events-none right-0 rounded-[10px] top-[38.81%]">
        <div
          aria-hidden="true"
          className="absolute border border-[#0055f7] border-solid inset-[-0.5px] rounded-[10.5px]"
        />
        <div className="absolute inset-0 shadow-[0px_0px_9.1px_0px_inset_rgba(0,85,247,0.22)]" />
      </div>
      <div className="absolute bottom-[17.91%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-[3.62%] right-[71.87%] text-[#000000] text-[14px] text-left text-nowrap top-[53.73%]">
        <p className="block leading-[normal] whitespace-pre">●●●●●●●</p>
      </div>
      <EyeOff3 />
    </div>
  );
}

function Frame5() {
  return (
    <div className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full">
      <EmailInput4 />
      <PasswordInput4 />
    </div>
  );
}

function Check3() {
  return (
    <div className="absolute inset-0" data-name="check">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 20 20"
      >
        <g id="check">
          <rect
            fill="var(--fill-0, white)"
            height="19"
            id="Rectangle 16"
            rx="4.5"
            stroke="var(--stroke-0, #CDD1E0)"
            width="19"
            x="0.5"
            y="0.5"
          />
          <path
            d={svgPaths.p1f7581a8}
            id="Vector 3"
            stroke="var(--stroke-0, #000C14)"
            strokeWidth="1.5"
          />
        </g>
      </svg>
    </div>
  );
}

function RememberMe3() {
  return (
    <div className="relative shrink-0 size-5" data-name="remember me">
      <div className="absolute bottom-[5%] font-['Manrope:Regular',_sans-serif] font-normal leading-[0] left-[135%] right-[-515%] text-[#000c14] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="adjustLetterSpacing block leading-[normal] whitespace-pre">
          Remember Me
        </p>
      </div>
      <Check3 />
    </div>
  );
}

function ForgotPassword8() {
  return (
    <div
      className="h-[19px] relative shrink-0 w-[120px]"
      data-name="Forgot Password"
    >
      <div className="absolute bottom-0 font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-0 right-[-2.5%] text-[#007aff] text-[14px] text-left text-nowrap top-0 tracking-[0.28px]">
        <p className="[text-decoration-line:underline] [text-decoration-skip-ink:none] [text-decoration-style:solid] [text-underline-position:from-font] adjustLetterSpacing block leading-[normal] whitespace-pre">
          Forgot Password?
        </p>
      </div>
    </div>
  );
}

function Frame6() {
  return (
    <div className="box-border content-stretch flex flex-row items-end justify-between p-0 relative shrink-0 w-full">
      <RememberMe3 />
      <ForgotPassword8 />
    </div>
  );
}

function Frame7() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[17px] items-start justify-start p-0 relative shrink-0 w-full">
      <Frame5 />
      <Frame6 />
    </div>
  );
}

function BigButton7() {
  return (
    <div className="absolute inset-0" data-name="Big Button">
      <div className="absolute bg-[#0055f7] inset-0 rounded-[10px]" />
      <div className="absolute bottom-[28.89%] flex flex-col font-['Rubik:Bold',_sans-serif] font-bold justify-center leading-[0] left-[42.9%] right-[42.9%] text-[#ffffff] text-[17px] text-center text-nowrap top-[26.67%]">
        <p className="block leading-[normal] whitespace-pre">Log in</p>
      </div>
    </div>
  );
}

function LoginButton3() {
  return (
    <div className="h-[45px] relative shrink-0 w-full" data-name="Login Button">
      <BigButton7 />
    </div>
  );
}

function Frame8() {
  return (
    <div className="absolute box-border content-stretch flex flex-col gap-[27px] items-start justify-start left-[27px] p-0 top-[196px] w-[359px]">
      <Frame7 />
      <LoginButton3 />
    </div>
  );
}

function Icon16() {
  return (
    <div className="relative shrink-0 size-6" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 24 24"
      >
        <g id="Icon">
          <path
            d={svgPaths.pa00bfc0}
            id="Icon_2"
            stroke="var(--stroke-0, #B3B3B3)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}

function Icon17() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-start justify-start p-0 relative shrink-0"
      data-name="<Icon>"
    >
      <Icon16 />
    </div>
  );
}

function IconButton8() {
  return (
    <div
      className="absolute box-border content-stretch flex flex-col items-center justify-center left-[17px] overflow-clip p-[8px] rounded-[100px] top-[50px]"
      data-name="!!<IconButton>"
    >
      <Icon17 />
    </div>
  );
}

function Login1() {
  return (
    <div
      className="absolute bg-[#ffffff] h-[874px] left-[1689px] overflow-clip top-[250px] w-[402px]"
      data-name="Login"
    >
      <StatusBarIPhone10 />
      <Group102 />
      <div className="absolute bottom-[80.66%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[36.32%] text-[#999ea1] text-[14px] text-left top-[15.1%]">
        <p className="block leading-[normal]">
          Hello again, you’ve been missed!
        </p>
      </div>
      <div className="absolute bottom-[82.84%] font-['Manrope:SemiBold',_sans-serif] font-semibold leading-[0] left-[6.96%] right-[28.86%] text-[#000000] text-[25px] text-left top-[11.21%]">
        <p className="block leading-[normal]">Hi, Wecome Back! 👋</p>
      </div>
      <Frame8 />
      <IconButton8 />
    </div>
  );
}

function Frame13() {
  return (
    <div className="absolute bg-[#32ade6] box-border content-stretch flex flex-row gap-2.5 h-[203px] items-center justify-start left-[243px] p-[10px] top-[1298px] w-[2683px]">
      <div className="font-['Manrope:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[#ffffff] text-[96px] text-left text-nowrap">
        <p className="block leading-[normal] whitespace-pre">
          Pages to be determined: account creating questions pages
        </p>
      </div>
    </div>
  );
}

export default function SignUpAndSignIn() {
  return (
    <div
      className="bg-[#d4dae0] relative size-full"
      data-name="Sign up and Sign in"
    >
      <LuanchingPage />
      <Register1 />
      <Login />
      <SignUp />
      <SignUp1 />
      <ForgotPassword3 />
      <ForgotPassword4 />
      <ForgotPassword5 />
      <ForgotPassword6 />
      <ForgotPassword7 />
      <Login1 />
      <Frame13 />
    </div>
  );
}