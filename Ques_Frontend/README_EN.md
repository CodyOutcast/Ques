# Ques Frontend

Ques is the first AI-powered social network designed to connect people based on skills, projects, goals, and mutual interests. This repository contains the React-based frontend application built with Vite and TypeScript.

## 🚀 Project Overview

Ques Frontend is a modern, responsive web application that provides:
- **AI Smart Matching** - Connect users based on compatibility algorithms
- **Comprehensive User Profiles** - Detailed profiles with skills, projects, goals, and institutions
- **Intelligent Chat System** - AI-integrated messaging and recommendation system
- **Notification System** - Friend requests and interaction alerts
- **Contact History** - Track and revisit previous connections
- **Multi-language Support** - Bilingual interface (Chinese/English)
- **Whisper Messages** - Messaging system with complete profile information

## 📁 Project Structure

```
Ques_Frontend/
├── src/
│   ├── components/              # React components
│   │   ├── ui/                 # Reusable UI components (shadcn/ui)
│   │   │   ├── button.tsx, input.tsx, card.tsx...  # Base components
│   │   │   ├── dialog.tsx, drawer.tsx, sheet.tsx   # Dialog components
│   │   │   ├── loading.tsx, error.tsx             # State components
│   │   │   └── ... (50+ components)
│   │   ├── BottomNavigation.tsx          # Bottom navigation bar
│   │   ├── ChatCards.tsx                 # Chat card display
│   │   ├── ChatInterface.tsx             # Chat interface (local version)
│   │   ├── ChatInterfaceAPI.tsx          # Chat interface (API integrated)
│   │   ├── ContactHistory.tsx            # Contact history
│   │   ├── NotificationPanel.tsx         # Notification panel
│   │   ├── PersonReceivesBar.tsx         # Personal receives status bar
│   │   ├── PhysicsTagContainer.tsx       # Physics engine tag container
│   │   ├── ProfileSetupWizard.tsx        # Profile setup wizard (local)
│   │   ├── ProfileSetupWizardAPI.tsx     # Profile setup wizard (API)
│   │   ├── ProfileView.tsx               # Profile view
│   │   ├── ReceivesBar.tsx               # Receives status bar
│   │   ├── SettingsScreen.tsx            # Settings page
│   │   └── WelcomeScreen.tsx             # Welcome screen
│   ├── services/                # API service layer
│   │   ├── authService.ts              # Authentication service
│   │   ├── profileService.ts           # Profile management service
│   │   ├── profileAIService.ts         # AI profile optimization service
│   │   ├── chatService.ts              # Chat service
│   │   ├── recommendationService.ts    # Recommendation service
│   │   ├── matchingService.ts          # Matching search service
│   │   ├── swipeService.ts             # Swipe interaction service
│   │   ├── contactService.ts           # Contact service
│   │   ├── notificationService.ts      # Notification service
│   │   ├── whisperService.ts           # Whisper message service
│   │   ├── cardTrackingService.ts      # Card tracking service
│   │   ├── settingsService.ts          # Settings management service
│   │   ├── paymentService.ts           # Payment service
│   │   ├── universityService.ts        # University verification service
│   │   ├── httpClient.ts               # HTTP client
│   │   ├── config.ts                   # API configuration
│   │   └── index.ts                    # Unified exports
│   ├── hooks/                   # Custom React Hooks
│   │   ├── useChatInterface.ts         # Chat interface logic
│   │   ├── useProfileWizard.ts         # Profile setup logic
│   │   └── useSettings.ts              # Settings management logic
│   ├── contexts/                # React Context
│   │   ├── LanguageContext.tsx         # Language switching context
│   │   └── index.ts
│   ├── locales/                 # Internationalization
│   │   ├── zh.ts                       # Chinese translations
│   │   ├── en.ts                       # English translations
│   │   └── index.ts
│   ├── types/                   # TypeScript type definitions
│   │   └── api.ts                      # API-related types
│   ├── styles/
│   │   └── globals.css                 # Global styles
│   ├── assets/                  # Static resources
│   │   ├── icon.jpg                    # App icon
│   │   └── icon_inverted.webp          # Inverted icon
│   ├── App.tsx                  # Main application component
│   ├── main.tsx                 # Application entry point
│   ├── index.css                # Base styles
│   ├── vite-env.d.ts            # Vite type declarations
│   └── Attributions.md          # Third-party attributions
├── build/                       # Production build output
├── node_modules/                # Dependencies
├── index.html                   # HTML template
├── package.json                 # Dependencies and scripts
├── package-lock.json            # Dependency lock file
├── vite.config.ts               # Vite configuration
├── FRONTEND_API_DOCUMENTATION.md     # API documentation (Chinese)
├── FRONTEND_API_DOCUMENTATION_EN.md  # API documentation (English)
└── README.md                    # Project documentation
```

