# Design System Documentation

This document explains how to use and customize the design system for the Tinder-like project partner finder app.

## 🎨 Overview

The design system is built around a centralized token system that makes it easy to:
- Change colors globally
- Update typography consistently
- Maintain design consistency across components
- Create new themes quickly

## 📁 File Structure

```
Dynamic Card Swiping Interface/
├── design-tokens.ts          # Single source of truth for all design values
├── utils/design-system.ts    # Utility functions for accessing design tokens
├── styles/globals.css        # Global CSS with CSS custom properties
├── tailwind.config.js        # Tailwind configuration using design tokens
└── DESIGN_SYSTEM.md          # This documentation file
```

## 🎯 Quick Start

### Changing Colors

To change the primary brand color, edit `design-tokens.ts`:

```typescript
// In design-tokens.ts
colors: {
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#0055f7', // ← Change this main brand color
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554',
  },
  // ... other colors
}
```

### Changing Typography

To change fonts, edit `design-tokens.ts`:

```typescript
// In design-tokens.ts
typography: {
  fonts: {
    primary: ['Your Font', 'Inter', 'system-ui', 'sans-serif'], // ← Change this
    secondary: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
  },
  // ... other typography settings
}
```

## 🎨 Color System

### Color Categories

1. **Primary Colors** - Main brand colors
2. **Secondary Colors** - Supporting colors
3. **Accent Colors** - Highlight colors
4. **Success Colors** - Positive states
5. **Warning Colors** - Caution states
6. **Error Colors** - Error states
7. **Neutral Colors** - Grays and whites
8. **Semantic Colors** - Background, text, border colors

### Color Scale

Each color category follows a 50-950 scale:
- `50` - Lightest shade (backgrounds, borders)
- `100-400` - Light shades
- `500` - Base color
- `600-900` - Dark shades
- `950` - Darkest shade

### Usage Examples

```typescript
// In React components
import { getDesignColor } from './utils/design-system';

// Get specific colors
const primaryColor = getDesignColor('primary.500');
const textColor = getDesignColor('text.primary');
const borderColor = getDesignColor('border.light');

// In Tailwind classes
<div className="bg-primary-500 text-text-primary border-border-light">
  Content
</div>
```

## 📝 Typography System

### Font Families

- **Primary** - Main brand font (Instrument Sans)
- **Secondary** - Supporting font (Inter)
- **Mono** - Code font (JetBrains Mono)

### Font Sizes

- `xs` - 0.75rem (12px)
- `sm` - 0.875rem (14px)
- `base` - 1rem (16px)
- `lg` - 1.125rem (18px)
- `xl` - 1.25rem (20px)
- `2xl` - 1.5rem (24px)
- `3xl` - 1.875rem (30px)
- `4xl` - 2.25rem (36px)
- `5xl` - 3rem (48px)
- `6xl` - 3.75rem (60px)

### Font Weights

- `light` - 300
- `normal` - 400
- `medium` - 500
- `semibold` - 600
- `bold` - 700
- `extrabold` - 800

### Usage Examples

```typescript
// In React components
import { getFontFamily, getFontSize, getFontWeight } from './utils/design-system';

const styles = {
  fontFamily: getFontFamily('primary'),
  fontSize: getFontSize('lg'),
  fontWeight: getFontWeight('semibold'),
};

// In Tailwind classes
<h1 className="font-primary text-2xl font-semibold">
  Heading
</h1>
```

## 📏 Spacing System

### Spacing Scale

- `0` - 0
- `1` - 0.25rem (4px)
- `2` - 0.5rem (8px)
- `3` - 0.75rem (12px)
- `4` - 1rem (16px)
- `5` - 1.25rem (20px)
- `6` - 1.5rem (24px)
- `8` - 2rem (32px)
- `10` - 2.5rem (40px)
- `12` - 3rem (48px)
- `16` - 4rem (64px)
- `20` - 5rem (80px)
- `24` - 6rem (96px)
- `32` - 8rem (128px)

### Usage Examples

```typescript
// In React components
import { getSpacing } from './utils/design-system';

const styles = {
  padding: getSpacing(4),
  margin: getSpacing(6),
};

// In Tailwind classes
<div className="p-4 m-6">
  Content
</div>
```

## 🎭 Component Styles

### Pre-built Component Classes

The design system includes pre-built CSS classes for common components:

#### Buttons
```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-outline">Outline Button</button>
```

#### Cards
```html
<div class="card">Default Card</div>
<div class="card card-elevated">Elevated Card</div>
<div class="card card-outlined">Outlined Card</div>
```

#### Inputs
```html
<input class="input" placeholder="Enter text..." />
```

#### Badges
```html
<span class="badge badge-primary">Primary Badge</span>
<span class="badge badge-success">Success Badge</span>
<span class="badge badge-warning">Warning Badge</span>
<span class="badge badge-error">Error Badge</span>
```

## 🔧 Utility Functions

### Color Utilities

```typescript
import { 
  getDesignColor, 
  generateColorPalette, 
  getColorContrast,
  getContrastingTextColor 
} from './utils/design-system';

// Get colors
const color = getDesignColor('primary.500');

// Generate palette from base color
const palette = generateColorPalette('#ff0000');

// Check color contrast
const contrast = getColorContrast('#ffffff'); // 'light' or 'dark'

// Get contrasting text color
const textColor = getContrastingTextColor('#000000'); // '#ffffff'
```

