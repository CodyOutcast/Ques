# Ques Frontend

Ques 是首个AI驱动的社交网络，旨在基于技能、项目、目标和共同兴趣连接人们。本仓库包含使用 Vite 和 TypeScript 构建的 React 前端应用程序。

## 🚀 项目概述

Ques Frontend 是一个现代化、响应式的 Web 应用，提供：
- **AI 智能匹配** - 基于兼容性算法连接用户
- **卡片滑动界面** - 类似 Tinder 的交互方式发现连接
- **全面的用户档案** - 包含技能、项目、目标和机构的详细档案
- **智能聊天系统** - 集成 AI 的消息和推荐系统
- **通知系统** - 好友请求和交互提醒
- **联系人历史** - 追踪并重访之前的连接
- **多语言支持** - 中文/英文双语界面
- **Whisper 消息** - 包含完整档案信息的消息系统

## 📁 项目结构

```
Ques_Frontend/
├── src/
│   ├── components/              # React 组件
│   │   ├── ui/                 # 可复用 UI 组件 (shadcn/ui)
│   │   │   ├── button.tsx, input.tsx, card.tsx...  # 基础组件
│   │   │   ├── dialog.tsx, drawer.tsx, sheet.tsx   # 对话框组件
│   │   │   ├── loading.tsx, error.tsx             # 状态组件
│   │   │   └── ... (50+ 组件)
│   │   ├── BottomNavigation.tsx          # 底部导航栏
│   │   ├── ChatCards.tsx                 # 聊天卡片显示
│   │   ├── ChatInterface.tsx             # 聊天界面（本地版）
│   │   ├── ChatInterfaceAPI.tsx          # 聊天界面（API集成版）
│   │   ├── ContactHistory.tsx            # 联系人历史
│   │   ├── NotificationPanel.tsx         # 通知面板
│   │   ├── PersonReceivesBar.tsx         # 个人receives状态栏
│   │   ├── PhysicsTagContainer.tsx       # 物理引擎标签容器
│   │   ├── ProfileSetupWizard.tsx        # 档案设置向导（本地版）
│   │   ├── ProfileSetupWizardAPI.tsx     # 档案设置向导（API版）
│   │   ├── ProfileView.tsx               # 档案查看
│   │   ├── ReceivesBar.tsx               # Receives 状态栏
│   │   ├── SettingsScreen.tsx            # 设置页面
│   │   ├── SwipeableCardStack.tsx        # 卡片滑动堆栈
│   │   └── WelcomeScreen.tsx             # 欢迎屏幕
│   ├── services/                # API 服务层
│   │   ├── authService.ts              # 认证服务
│   │   ├── profileService.ts           # 档案管理服务
│   │   ├── profileAIService.ts         # AI 档案优化服务
│   │   ├── chatService.ts              # 聊天服务
│   │   ├── recommendationService.ts    # 推荐服务
│   │   ├── matchingService.ts          # 匹配搜索服务
│   │   ├── swipeService.ts             # 滑动交互服务
│   │   ├── contactService.ts           # 联系人服务
│   │   ├── notificationService.ts      # 通知服务
│   │   ├── whisperService.ts           # Whisper消息服务
│   │   ├── cardTrackingService.ts      # 卡片跟踪服务
│   │   ├── settingsService.ts          # 设置管理服务
│   │   ├── paymentService.ts           # 支付服务
│   │   ├── universityService.ts        # 大学验证服务
│   │   ├── httpClient.ts               # HTTP 客户端
│   │   ├── config.ts                   # API 配置
│   │   └── index.ts                    # 统一导出
│   ├── hooks/                   # 自定义 React Hooks
│   │   ├── useChatInterface.ts         # 聊天界面逻辑
│   │   ├── useProfileWizard.ts         # 档案设置逻辑
│   │   ├── useSettings.ts              # 设置管理逻辑
│   │   └── useSwipeActions.ts          # 滑动操作逻辑
│   ├── contexts/                # React Context
│   │   ├── LanguageContext.tsx         # 语言切换上下文
│   │   └── index.ts
│   ├── locales/                 # 国际化翻译
│   │   ├── zh.ts                       # 中文翻译
│   │   ├── en.ts                       # 英文翻译
│   │   └── index.ts
│   ├── types/                   # TypeScript 类型定义
│   │   └── api.ts                      # API 相关类型
│   ├── styles/
│   │   └── globals.css                 # 全局样式
│   ├── assets/                  # 静态资源
│   │   ├── icon.jpg                    # 应用图标
│   │   └── icon_inverted.webp          # 反色图标
│   ├── App.tsx                  # 主应用组件
│   ├── main.tsx                 # 应用入口
│   ├── index.css                # 基础样式
│   ├── vite-env.d.ts            # Vite 类型声明
│   └── Attributions.md          # 第三方归属
├── build/                       # 生产构建输出
├── node_modules/                # 依赖包
├── index.html                   # HTML 模板
├── package.json                 # 依赖和脚本
├── package-lock.json            # 依赖锁定文件
├── vite.config.ts               # Vite 配置
├── FRONTEND_API_DOCUMENTATION.md     # API 文档（中文）
├── FRONTEND_API_DOCUMENTATION_EN.md  # API 文档（英文）
└── README.md                    # 项目说明文档
```