## 🎯 Core Components

### Application Flow Components

#### **WelcomeScreen.tsx** - Welcome Screen
- **Purpose**: First screen shown to new users
- **Features**: App branding display, tagline, get started button
- **Dependencies**: Motion animations, Lucide icons

#### **ProfileSetupWizard.tsx / ProfileSetupWizardAPI.tsx** - Profile Setup Wizard
- **Purpose**: Multi-step profile creation process
- **Features**: 
  - Demographics (name, age, gender, location)
  - Skills and resources input
  - Project portfolio creation
  - Goals and demands specification
  - Institution verification (university email)
- **Versions**: 
  - `ProfileSetupWizard.tsx`: Local state management version
  - `ProfileSetupWizardAPI.tsx`: API integrated version

#### **App.tsx** - Main Application Container
- **Purpose**: Main application container and state management
- **Features**:
  - Screen routing (`welcome`, `profile-setup`, `home`, `profile`, `settings`)
  - Global state management (user profile, contacts, notifications)
  - Contact history and friend request management
  - Plan and receives tracking (basic/pro plans)
  - Multi-language support integration

### User Interface Components

#### **ChatInterface.tsx / ChatInterfaceAPI.tsx** - Chat Interface
- **Purpose**: In-app intelligent chat system
- **Features**:
  - AI conversation and search functionality
  - User recommendation card display
  - Message history management
  - Quote/reply functionality
  - Inside/Global search mode toggle
  - Integrated card tracking feature
- **Versions**:
  - `ChatInterface.tsx`: Local simulation version
  - `ChatInterfaceAPI.tsx`: Full API integration version

#### **ProfileView.tsx** - Profile View
- **Purpose**: User's own profile display and editing
- **Features**:
  - Comprehensive profile overview
  - Edit mode for updating information
  - Profile completeness indicators
  - Section-based organization
  - Physics engine tag display

### Navigation and History Components

#### **BottomNavigation.tsx** - Bottom Navigation Bar
- **Purpose**: Main app navigation bar
- **Features**: 
  - Tab navigation between Home, Profile, and Settings
  - Badge count for unread notifications
  - Responsive design

#### **ContactHistory.tsx** - Contact History
- **Purpose**: View and manage previously contacted users
- **Features**:
  - Contact list with detailed information
  - Report functionality
  - Quote/message options
  - Remove contact option
  - API-integrated contact management

#### **NotificationPanel.tsx** - Notification Panel
- **Purpose**: Friend requests and notification management
- **Features**:
  - Friend request list
  - Accept/decline actions
  - Quote functionality for messaging
  - Real-time notification updates

### Utility Components

#### **SettingsScreen.tsx** - Settings Screen
- **Purpose**: App configuration and user preferences
- **Features**: 
  - Account settings and management
  - WeChat ID configuration
  - Custom Whisper messages
  - Plan upgrade/downgrade
  - Purchase receives
  - Language switching
  - Account actions (logout, delete account)

#### **ChatCards.tsx** - Chat Cards
- **Purpose**: Card display component for chat contexts
- **Features**: Optimized card display for messaging flow with swipe interactions

#### **PersonReceivesBar.tsx & ReceivesBar.tsx** - Receives Status Bar
- **Purpose**: Display and manage user's monthly "receives" (connection attempts)
- **Features**: 
  - Usage tracking
  - Top-up functionality
  - Gift receives to other users

#### **PhysicsTagContainer.tsx** - Physics Tag Container
- **Purpose**: Display interactive tags using physics engine
- **Features**:
  - Matter.js physics engine integration
  - Interactive tag animations
  - Visual display for skills, projects, goals, etc.

