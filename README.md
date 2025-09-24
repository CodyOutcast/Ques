# Ques Frontend

Ques is the first AI-powered social network designed to connect people based on skills, projects, goals, and mutual interests. This repository contains the React-based frontend application built with Vite and TypeScript.

## 🚀 Project Overview

Ques Frontend is a modern, responsive web application that provides:
- **AI-powered matchmaking** - Connect with people based on compatibility algorithms
- **Swipeable card interface** - Tinder-like interaction for discovering connections
- **Comprehensive user profiles** - Detailed profiles with skills, projects, goals, and institutions
- **Real-time chat system** - Integrated messaging with contacts
- **Notification system** - Friend requests and interaction alerts
- **Contact history** - Track and revisit previous connections

## 📁 Project Structure

```
frontend/Ques/Ques_Frontend/
├── src/
│   ├── components/           # React components
│   │   ├── ui/              # Reusable UI components (shadcn/ui)
│   │   ├── BottomNavigation.tsx
│   │   ├── ChatCards.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── ContactHistory.tsx
│   │   ├── NotificationPanel.tsx
│   │   ├── PersonReceivesBar.tsx
│   │   ├── ProfileSetupWizard.tsx
│   │   ├── ProfileView.tsx
│   │   ├── ReceivesBar.tsx
│   │   ├── SettingsScreen.tsx
│   │   ├── SwipeableCardStack.tsx
│   │   └── WelcomeScreen.tsx
│   ├── styles/
│   │   └── globals.css       # Global styling
│   ├── guidelines/
│   │   └── Guidelines.md     # Design system guidelines
│   ├── App.tsx               # Main application component
│   ├── main.tsx             # Application entry point
│   ├── index.css            # Base styles
│   └── Attributions.md      # Third-party attributions
├── build/                   # Production build output
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
└── README.md               # Original project README
```

## 🎯 Core Components

### Application Flow Components

#### **WelcomeScreen.tsx**
- **Purpose**: First screen shown to new users
- **Features**: App branding, tagline, and get started button
- **Dependencies**: Motion animations, Lucide icons

#### **ProfileSetupWizard.tsx**
- **Purpose**: Multi-step profile creation process
- **Features**: 
  - Demographics (name, age, gender, location)
  - Skills and resources input
  - Project portfolio creation
  - Goals and demands specification
  - Institution verification
- **Navigation**: Step-by-step wizard with validation

#### **App.tsx**
- **Purpose**: Main application container and state management
- **Features**:
  - Screen routing (`welcome`, `profile-setup`, `home`, `profile`, `settings`)
  - Global state for user profile, contacts, notifications
  - Contact history and friend request management
  - Plan and receives tracking (basic/pro plans)

### User Interface Components

#### **SwipeableCardStack.tsx**
- **Purpose**: Main card-swiping interface for discovering connections
- **Features**:
  - Tinder-like swipe gestures (left to ignore, right to connect)
  - Expandable profile cards with detailed information
  - Match score display and reasoning
  - Plan-based receives tracking

#### **ChatInterface.tsx**
- **Purpose**: In-app messaging system
- **Features**:
  - Real-time chat simulation
  - Contact profile preview
  - Message history management
  - Quote/reply functionality

#### **ProfileView.tsx**
- **Purpose**: User's own profile display and editing
- **Features**:
  - Comprehensive profile overview
  - Edit mode for updating information
  - Profile completeness indicators
  - Section-based organization

### Navigation & History Components

#### **BottomNavigation.tsx**
- **Purpose**: Main app navigation bar
- **Features**: Tab-based navigation between Home, Profile, and Settings
- **Notifications**: Badge count for unread notifications

#### **ContactHistory.tsx**
- **Purpose**: View and manage previously contacted users
- **Features**:
  - Contact list with details
  - Report functionality
  - Quote/message options
  - Remove contacts option

#### **NotificationPanel.tsx**
- **Purpose**: Friend requests and notification management
- **Features**:
  - Friend request list
  - Accept/decline actions
  - Quote functionality for messaging

### Utility Components

#### **SettingsScreen.tsx**
- **Purpose**: App configuration and user preferences
- **Features**: Account settings, preferences, and app information

#### **ChatCards.tsx**
- **Purpose**: Alternative card display component for chat contexts
- **Features**: Similar to SwipeableCardStack but optimized for messaging flow

#### **PersonReceivesBar.tsx** & **ReceivesBar.tsx**
- **Purpose**: Display and manage user's monthly "receives" (connection attempts)
- **Features**: 
  - Usage tracking
  - Top-up functionality
  - Gift receives to other users

### UI Component Library

The `components/ui/` directory contains a comprehensive set of reusable UI components based on **shadcn/ui**:

- **Form Components**: `button.tsx`, `input.tsx`, `textarea.tsx`, `select.tsx`, `checkbox.tsx`, etc.
- **Layout Components**: `card.tsx`, `separator.tsx`, `scroll-area.tsx`, `sheet.tsx`
- **Navigation Components**: `tabs.tsx`, `navigation-menu.tsx`, `breadcrumb.tsx`
- **Feedback Components**: `alert.tsx`, `badge.tsx`, `progress.tsx`, `skeleton.tsx`
- **Overlay Components**: `dialog.tsx`, `popover.tsx`, `tooltip.tsx`, `drawer.tsx`