## 🎯 核心组件

### 应用流程组件

#### **WelcomeScreen.tsx** - 欢迎屏幕
- **功能**: 新用户首次看到的屏幕
- **特性**: 应用品牌展示、标语、开始按钮
- **依赖**: Motion 动画、Lucide 图标

#### **ProfileSetupWizard.tsx / ProfileSetupWizardAPI.tsx** - 档案设置向导
- **功能**: 多步骤档案创建流程
- **特性**: 
  - 人口统计信息（姓名、年龄、性别、位置）
  - 技能和资源输入
  - 项目作品集创建
  - 目标和需求说明
  - 机构验证（大学邮箱验证）
- **版本**: 
  - `ProfileSetupWizard.tsx`: 本地状态管理版本
  - `ProfileSetupWizardAPI.tsx`: API 集成版本

#### **App.tsx** - 主应用容器
- **功能**: 主应用容器和状态管理
- **特性**:
  - 屏幕路由 (`welcome`, `profile-setup`, `home`, `profile`, `settings`)
  - 全局状态管理（用户档案、联系人、通知）
  - 联系人历史和好友请求管理
  - 计划和 receives 跟踪（basic/pro 计划）
  - 多语言支持集成

### 用户界面组件

#### **ChatInterface.tsx / ChatInterfaceAPI.tsx** - 聊天界面
- **功能**: 应用内智能聊天系统
- **特性**:
  - AI 对话和搜索功能
  - 用户推荐卡片显示
  - 消息历史管理
  - 引用/回复功能
  - Inside/Global 搜索模式切换
  - 集成卡片跟踪功能
- **版本**:
  - `ChatInterface.tsx`: 本地模拟版本
  - `ChatInterfaceAPI.tsx`: 完整 API 集成版本

#### **SwipeableCardStack.tsx** - 卡片滑动堆栈
- **功能**: 主要的卡片滑动界面用于发现连接
- **特性**:
  - 类似 Tinder 的滑动手势（左滑忽略，右滑发送 Whisper）
  - 可展开的档案卡片，包含详细信息
  - 匹配分数显示和推理
  - 基于计划的 receives 跟踪
  - 集成 Whisper 消息发送

#### **ProfileView.tsx** - 档案查看
- **功能**: 用户自己的档案显示和编辑
- **特性**:
  - 全面的档案概览
  - 编辑模式更新信息
  - 档案完整度指示器
  - 基于分段的组织结构
  - 物理引擎标签显示

### 导航和历史组件

#### **BottomNavigation.tsx** - 底部导航栏
- **功能**: 主应用导航栏
- **特性**: 
  - 在首页、档案和设置之间切换的标签导航
  - 未读通知的徽章计数
  - 响应式设计

#### **ContactHistory.tsx** - 联系人历史
- **功能**: 查看和管理之前联系过的用户
- **特性**:
  - 带详细信息的联系人列表
  - 举报功能
  - 引用/消息选项
  - 删除联系人选项
  - API 集成的联系人管理

#### **NotificationPanel.tsx** - 通知面板
- **功能**: 好友请求和通知管理
- **特性**:
  - 好友请求列表
  - 接受/拒绝操作
  - 用于消息的引用功能
  - 实时通知更新

### 实用组件

#### **SettingsScreen.tsx** - 设置屏幕
- **功能**: 应用配置和用户偏好
- **特性**: 
  - 账户设置和管理
  - 微信 ID 配置
  - 自定义 Whisper 消息
  - 计划升级/降级
  - 购买 receives
  - 语言切换
  - 账户操作（登出、删除账户）

#### **ChatCards.tsx** - 聊天卡片
- **功能**: 用于聊天上下文的替代卡片显示组件
- **特性**: 类似于 SwipeableCardStack 但针对消息流程优化