### UI Component Library

The `components/ui/` directory contains a comprehensive set of reusable UI components based on **shadcn/ui**:

- **Form Components**: `button.tsx`, `input.tsx`, `textarea.tsx`, `select.tsx`, `checkbox.tsx`, etc.
- **Layout Components**: `card.tsx`, `separator.tsx`, `scroll-area.tsx`, `sheet.tsx`
- **Navigation Components**: `tabs.tsx`, `navigation-menu.tsx`, `breadcrumb.tsx`
- **Feedback Components**: `alert.tsx`, `badge.tsx`, `progress.tsx`, `skeleton.tsx`
- **Overlay Components**: `dialog.tsx`, `popover.tsx`, `tooltip.tsx`, `drawer.tsx`
- **State Components**: `loading.tsx`, `error.tsx` - Custom loading and error display components

## 🛠️ Technology Stack

### Core Technologies
- **React 18.3.1** - UI library with hooks and functional components
- **TypeScript** - Type-safe JavaScript development
- **Vite 6.3.5** - Fast build tool and development server
- **Motion (Framer Motion)** - Advanced animation and gesture library

### UI Framework
- **Radix UI** - Accessible, unstyled UI primitives
  - 20+ Radix UI component packages (Dialog, Dropdown, Select, Tabs, etc.)
- **shadcn/ui** - Reusable component system built on Radix UI
- **Tailwind CSS** - Utility-first CSS framework (via Vite configuration)
- **Lucide React 0.487.0** - Beautiful, customizable icon library

### Key Libraries
- **React Hook Form 7.55.0** - High-performance forms with validation
- **React Day Picker 8.10.1** - Date picker component
- **Recharts 2.15.2** - Data visualization charting library
- **CMDK 1.1.1** - Command palette component
- **Sonner 2.0.3** - Toast notification system
- **Next Themes 0.4.6** - Theme switching functionality
- **Matter.js 0.20.0** - 2D physics engine (for tag animations)
- **Embla Carousel React 8.6.0** - Carousel component
- **Input OTP 1.4.2** - OTP input component
- **Vaul 1.1.2** - Drawer component
- **Class Variance Authority 0.7.1** - CSS class name management
- **Tailwind Merge** - Tailwind class name merging utility
- **CLSX** - Conditional class name utility

## 📱 Features

### User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations**: Motion-powered transitions and interactions
- **Intuitive Navigation**: Bottom tab navigation with clear visual feedback
- **Multi-language Support**: Complete bilingual interface (Chinese/English)
- **Physics Engine Interaction**: Matter.js-powered interactive tag display

### Core Functionality

#### 1. Profile Management
- **Complete User Profiles**: Comprehensive profile system with multiple data types
- **AI Profile Optimization**: Intelligent profile enhancement and optimization suggestions
- **University Email Verification**: Institution identity verification system
- **WeChat ID Integration**: Contact information management

#### 2. AI Smart Matching
- **Intelligent Recommendation Algorithm**: Algorithm-based user recommendations with match scores
- **Match Explanation**: AI-generated match reasoning and compatibility analysis
- **Inside/Global Search**: Dual-mode search system
- **Advanced Filtering**: Advanced search based on location, skills, projects, etc.

#### 3. Social Interactions
- **Swipe Connections**: Tinder-like swipe gesture interactions
- **Whisper Messages**: Messaging system with complete profile information
- **Friend Requests**: Send and manage friend requests
- **Contact Management**: History tracking, reporting, and contact organization
- **Card Tracking**: Real-time tracking of currently viewed recommendation cards

#### 4. Chat System
- **AI Conversations**: Intelligent chat assistant to help find connections
- **Real-time Recommendations**: Real-time user recommendations based on conversation content
- **Message History**: Complete chat history management
- **Quote Functionality**: Ability to quote contacts and messages

#### 5. Plan Management
- **Basic/Pro Plans**: Two-tier subscription system
- **Receives Tracking**: Monthly connection attempt management
- **Online Payment**: Integrated WeChat Pay, Alipay, credit card
- **Plan Upgrade/Downgrade**: Flexible subscription management