### Typography Utilities

```typescript
import { 
  getFontFamily, 
  getFontSize, 
  getFontWeight,
  getLineHeight 
} from './utils/design-system';

const fontFamily = getFontFamily('primary');
const fontSize = getFontSize('lg');
const fontWeight = getFontWeight('semibold');
const lineHeight = getLineHeight('tight');
```

### Style Generators

```typescript
import { 
  generateButtonStyles, 
  generateCardStyles 
} from './utils/design-system';

// Generate button styles
const buttonStyles = generateButtonStyles('primary');

// Generate card styles
const cardStyles = generateCardStyles('elevated');
```

## 🌙 Dark Mode

The design system includes dark mode support through CSS custom properties:

```css
/* Light mode (default) */
:root {
  --color-background-primary: #ffffff;
  --color-text-primary: #0f172a;
}

/* Dark mode */
.dark {
  --color-background-primary: #0f172a;
  --color-text-primary: #f8fafc;
}
```

To enable dark mode, add the `dark` class to your HTML element:

```javascript
// Toggle dark mode
document.documentElement.classList.toggle('dark');
```

## 🎨 Creating Custom Themes

### Method 1: Modify Design Tokens

Edit `design-tokens.ts` directly to change the entire theme:

```typescript
export const designTokens = {
  colors: {
    primary: {
      500: '#your-custom-color', // Change main brand color
      // ... other shades
    },
    // ... other colors
  },
  // ... other tokens
};
```

### Method 2: Create Theme Function

Use the `createTheme` function to create custom themes:

```typescript
import { createTheme } from './utils/design-system';

const customTheme = createTheme({
  primary: {
    500: '#ff6b6b',
    600: '#ee5a52',
    // ... other shades
  },
  accent: {
    500: '#4ecdc4',
    // ... other shades
  },
});
```

## 📱 Responsive Design

The design system includes responsive breakpoints:

```typescript
import { getBreakpoint, isBreakpoint } from './utils/design-system';

const mdBreakpoint = getBreakpoint('md'); // '768px'
const isMobile = isBreakpoint('md'); // false if screen >= 768px
```

### Breakpoints

- `sm` - 640px
- `md` - 768px
- `lg` - 1024px
- `xl` - 1280px
- `2xl` - 1536px

## 🎯 Best Practices

### 1. Use Design Tokens

Always use design tokens instead of hardcoded values:

```typescript
// ✅ Good
const color = getDesignColor('primary.500');

// ❌ Bad
const color = '#0055f7';
```

### 2. Use Tailwind Classes

Prefer Tailwind classes that use design tokens:

```html
<!-- ✅ Good -->
<div class="bg-primary-500 text-text-primary p-4">

<!-- ❌ Bad -->
<div class="bg-blue-500 text-black p-4">
```

### 3. Maintain Consistency

Use the same spacing, typography, and color patterns throughout the app:

```typescript
// ✅ Consistent spacing
<div class="p-4 m-6">
<div class="p-4 m-6">

// ❌ Inconsistent spacing
<div class="p-4 m-6">
<div class="p-5 m-8">
```

### 4. Use Semantic Colors

Use semantic color names instead of specific colors:

```typescript
// ✅ Good
const backgroundColor = getDesignColor('background.primary');
const textColor = getDesignColor('text.primary');

// ❌ Bad
const backgroundColor = getDesignColor('neutral.50');
const textColor = getDesignColor('neutral.900');
```

## 🔄 Migration Guide

### From Hardcoded Values

If you have existing components with hardcoded values, here's how to migrate:

```typescript
// Before
const styles = {
  backgroundColor: '#0055f7',
  color: '#ffffff',
  padding: '16px',
  fontSize: '18px',
};

// After
import { getDesignColor, getSpacing, getFontSize } from './utils/design-system';

const styles = {
  backgroundColor: getDesignColor('primary.500'),
  color: getDesignColor('text.inverse'),
  padding: getSpacing(4),
  fontSize: getFontSize('lg'),
};
```

### From Tailwind Arbitrary Values

```html
<!-- Before -->
<div class="bg-[#0055f7] text-[#ffffff] p-[16px] text-[18px]">

<!-- After -->
<div class="bg-primary-500 text-text-inverse p-4 text-lg">
```

## 🐛 Troubleshooting

### Colors Not Updating

1. Check that you're using design tokens, not hardcoded values
2. Ensure Tailwind is rebuilding after changes
3. Clear browser cache

### Typography Not Working

1. Verify font imports in `globals.css`
2. Check that font families are correctly specified
3. Ensure font files are accessible

### Build Errors

1. Check TypeScript types in `design-tokens.ts`
2. Verify import paths in `tailwind.config.js`
3. Ensure all dependencies are installed

## 📚 Additional Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Design Tokens](https://www.designtokens.org/)
- [Figma Design Tokens](https://www.figma.com/plugin-docs/design-tokens/)

## 🤝 Contributing

When adding new design tokens or modifying existing ones:

1. Update `design-tokens.ts`
2. Update `tailwind.config.js` if needed
3. Update `globals.css` if needed
4. Update this documentation
5. Test across different components
6. Ensure dark mode compatibility

---

This design system is designed to be flexible and maintainable. By following these guidelines, you can easily customize the app's appearance while maintaining consistency and accessibility. 