#### **PersonReceivesBar.tsx & ReceivesBar.tsx** - Receives 状态栏
- **功能**: 显示和管理用户的月度 "receives"（连接尝试）
- **特性**: 
  - 使用跟踪
  - 充值功能
  - 向其他用户赠送 receives

#### **PhysicsTagContainer.tsx** - 物理引擎标签容器
- **功能**: 使用物理引擎显示交互式标签
- **特性**:
  - Matter.js 物理引擎集成
  - 交互式标签动画
  - 用于技能、项目、目标等的可视化显示

### UI 组件库

`components/ui/` 目录包含基于 **shadcn/ui** 的全面可复用 UI 组件集：

- **表单组件**: `button.tsx`, `input.tsx`, `textarea.tsx`, `select.tsx`, `checkbox.tsx` 等
- **布局组件**: `card.tsx`, `separator.tsx`, `scroll-area.tsx`, `sheet.tsx`
- **导航组件**: `tabs.tsx`, `navigation-menu.tsx`, `breadcrumb.tsx`
- **反馈组件**: `alert.tsx`, `badge.tsx`, `progress.tsx`, `skeleton.tsx`
- **覆盖组件**: `dialog.tsx`, `popover.tsx`, `tooltip.tsx`, `drawer.tsx`
- **状态组件**: `loading.tsx`, `error.tsx` - 自定义加载和错误显示组件

## 🛠️ 技术栈

### 核心技术
- **React 18.3.1** - 使用 hooks 和函数组件的 UI 库
- **TypeScript** - 类型安全的 JavaScript 开发
- **Vite 6.3.5** - 快速构建工具和开发服务器
- **Motion (Framer Motion)** - 高级动画和手势库

### UI 框架
- **Radix UI** - 可访问的、无样式的 UI 原语组件
  - 20+ Radix UI 组件包（Dialog, Dropdown, Select, Tabs 等）
- **shadcn/ui** - 基于 Radix UI 构建的可复用组件系统
- **Tailwind CSS** - 实用优先的 CSS 框架（通过 Vite 配置）
- **Lucide React 0.487.0** - 美观、可定制的图标库

### 关键库
- **React Hook Form 7.55.0** - 高性能的表单和验证
- **React Day Picker 8.10.1** - 日期选择组件
- **Recharts 2.15.2** - 数据可视化图表库
- **CMDK 1.1.1** - 命令面板组件
- **Sonner 2.0.3** - Toast 通知系统
- **Next Themes 0.4.6** - 主题切换功能
- **Matter.js 0.20.0** - 2D 物理引擎（用于标签动画）
- **Embla Carousel React 8.6.0** - 轮播组件
- **Input OTP 1.4.2** - OTP 输入组件
- **Vaul 1.1.2** - 抽屉组件
- **Class Variance Authority 0.7.1** - CSS 类名管理
- **Tailwind Merge** - Tailwind 类名合并工具
- **CLSX** - 条件类名工具

## 📱 功能特性

### 用户体验
- **响应式设计**: 在桌面、平板和移动设备上无缝工作
- **流畅动画**: Motion 驱动的过渡和交互效果
- **直观导航**: 带有清晰视觉反馈的底部标签导航
- **多语言支持**: 完整的中文/英文双语界面切换
- **物理引擎交互**: Matter.js 驱动的交互式标签显示

### 核心功能

#### 1. 档案管理
- **完整的用户档案**: 包含多种数据类型的综合档案系统
- **AI 档案优化**: 智能档案完善和优化建议
- **大学邮箱验证**: 机构身份验证系统
- **微信 ID 集成**: 联系方式管理

#### 2. AI 智能匹配
- **智能推荐算法**: 基于算法的用户推荐，带有匹配分数
- **匹配解释**: AI 生成的匹配理由和兼容性分析
- **Inside/Global 搜索**: 双模式搜索系统
- **高级筛选**: 基于位置、技能、项目等的高级搜索

#### 3. 社交互动
- **滑动连接**: 类似 Tinder 的滑动手势交互
- **Whisper 消息**: 包含完整档案信息的消息系统
- **好友请求**: 发送和管理好友请求
- **联系人管理**: 历史跟踪、举报和联系人组织
- **卡片跟踪**: 实时跟踪当前查看的推荐卡片

#### 4. 聊天系统
- **AI 对话**: 智能聊天助手帮助查找连接
- **实时推荐**: 基于对话内容的实时用户推荐
- **消息历史**: 完整的聊天历史记录管理
- **引用功能**: 引用联系人和消息的能力