### Data Structure
```typescript
interface UserProfile {
  // Demographics
  profilePhoto?: string;
  name: string;
  age: string;
  gender: string;
  location: string;
  hobbies: string[];
  languages: string[];
  oneSentenceIntro?: string;
  
  // Professional Information
  skills: string[];
  resources: string[];
  
  // Projects
  projects: { 
    title: string; 
    role: string; 
    description: string; 
    referenceLinks: string[] 
  }[];
  
  // Goals & Demands
  goals: string[];
  demands: string[];
  
  // Institutions
  institutions: { 
    name: string; 
    role: string; 
    description: string; 
    email?: string;
    verified: boolean;
  }[];
  
  // University
  university?: {
    name: string;
    verified: boolean;
  };
  
  // Contact & Social
  wechatId?: string;
  
  // Legacy fields for backward compatibility
  bio?: string;
  expertise?: { skill: string; level: string; years: string }[];
  interests?: string[];
  education?: string;
  experience?: string;
  availability?: string;
  preferences?: string[];
  values?: string[];
}
```

## 🚀 Setup Guide

### Prerequisites
- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager
- **Git** for version control

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ques/Ques_Frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment variables (optional)**
   ```bash
   # Create .env.local file
   cp .env.example .env.local
   
   # Edit .env.local file
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_APP_MODE=development
   VITE_APP_DEBUG=true
   ```

4. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open in browser**
   - Navigate to `http://localhost:3000`
   - The app will automatically reload when you make changes

### Production Build

1. **Create production build**
   ```bash
   npm run build
   # or
   yarn build
   ```

2. **Build output**
   - The `build/` directory contains production-ready files
   - Deploy to any static hosting service (Vercel, Netlify, etc.)

### Development Workflow

1. **Code Structure**: Follow the existing component organization
2. **Styling**: Use Tailwind CSS classes and the established design system
3. **Components**: Create new components in `src/components/`
4. **UI Components**: Use existing shadcn/ui components from `src/components/ui/`
5. **API Services**: Add new API services in `src/services/`
6. **Custom Hooks**: Create reusable logic in `src/hooks/`
7. **Internationalization**: Add translation strings in `src/locales/`
8. **Type Safety**: Always use TypeScript interfaces for component props and data structures

### Configuration

#### Vite Configuration (`vite.config.ts`)
- **Plugins**: React SWC for fast compilation
- **Aliases**: `@` points to `src/` directory
- **Dependency Aliases**: Version-specific package alias mappings
- **Server**: Configured to run on port 3000, allows LAN access
- **Build**: Outputs to `build/` directory

#### API Configuration (`src/services/config.ts`)
- **Base URL**: Read from environment variables
- **Endpoint Definitions**: Centralized configuration of all API endpoints
- **Timeout Settings**: Request timeout configuration

#### Language Configuration (`src/contexts/LanguageContext.tsx`)
- **Supported Languages**: Chinese (zh) and English (en)
- **Default Language**: English
- **Persistence**: Language selection saved in localStorage

## 🎨 Design Philosophy

### Principles
- **User-Centric**: Prioritize user experience and intuitive interactions
- **Accessibility**: Follow WCAG guidelines and use semantic HTML
- **High Performance**: Optimize for fast loading and smooth animations
- **Consistency**: Maintain design consistency across all screens
- **Mobile-First**: Design for mobile devices, then scale up to desktop
- **Internationalization**: Global design supporting multiple languages

### Visual Design
- **Clean Interface**: Minimal, uncluttered design with clear hierarchy
- **Card-Based Layout**: Consistent card components for content organization
- **Smooth Animations**: Enhance UX through purposeful motion design
- **Intuitive Icons**: Use Lucide icons for clear visual communication
- **Physics Interaction**: Matter.js-powered natural physics interactions

## 🔗 API Integration

### Backend API Integration
The frontend is fully prepared for backend API integration, including:

#### Authentication and User Management
- `authService.ts` - User registration, login, logout
- `profileService.ts` - Profile CRUD operations
- `universityService.ts` - University email verification

