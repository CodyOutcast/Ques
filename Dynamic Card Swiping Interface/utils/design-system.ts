import { designTokens, getColor, getTypography } from '../design-tokens';

// ===== DESIGN SYSTEM UTILITIES =====

/**
 * Get a color value from the design system
 * @param path - Color path (e.g., 'primary.500', 'text.primary')
 * @returns Color value
 */
export const getDesignColor = (path: string): string => {
  return getColor(path);
};

/**
 * Get a typography value from the design system
 * @param path - Typography path (e.g., 'sizes.base', 'weights.medium')
 * @returns Typography value
 */
export const getDesignTypography = (path: string): string => {
  return getTypography(path);
};

/**
 * Get spacing value from design tokens
 * @param size - Spacing size (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32)
 * @returns Spacing value
 */
export const getSpacing = (size: keyof typeof designTokens.spacing): string => {
  return designTokens.spacing[size];
};

/**
 * Get border radius value from design tokens
 * @param size - Border radius size
 * @returns Border radius value
 */
export const getBorderRadius = (size: keyof typeof designTokens.borderRadius): string => {
  return designTokens.borderRadius[size];
};

/**
 * Get shadow value from design tokens
 * @param size - Shadow size
 * @returns Shadow value
 */
export const getShadow = (size: keyof typeof designTokens.shadows): string => {
  return designTokens.shadows[size];
};

/**
 * Get transition value from design tokens
 * @param type - Transition type
 * @returns Transition value
 */
export const getTransition = (type: keyof typeof designTokens.transitions): string => {
  return designTokens.transitions[type];
};

/**
 * Get z-index value from design tokens
 * @param level - Z-index level
 * @returns Z-index value
 */
export const getZIndex = (level: keyof typeof designTokens.zIndex): string | number => {
  return designTokens.zIndex[level];
};

// ===== COLOR UTILITIES =====

/**
 * Generate a color palette for a given base color
 * @param baseColor - Base color in hex format
 * @returns Object with color variations
 */
export const generateColorPalette = (baseColor: string) => {
  // This is a simplified color palette generator
  // In a real implementation, you might want to use a color manipulation library
  return {
    50: baseColor + '0A', // 4% opacity
    100: baseColor + '1A', // 6% opacity
    200: baseColor + '33', // 20% opacity
    300: baseColor + '4D', // 30% opacity
    400: baseColor + '66', // 40% opacity
    500: baseColor,
    600: baseColor + 'CC', // 80% opacity
    700: baseColor + 'E6', // 90% opacity
    800: baseColor + 'F2', // 95% opacity
    900: baseColor + 'FA', // 98% opacity
    950: baseColor + 'FF', // 100% opacity
  };
};

/**
 * Check if a color is light or dark
 * @param color - Color in hex format
 * @returns 'light' or 'dark'
 */
export const getColorContrast = (color: string): 'light' | 'dark' => {
  // Remove # if present
  const hex = color.replace('#', '');
  
  // Convert to RGB
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  
  return luminance > 0.5 ? 'light' : 'dark';
};

/**
 * Get contrasting text color for a background color
 * @param backgroundColor - Background color in hex format
 * @returns Text color in hex format
 */
export const getContrastingTextColor = (backgroundColor: string): string => {
  const contrast = getColorContrast(backgroundColor);
  return contrast === 'light' ? '#000000' : '#ffffff';
};

// ===== TYPOGRAPHY UTILITIES =====

/**
 * Get font family from design tokens
 * @param family - Font family type
 * @returns Font family string
 */
export const getFontFamily = (family: keyof typeof designTokens.typography.fonts): string => {
  return designTokens.typography.fonts[family].join(', ');
};

/**
 * Get font size from design tokens
 * @param size - Font size
 * @returns Font size value
 */
export const getFontSize = (size: keyof typeof designTokens.typography.sizes): string => {
  return designTokens.typography.sizes[size];
};

/**
 * Get font weight from design tokens
 * @param weight - Font weight
 * @returns Font weight value
 */
export const getFontWeight = (weight: keyof typeof designTokens.typography.weights): number => {
  return designTokens.typography.weights[weight];
};

/**
 * Get line height from design tokens
 * @param height - Line height
 * @returns Line height value
 */
export const getLineHeight = (height: keyof typeof designTokens.typography.lineHeights): number => {
  return designTokens.typography.lineHeights[height];
};

// ===== RESPONSIVE UTILITIES =====