#### 5. 计划管理
- **Basic/Pro 计划**: 双层级订阅系统
- **Receives 跟踪**: 月度连接尝试次数管理
- **在线支付**: 集成微信支付、支付宝、信用卡
- **计划升级/降级**: 灵活的订阅管理

### 数据结构
```typescript
interface UserProfile {
  // 人口统计信息
  profilePhoto?: string;
  name: string;
  age: string;
  gender: string;
  location: string;
  hobbies: string[];
  languages: string[];
  oneSentenceIntro?: string;
  
  // 专业信息
  skills: string[];
  resources: string[];
  
  // 项目
  projects: { 
    title: string; 
    role: string; 
    description: string; 
    referenceLinks: string[] 
  }[];
  
  // 目标和需求
  goals: string[];
  demands: string[];
  
  // 机构
  institutions: { 
    name: string; 
    role: string; 
    description: string; 
    email?: string;
    verified: boolean;
  }[];
  
  // 大学
  university?: {
    name: string;
    verified: boolean;
  };
  
  // 联系方式和社交
  wechatId?: string;
  
  // 向后兼容的遗留字段
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

## 🚀 安装指南

### 前置要求
- **Node.js** (版本 16 或更高)
- **npm** 或 **yarn** 包管理器
- **Git** 用于版本控制

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd Ques/Ques_Frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   # 或
   yarn install
   ```

3. **配置环境变量（可选）**
   ```bash
   # 创建 .env.local 文件
   cp .env.example .env.local
   
   # 编辑 .env.local 文件
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_APP_MODE=development
   VITE_APP_DEBUG=true
   ```

4. **启动开发服务器**
   ```bash
   npm run dev
   # 或
   yarn dev
   ```

5. **在浏览器中打开**
   - 导航到 `http://localhost:3000`
   - 应用会在您进行更改时自动重新加载

### 生产构建

1. **创建生产构建**
   ```bash
   npm run build
   # 或
   yarn build
   ```

2. **构建输出**
   - `build/` 目录包含生产就绪的文件
   - 部署到任何静态托管服务（Vercel、Netlify 等）

### 开发工作流

1. **代码结构**: 遵循现有的组件组织结构
2. **样式**: 使用 Tailwind CSS 类和已建立的设计系统
3. **组件**: 在 `src/components/` 中创建新组件
4. **UI 组件**: 使用 `src/components/ui/` 中现有的 shadcn/ui 组件
5. **API 服务**: 在 `src/services/` 中添加新的 API 服务
6. **自定义 Hooks**: 在 `src/hooks/` 中创建可复用的逻辑
7. **国际化**: 在 `src/locales/` 中添加翻译字符串
8. **类型安全**: 始终为组件 props 和数据结构使用 TypeScript 接口

### 配置

#### Vite 配置 (`vite.config.ts`)
- **插件**: React SWC 用于快速编译
- **别名**: `@` 指向 `src/` 目录
- **依赖别名**: 版本特定的包别名映射
- **服务器**: 配置为在 3000 端口运行，允许局域网访问
- **构建**: 输出到 `build/` 目录

#### API 配置 (`src/services/config.ts`)
- **基础 URL**: 从环境变量读取
- **端点定义**: 所有 API 端点的集中配置
- **超时设置**: 请求超时配置

#### 语言配置 (`src/contexts/LanguageContext.tsx`)
- **支持语言**: 中文 (zh) 和英文 (en)
- **默认语言**: 英文
- **持久化**: 语言选择保存在 localStorage 中

## 🎨 设计理念

### 原则
- **以用户为中心**: 优先考虑用户体验和直观交互
- **可访问性**: 遵循 WCAG 指南，使用语义化 HTML
- **高性能**: 优化快速加载和流畅动画
- **一致性**: 在所有屏幕上保持设计一致性
- **移动优先**: 为移动设备设计，然后扩展到桌面
- **国际化**: 支持多语言的全球化设计

### 视觉设计
- **简洁界面**: 简约、整洁的设计，层次清晰
- **基于卡片的布局**: 一致的卡片组件用于内容组织
- **流畅动画**: 通过有目的的动作设计增强用户体验
- **直观图标**: 使用 Lucide 图标实现清晰的视觉交流
- **物理交互**: Matter.js 驱动的自然物理交互

## 🔗 API 集成

### 后端 API 集成
前端已完全准备好与后端 API 集成，包括：

#### 认证和用户管理
- `authService.ts` - 用户注册、登录、登出
- `profileService.ts` - 档案 CRUD 操作
- `universityService.ts` - 大学邮箱验证