## 🛠️ Technology Stack

### Core Technologies
- **React 18.3.1** - UI library with hooks and functional components
- **TypeScript** - Type-safe JavaScript development
- **Vite 6.3.5** - Fast build tool and development server
- **Motion (Framer Motion)** - Advanced animations and gestures

### UI Framework
- **Radix UI** - Accessible, unstyled UI primitives
- **shadcn/ui** - Re-usable components built on Radix UI
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful, customizable icons

### Key Libraries
- **React Hook Form 7.55.0** - Performant forms with validation
- **React Day Picker 8.10.1** - Date selection component
- **Recharts 2.15.2** - Charting library for data visualization
- **CMDK 1.1.1** - Command palette component
- **Sonner 2.0.3** - Toast notifications
- **Next Themes 0.4.6** - Theme switching functionality

## 📱 Features

### User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations**: Motion-powered transitions and interactions
- **Intuitive Navigation**: Bottom tab navigation with clear visual feedback
- **Dark/Light Mode**: Theme switching capability (configured but not fully implemented)

### Core Functionality
- **Profile Management**: Comprehensive user profiles with multiple data types
- **AI Matching**: Algorithm-based user recommendations with match scores
- **Social Interactions**: Swipe-to-connect, messaging, and friend requests
- **Contact Management**: History tracking, reporting, and contact organization
- **Plan Management**: Basic/Pro plans with receives tracking

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
  
  // Professional
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
}
```

## 🚀 Setup Guide

### Prerequisites
- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ques/frontend/Ques/Ques_Frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open in browser**
   - Navigate to `http://localhost:5173`
   - The app will automatically reload when you make changes

### Production Build

1. **Create production build**
   ```bash
   npm run build
   # or
   yarn build
   ```

2. **Preview production build**
   ```bash
   npm run preview
   # or
   yarn preview
   ```

3. **Deploy**
   - The `build/` directory contains the production-ready files
   - Deploy to any static hosting service (Vercel, Netlify, etc.)

### Development Workflow

1. **Code Structure**: Follow the existing component organization
2. **Styling**: Use Tailwind CSS classes and the established design system
3. **Components**: Create new components in `src/components/`
4. **UI Components**: Use existing shadcn/ui components from `src/components/ui/`
5. **State Management**: Use React hooks and prop drilling (consider Redux for complex state)
6. **Type Safety**: Always use TypeScript interfaces for component props and data structures

### Configuration

#### Vite Configuration (`vite.config.ts`)
- **Plugins**: React SWC for fast compilation
- **Aliases**: Path aliases for cleaner imports
- **Dependency Aliases**: Version-specific package aliases

#### Design System
- **Guidelines**: See `src/guidelines/Guidelines.md`
- **Colors**: Tailwind CSS default palette with custom extensions
- **Typography**: System fonts with proper scaling
- **Components**: shadcn/ui design system components

## 🎨 Design Philosophy

### Principles
- **User-Centric**: Prioritize user experience and intuitive interactions
- **Accessible**: Follow WCAG guidelines and use semantic HTML
- **Performant**: Optimize for fast loading and smooth animations  
- **Consistent**: Maintain design consistency across all screens
- **Mobile-First**: Design for mobile and scale up to desktop

### Visual Design
- **Clean Interface**: Minimal, uncluttered design with clear hierarchy
- **Card-Based Layout**: Consistent card components for content organization
- **Smooth Animations**: Enhance UX with purposeful motion design
- **Intuitive Icons**: Lucide icons for clear visual communication

## 🔗 Integration Points

### Backend API (Future)
The frontend is prepared for backend integration with:
- User authentication and registration
- Profile data persistence
- Real-time messaging
- Recommendation algorithms
- Notification systems

### Expected API Endpoints
```
POST /api/auth/register
POST /api/auth/login
GET /api/user/profile
PUT /api/user/profile
GET /api/recommendations
POST /api/connections
GET /api/chat/messages
POST /api/chat/messages
GET /api/notifications
```

## 📋 Development Status

### Completed Features ✅
- User onboarding and profile setup
- Swipeable card interface  
- Basic messaging UI
- Contact history management
- Notification system UI
- Responsive design
- Component library integration

### In Progress 🚧
- Backend API integration
- Real-time messaging
- Advanced matching algorithms
- User authentication
- Data persistence

### Future Enhancements 🔮
- Push notifications
- Advanced search and filters
- Group conversations
- Media sharing
- Video calls integration
- Analytics dashboard

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
- Use Prettier for code formatting
- Follow React best practices and hooks patterns

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **shadcn/ui** - Beautiful, accessible component library
- **Radix UI** - Unstyled, accessible UI primitives  
- **Lucide** - Beautiful icon library
- **Unsplash** - High-quality photos for user avatars
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Next generation frontend tooling

---

Built with ❤️ for connecting people through AI-powered social networking.