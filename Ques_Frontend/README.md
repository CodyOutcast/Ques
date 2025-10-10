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

## �� 最新功能更新 - Whisper消息系统

### 功能概述
实现了完整的搜索页面卡片右滑发送whisper消息功能，用户可以通过右滑卡片向其他用户发送包含完整档案信息的whisper消息。

### 核心功能
- **卡片右滑发送Whisper**: 在搜索结果中右滑用户卡片即可发送whisper消息
- **完整档案信息**: whisper消息包含发送者的完整档案信息（技能、项目、目标、微信号等）
- **智能匹配解释**: 自动包含AI生成的匹配解释
- **微信ID管理**: 支持在设置中管理个人微信ID
- **自定义消息**: Pro用户可设置自定义whisper消息模板

### 技术实现

#### 新增服务
- `whisperService.ts`: 完整的whisper消息API服务
  - 发送whisper消息
  - 获取收到/发送的whisper消息
  - 回复whisper消息
  - 管理whisper设置

#### 核心文件更新
- `useChatInterface.ts`: 更新卡片右滑逻辑，调用whisper API
- `App.tsx`: UserProfile接口添加wechatId字段
- `SettingsScreen.tsx`: 支持微信ID和自定义消息的本地存储
- `services/index.ts`: 导出新的whisperService

#### API数据结构
```typescript
SendWhisperRequest {
  recipientId: string;
  message?: string;
  senderProfile: {
    // 包含完整的用户档案信息
    id, name, avatar, wechatId, skills, projects, etc.
  };
  context: {
    searchQuery, searchMode, matchExplanation, etc.
  };
}
```

### 使用流程
1. 用户在设置中配置微信ID
2. 在搜索界面进行搜索
3. 右滑感兴趣的用户卡片
4. 系统自动发送包含完整档案的whisper消息
5. 对方收到whisper请求，包含发送者的微信号等联系信息

### 与FriendRequest的区别
- **FriendRequest**: 仅包含基本信息 (recipientId, message, giftReceives)
- **Whisper**: 包含完整的发送者档案信息，便于接收者了解发送者背景

### 本地存储
- `user_wechat_id`: 用户微信ID
- `custom_whisper_message`: 自定义whisper消息模板

这个实现确保了搜索页面的卡片右滑能够发送完整的whisper消息，而不仅仅是添加到本地联系人历史。

## 💳 设置页面接口实现

### 功能概述
完整实现了设置页面的所有后端接口，包括购买receives、计划升级/降级、账户管理等核心功能。

### 新增服务

#### settingsService.ts - 用户设置管理
- **用户设置CRUD**: 获取、更新用户设置信息
- **通知设置**: 管理whisper请求等通知开关
- **用户偏好**: 搜索模式、自动匹配等偏好设置
- **账户操作**: 登出、删除账户、导出数据
- **本地设置管理**: 微信ID、自定义消息的localStorage管理

#### paymentService.ts - 支付和订阅管理
- **购买receives**: 支持微信支付、支付宝、信用卡等支付方式
- **计划升级/降级**: Basic ↔ Pro计划切换
- **交易历史**: 获取用户的所有交易记录
- **支付会话**: 创建支付链接和二维码
- **费用计算**: 自动计算购买和升级费用

### useSettings Hook
创建了完整的React Hook来管理设置页面状态：

```typescript
const {
  // 状态
  userSettings,
  currentPlan,
  receivesLeft,
  isProcessingPayment,
  paymentError,
  
  // 操作
  purchaseReceives,
  changePlan,
  updateNotificationSettings,
  logout,
  deleteAccount,
} = useSettings();
```

### API端点结构
```typescript
// 设置管理
SETTINGS: {
  GET_USER_SETTINGS: '/settings',
  UPDATE_NOTIFICATION_SETTINGS: '/settings/notifications',
  UPDATE_USER_PREFERENCES: '/settings/preferences',
  GET_USER_STATS: '/settings/stats',
},

// 支付管理
PAYMENTS: {
  PURCHASE_RECEIVES: '/payments/receives',
  CHANGE_PLAN: '/payments/plan',
  GET_TRANSACTIONS: '/payments/transactions',
  CREATE_PAYMENT_SESSION: '/payments/session',
},

// 账户管理
ACCOUNT: {
  LOGOUT: '/auth/logout',
  DELETE_ACCOUNT: '/account/delete',
  EXPORT_DATA: '/account/export',
}
```

### 核心功能实现

#### 1. 购买Receives
```typescript
// 购买1-100个receives，每个¥1
await purchaseReceives(amount, 'wechat_pay');
// 自动处理支付跳转和余额更新
```

#### 2. 计划升级
```typescript
// 升级到Pro计划（¥10/月）
await changePlan('pro', 'alipay');
// 降级到Basic计划（免费）
await changePlan('basic');
```

#### 3. 数据类型完整性
- **UserSettings**: 用户完整设置信息
- **Transaction**: 交易历史记录
- **PurchaseReceivesRequest/Response**: 购买请求和响应
- **ChangePlanRequest/Response**: 计划变更数据结构

### 支付集成
- 支持微信支付、支付宝、信用卡
- 自动生成支付链接和二维码
- 处理支付状态回调
- 交易记录和状态跟踪

### 错误处理和用户反馈
- 完善的错误处理机制
- 支付失败自动重试
- 用户友好的错误提示
- 本地数据同步保护

这个实现为设置页面提供了完整的后端支持，用户可以直接进行购买、升级、账户管理等操作。