#### Social Features
- `chatService.ts` - AI chat and conversation management
- `recommendationService.ts` - Intelligent recommendation algorithms
- `matchingService.ts` - Advanced search and matching
- `swipeService.ts` - Swipe interaction tracking
- `whisperService.ts` - Whisper message system
- `contactService.ts` - Contact management
- `notificationService.ts` - Notifications and friend requests

#### Payment and Subscriptions
- `paymentService.ts` - Payment processing, subscription management
- `settingsService.ts` - User settings and preferences

#### Utility Features
- `cardTrackingService.ts` - Card browsing tracking
- `profileAIService.ts` - AI profile optimization

### API Endpoint Examples
For detailed API documentation, please refer to:
- Chinese documentation: `FRONTEND_API_DOCUMENTATION.md`
- English documentation: `FRONTEND_API_DOCUMENTATION_EN.md`

Main endpoint categories:
```typescript
// Authentication
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout

// Profile Management
GET /api/profile
PUT /api/profile
POST /api/profile/avatar

// Chat and Recommendations
POST /api/chat/message
GET /api/recommendations
POST /api/matching/search

// Social Interactions
POST /api/swipe/right
POST /api/swipe/left
POST /api/whisper/send
GET /api/contacts

// Notifications
GET /api/notifications/friend-requests
POST /api/notifications/friend-request
GET /api/notifications/receives

// Payments
POST /api/payments/receives
POST /api/payments/plan
GET /api/payments/transactions
```

## 📋 Development Status

### Completed Features ✅
- ✅ User onboarding and profile setup
- ✅ AI chat system
- ✅ Contact history management
- ✅ Notification system UI
- ✅ Responsive design
- ✅ Component library integration
- ✅ Complete API service layer
- ✅ Whisper message system
- ✅ Card tracking feature
- ✅ Multi-language support (Chinese/English)
- ✅ University email verification
- ✅ Physics engine tag display
- ✅ Payment integration (WeChat, Alipay, credit card)
- ✅ Subscription plan management
- ✅ Custom Hooks (useChatInterface, useProfileWizard, useSettings, etc.)

### In Progress 🚧
- 🔄 Full backend API integration and testing
- 🔄 Real-time message push
- 🔄 WebSocket connection
- 🔄 Push notifications
- 🔄 Advanced search optimization

### Future Enhancements 🔮
- 📱 PWA support
- 🔔 Browser push notifications
- 👥 Group conversations
- 📸 Media sharing
- 📹 Video call integration
- 📊 Analytics dashboard
- 🤖 More AI features
- 🌐 More language support

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Code Style
- Use TypeScript for all new code
- Follow existing naming conventions
- Add JSDoc comments for complex functions
- Follow React best practices and hooks patterns
- Keep components single-responsibility
- Write reusable code

### Commit Convention
- feat: New feature
- fix: Bug fix
- docs: Documentation updates
- style: Code formatting
- refactor: Code refactoring
- test: Testing related
- chore: Build or tooling related

## 📚 Related Documentation

### API Documentation
- **Chinese**: `FRONTEND_API_DOCUMENTATION.md` - Complete API integration documentation
- **English**: `FRONTEND_API_DOCUMENTATION_EN.md` - Complete API integration documentation

### Service Documentation
- `src/services/SET_UP_README.md` - API service setup guide
- `src/services/CHAT_API_README.md` - Chat API usage documentation
- `src/services/CARD_TRACKING_README.md` - Card tracking feature documentation
- `src/services/CARD_TRACKING_API_REFERENCE.md` - Card tracking API reference
- `src/services/PROFILE_API_USAGE_EXAMPLES.md` - Profile API usage examples
- `src/services/SWIPE_API_USAGE_EXAMPLES.md` - Swipe API usage examples

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details

## 🙏 Acknowledgments

- **shadcn/ui** - Beautiful, accessible component library
- **Radix UI** - Unstyled, accessible UI primitives
- **Lucide** - Beautiful icon library
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Next generation frontend tooling
- **Motion (Framer Motion)** - Powerful animation library
- **Matter.js** - 2D physics engine

---

用 ❤️ 构建，通过 AI 驱动的社交网络连接人们。

Built with ❤️ for connecting people through AI-powered social networking.

