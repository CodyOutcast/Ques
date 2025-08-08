/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    // Popup Frame Component custom classes
    'box-border', 'content-stretch', 'flex', 'flex-col', 'flex-row', 'gap-1', 'gap-2.5', 'gap-3', 'gap-[7px]', 'gap-[147px]',
    'items-start', 'items-center', 'items-end', 'justify-center', 'justify-start', 'justify-end', 'justify-between',
    'leading-[0]', 'leading-[normal]', 'italic', 'font-bold',
    'h-[78px]', 'h-14', 'h-[38px]', 'h-12', 'h-[127.114px]', 'h-[166.994px]',
    'w-[311px]', 'w-[477px]', 'w-[134px]', 'w-[548px]', 'w-[127.943px]', 'w-[167.433px]',
    'relative', 'absolute', 'shrink-0', 'p-0', 'pl-[22px]', 'pr-0', 'py-0', 'pb-12', 'pt-[22px]', 'left-0', 'top-0', 'top-4', 'top-[-24px]', 'top-[213px]', 'left-[30px]', 'left-[439px]', 'left-[377.23px]',
    'rounded-[30px]', 'rounded-[48px]', 'rounded-[41.088px]', 'rounded-[100px]', 'rounded-sm',
    'shadow-[5px_4px_20px_0px_rgba(0,0,0,0.13)]', 'shadow-[0px_15px_28px_0px_rgba(171,178,187,0.25)]',
    'bg-[#ffffff]', 'bg-[#0a0c0f]', 'bg-transparent', 'bg-[#3369ff]', 'bg-[#0088ff]', 'bg-[#b1bccd]',
    'text-[#2a2f3f]', 'text-[#3369ff]', 'text-[#000000]', 'text-[#b1bccd]', 'text-[#8a9bb3]', 'text-[13px]', 'text-[15px]', 'text-[16px]', 'text-[72px]', 'text-[128px]',
    'text-left', 'text-nowrap', 'whitespace-pre', 'block', 'transition-all', 'duration-200', 'scale-125', 'scale-100', 'hover:scale-110', 'drop-shadow-md', 'brightness-110',
    'border', 'border-[#0088ff]', 'border-[#49454f]', 'border-solid', 'border-2', 'pointer-events-none', 'outline-none', 'outline-ring/50', 'z-10', 'filter', 'blur-[25px]', 'opacity-40',
    'overflow-clip', 'overflow-hidden', 'overflow-auto', 'overflow-scroll',
    'size-full', 'size-6',
    'cursor-pointer', 'hover:bg-gray-50', 'transition-colors', 'hover:text-[#8a9bb3]',
    '[text-decoration-line:underline]', '[text-decoration-style:solid]', '[text-underline-position:from-font]'
  ],
  theme: {
    extend: {
      // Colors from design tokens (restored to original)
      colors: {
        // Primary brand colors (restored to original)
        primary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#030213', // Original primary color
          600: '#1e293b',
          700: '#334155',
          800: '#475569',
          900: '#64748b',
          950: '#0f172a',
        },
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        accent: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#e9ebef', // Original accent color
          600: '#cbd5e1',
          700: '#94a3b8',
          800: '#64748b',
          900: '#475569',
          950: '#334155',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#d4183d', // Original destructive color
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          950: '#450a0a',
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
        
        // Semantic colors (restored to original)
        background: {
          primary: '#ffffff',
          secondary: '#f8fafc',
          tertiary: '#f1f5f9',
          dark: '#0f172a',
          darkSecondary: '#1e293b',
        },
        text: {
          primary: '#030213', // Original foreground color
          secondary: '#64748b',
          tertiary: '#94a3b8',
          inverse: '#ffffff',
          muted: '#717182', // Original muted foreground
        },
        border: {
          light: 'rgba(0, 0, 0, 0.1)', // Original border color
          medium: '#cbd5e1',
          dark: '#94a3b8',
        },
        overlay: {
          light: 'rgba(255, 255, 255, 0.8)',
          medium: 'rgba(0, 0, 0, 0.5)',
          dark: 'rgba(0, 0, 0, 0.7)',
        },
      },

      // Typography from design tokens (restored Instrument Sans)
      fontFamily: {
        primary: ['Instrument Sans', 'system-ui', 'sans-serif'],
        secondary: ['system-ui', 'sans-serif'],
        mono: ['monospace'],
        sans: ['Instrument Sans', 'system-ui', 'sans-serif'], // Default sans font
      },

      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.5' }],
        sm: ['0.875rem', { lineHeight: '1.5' }],
        base: ['1rem', { lineHeight: '1.5' }],
        lg: ['1.125rem', { lineHeight: '1.5' }],
        xl: ['1.25rem', { lineHeight: '1.5' }],
        '2xl': ['1.5rem', { lineHeight: '1.25' }],
        '3xl': ['1.875rem', { lineHeight: '1.25' }],
        '4xl': ['2.25rem', { lineHeight: '1.25' }],
        '5xl': ['3rem', { lineHeight: '1.25' }],
        '6xl': ['3.75rem', { lineHeight: '1.25' }],
      },

      fontWeight: {
        light: 300,
        normal: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
        extrabold: 800,
      },

      lineHeight: {
        tight: 1.25,
        normal: 1.5,
        relaxed: 1.75,
        loose: 2,
      },

      letterSpacing: {
        tight: '-0.025em',
        normal: '0em',
        wide: '0.025em',
        wider: '0.05em',
        widest: '0.1em',
      },

      // Spacing from design tokens
      spacing: {
        0: '0',
        1: '0.25rem',
        2: '0.5rem',
        3: '0.75rem',
        4: '1rem',
        5: '1.25rem',
        6: '1.5rem',
        8: '2rem',
        10: '2.5rem',
        12: '3rem',
        16: '4rem',
        20: '5rem',
        24: '6rem',
        32: '8rem',
      },

      // Border radius from design tokens
      borderRadius: {
        none: '0',
        sm: '0.125rem',
        base: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
        full: '9999px',
      },

      // Shadows from design tokens
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        none: 'none',
      },

      // Transitions from design tokens
      transitionDuration: {
        fast: '150ms',
        normal: '250ms',
        slow: '350ms',
      },

      transitionTimingFunction: {
        bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },

      // Z-index from design tokens
      zIndex: {
        hide: -1,
        auto: 'auto',
        base: 0,
        docked: 10,
        dropdown: 1000,
        sticky: 1100,
        banner: 1200,
        overlay: 1300,
        modal: 1400,
        popover: 1500,
        skipLink: 1600,
        toast: 1700,
        tooltip: 1800,
      },

      // Breakpoints from design tokens
      screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
      },

      // Custom animations
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'bounce-in': 'bounceIn 0.6s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