/**
 * Get breakpoint value from design tokens
 * @param breakpoint - Breakpoint size
 * @returns Breakpoint value
 */
export const getBreakpoint = (breakpoint: keyof typeof designTokens.breakpoints): string => {
  return designTokens.breakpoints[breakpoint];
};

/**
 * Check if current screen size matches a breakpoint
 * @param breakpoint - Breakpoint to check
 * @returns Boolean indicating if screen matches breakpoint
 */
export const isBreakpoint = (breakpoint: keyof typeof designTokens.breakpoints): boolean => {
  const breakpointValue = getBreakpoint(breakpoint);
  const numericValue = parseInt(breakpointValue);
  return window.innerWidth >= numericValue;
};

// ===== STYLE GENERATORS =====

/**
 * Generate CSS object for a button variant
 * @param variant - Button variant
 * @returns CSS object
 */
export const generateButtonStyles = (variant: 'primary' | 'secondary' | 'outline' | 'ghost') => {
  const baseStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: `${getSpacing(3)} ${getSpacing(4)}`,
    fontSize: getFontSize('sm'),
    fontWeight: getFontWeight('medium'),
    lineHeight: getLineHeight('normal'),
    borderRadius: getBorderRadius('md'),
    border: '1px solid transparent',
    cursor: 'pointer',
    transition: getTransition('fast'),
    textDecoration: 'none',
  };

  switch (variant) {
    case 'primary':
      return {
        ...baseStyles,
        backgroundColor: getDesignColor('primary.500'),
        color: getDesignColor('text.inverse'),
        borderColor: getDesignColor('primary.500'),
        '&:hover': {
          backgroundColor: getDesignColor('primary.600'),
          borderColor: getDesignColor('primary.600'),
        },
      };
    case 'secondary':
      return {
        ...baseStyles,
        backgroundColor: getDesignColor('secondary.100'),
        color: getDesignColor('secondary.700'),
        borderColor: getDesignColor('secondary.200'),
        '&:hover': {
          backgroundColor: getDesignColor('secondary.200'),
          borderColor: getDesignColor('secondary.300'),
        },
      };
    case 'outline':
      return {
        ...baseStyles,
        backgroundColor: 'transparent',
        color: getDesignColor('primary.500'),
        borderColor: getDesignColor('primary.500'),
        '&:hover': {
          backgroundColor: getDesignColor('primary.500'),
          color: getDesignColor('text.inverse'),
        },
      };
    case 'ghost':
      return {
        ...baseStyles,
        backgroundColor: 'transparent',
        color: getDesignColor('text.secondary'),
        borderColor: 'transparent',
        '&:hover': {
          backgroundColor: getDesignColor('secondary.100'),
          color: getDesignColor('text.primary'),
        },
      };
    default:
      return baseStyles;
  }
};

/**
 * Generate CSS object for a card component
 * @param variant - Card variant
 * @returns CSS object
 */
export const generateCardStyles = (variant: 'default' | 'elevated' | 'outlined' = 'default') => {
  const baseStyles = {
    backgroundColor: getDesignColor('background.primary'),
    borderRadius: getBorderRadius('lg'),
    transition: getTransition('normal'),
  };

  switch (variant) {
    case 'elevated':
      return {
        ...baseStyles,
        boxShadow: getShadow('lg'),
        '&:hover': {
          boxShadow: getShadow('xl'),
          transform: 'translateY(-2px)',
        },
      };
    case 'outlined':
      return {
        ...baseStyles,
        border: `1px solid ${getDesignColor('border.light')}`,
        '&:hover': {
          borderColor: getDesignColor('border.medium'),
        },
      };
    default:
      return {
        ...baseStyles,
        border: `1px solid ${getDesignColor('border.light')}`,
        boxShadow: getShadow('sm'),
        '&:hover': {
          boxShadow: getShadow('md'),
        },
      };
  }
};

// ===== THEME UTILITIES =====

/**
 * Create a theme object with custom colors
 * @param customColors - Custom color overrides
 * @returns Theme object
 */
export const createTheme = (customColors: Partial<typeof designTokens.colors>) => {
  return {
    ...designTokens,
    colors: {
      ...designTokens.colors,
      ...customColors,
    },
  };
};

/**
 * Export design tokens for direct access
 */
export { designTokens };

// ===== TYPE EXPORTS =====
export type {
  ColorToken,
  TypographyToken,
  SpacingToken,
  BorderRadiusToken,
  ShadowToken,
  TransitionToken,
  ZIndexToken,
} from '../design-tokens'; 