#### 社交功能
- `chatService.ts` - AI 聊天和对话管理
- `recommendationService.ts` - 智能推荐算法
- `matchingService.ts` - 高级搜索和匹配
- `swipeService.ts` - 滑动交互跟踪
- `whisperService.ts` - Whisper 消息系统
- `contactService.ts` - 联系人管理
- `notificationService.ts` - 通知和好友请求

#### 支付和订阅
- `paymentService.ts` - 支付处理、订阅管理
- `settingsService.ts` - 用户设置和偏好

#### 实用功能
- `cardTrackingService.ts` - 卡片浏览跟踪
- `profileAIService.ts` - AI 档案优化

### API 端点示例
详细的 API 文档请参考：
- 中文文档: `FRONTEND_API_DOCUMENTATION.md`
- 英文文档: `FRONTEND_API_DOCUMENTATION_EN.md`

主要端点类别：
```typescript
// 认证
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout

// 档案管理
GET /api/profile
PUT /api/profile
POST /api/profile/avatar

// 聊天和推荐
POST /api/chat/message
GET /api/recommendations
POST /api/matching/search

// 社交互动
POST /api/swipe/right
POST /api/swipe/left
POST /api/whisper/send
GET /api/contacts

// 通知
GET /api/notifications/friend-requests
POST /api/notifications/friend-request
GET /api/notifications/receives

// 支付
POST /api/payments/receives
POST /api/payments/plan
GET /api/payments/transactions
```

## 📋 开发状态

### 已完成功能 ✅
- ✅ 用户引导和档案设置
- ✅ 卡片滑动界面
- ✅ AI 聊天系统
- ✅ 联系人历史管理
- ✅ 通知系统 UI
- ✅ 响应式设计
- ✅ 组件库集成
- ✅ 完整的 API 服务层
- ✅ Whisper 消息系统
- ✅ 卡片跟踪功能
- ✅ 多语言支持（中文/英文）
- ✅ 大学邮箱验证
- ✅ 物理引擎标签显示
- ✅ 支付集成（微信、支付宝、信用卡）
- ✅ 订阅计划管理
- ✅ 自定义 Hooks（useChatInterface, useProfileWizard, useSettings 等）

### 待完成功能 🚧
- 🔄 后端 API 完全集成和测试
- 🔄 实时消息推送
- 🔄 WebSocket 连接
- 🔄 推送通知
- 🔄 高级搜索优化

### 未来增强 🔮
- 📱 PWA 支持
- 🔔 浏览器推送通知
- 👥 群组对话
- 📸 媒体分享
- 📹 视频通话集成
- 📊 分析仪表板
- 🤖 更多 AI 功能
- 🌐 更多语言支持

## 🤝 贡献指南

1. **Fork 仓库**
2. **创建功能分支** (`git checkout -b feature/amazing-feature`)
3. **提交更改** (`git commit -m 'Add amazing feature'`)
4. **推送到分支** (`git push origin feature/amazing-feature`)
5. **打开 Pull Request**

### 代码风格
- 所有新代码使用 TypeScript
- 遵循现有的命名约定
- 为复杂函数添加 JSDoc 注释
- 遵循 React 最佳实践和 hooks 模式
- 保持组件的单一职责
- 编写可复用的代码

### 提交规范
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建或工具相关

## 📚 相关文档

### API 文档
- **中文**: `FRONTEND_API_DOCUMENTATION.md` - 完整的 API 集成文档
- **English**: `FRONTEND_API_DOCUMENTATION_EN.md` - Complete API integration documentation

### 服务文档
- `src/services/SET_UP_README.md` - API 服务设置指南
- `src/services/CHAT_API_README.md` - 聊天 API 使用文档
- `src/services/CARD_TRACKING_README.md` - 卡片跟踪功能文档
- `src/services/CARD_TRACKING_API_REFERENCE.md` - 卡片跟踪 API 参考
- `src/services/PROFILE_API_USAGE_EXAMPLES.md` - 档案 API 使用示例
- `src/services/SWIPE_API_USAGE_EXAMPLES.md` - 滑动 API 使用示例

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 🙏 致谢

- **shadcn/ui** - 美观、可访问的组件库
- **Radix UI** - 无样式、可访问的 UI 原语组件
- **Lucide** - 美观的图标库
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Vite** - 下一代前端构建工具
- **Motion (Framer Motion)** - 强大的动画库
- **Matter.js** - 2D 物理引擎

---

用 ❤️ 构建，通过 AI 驱动的社交网络连接人们。

Built with ❤️ for connecting people through AI-powered social networking.