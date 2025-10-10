# 前端API接口文档

> **文档版本**: 1.0.0  
> **生成时间**: 2025-10-10  
> **适用范围**: Ques前端应用所有API接口

## 目录
- [概述](#概述)
- [基础配置](#基础配置)
- [认证系统](#1-认证系统-authservice)
- [用户资料](#2-用户资料系统-profileservice)
- [AI资料润色](#3-ai资料润色服务-profileaiservice)
- [大学验证](#4-大学验证系统-universityservice)
- [推荐系统](#5-推荐系统-recommendationservice)
- [匹配搜索](#6-匹配搜索服务-matchingservice)
- [聊天系统](#7-聊天系统-chatservice)
- [卡片滑动](#8-卡片滑动服务-swipeservice)
- [联系人管理](#9-联系人管理-contactservice)
- [通知系统](#10-通知系统-notificationservice)
- [Whisper消息](#11-whisper消息系统-whisperservice)
- [支付系统](#12-支付系统-paymentservice)
- [设置管理](#13-设置管理-settingsservice)
- [卡片跟踪](#14-卡片跟踪服务-cardtrackingservice)
- [数据类型](#数据类型定义)

---

## 概述

本文档描述了Ques前端应用与后端API交互的所有接口。前端采用TypeScript开发，所有API调用都经过统一的HTTP客户端处理，支持：

- ✅ 自动Token管理
- ✅ 请求/响应拦截
- ✅ 错误统一处理
- ✅ 自动重试机制
- ✅ 离线缓存支持
- ✅ 文件上传进度

---

## 基础配置

### API基础URL
```typescript
BASE_URL: 'http://localhost:8000/api' // 开发环境
// 生产环境从环境变量 VITE_API_BASE_URL 读取
```

### 认证机制
- **Header**: `Authorization: Bearer {token}`
- **Token存储**: LocalStorage (`auth_token`)
- **Refresh Token**: LocalStorage (`refresh_token`)
- **用户信息**: LocalStorage (`user_info`)

### 通用响应格式
```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
```

### 分页响应格式
```typescript
interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}
```

---

## 1. 认证系统 (AuthService)

### 1.1 用户注册
```
POST /auth/register
```

**请求体**:
```typescript
{
  // 基本信息
  demographics: {
    name: string;
    age: string;
    gender: 'male' | 'female' | 'other';
    location: string;
    hobbies: string[];
    languages: string[];
    oneSentenceIntro?: string;
    profilePhoto?: string;
  };
  
  // 技能和资源
  skills: string[];
  resources: string[];
  
  // 项目经历
  projects: Array<{
    title: string;
    role: string;
    description: string;
    referenceLinks: string[];
  }>;
  
  // 目标和需求
  goals: string[];
  demands: string[];
  
  // 机构背景
  institutions: Array<{
    name: string;
    role: string;
    description: string;
    verified: boolean;
  }>;
  
  // 可选字段
  wechatId?: string;
  universityEmail?: string;
  university?: {
    name: string;
    verified: boolean;
  };
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    user: UserAuth;
    profile: UserProfile;
    token: string;
    refreshToken: string;
  }
}
```

### 1.2 用户登录
```
POST /auth/login
```

**请求体**:
```typescript
{
  wechatId?: string;
  phoneNumber?: string;
  verificationCode?: string;
}
```

**响应**: 同注册响应

### 1.3 发送验证码
```
POST /auth/send-code
```

**请求体**:
```typescript
{
  email: string;
  type: 'university' | 'phone' | 'wechat';
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    sent: boolean;
    expiresIn: number; // 过期时间（秒）
  }
}
```

### 1.4 验证验证码
```
POST /auth/verify-code
```

**请求体**:
```typescript
{
  email?: string;
  phoneNumber?: string;
  code: string;
  type: 'university' | 'phone' | 'wechat';
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    verified: boolean;
    token?: string;
  }
}
```

### 1.5 刷新Token
```
POST /auth/refresh
```

**请求体**:
```typescript
{
  refreshToken: string;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    token: string;
    refreshToken: string;
  }
}
```

### 1.6 登出
```
POST /auth/logout
```

**请求体**: 无  
**响应**: `{ success: true }`

### 1.7 上传头像
```
POST /upload/image (FormData)
```

**请求体**:
```typescript
FormData {
  file: File;
  type: 'avatar';
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    url: string;
    filename: string;
    size: number;
    type: string;
  }
}
```

### 1.8 微信登录授权
```
GET /auth/wechat/authorize
```

**响应**:
```typescript
{
  success: true,
  data: {
    authUrl: string;
    state: string;
  }
}
```

### 1.9 微信登录回调
```
POST /auth/wechat/callback
```

**请求体**:
```typescript
{
  code: string;
  state: string;
}
```

**响应**: 同登录响应

---

## 2. 用户资料系统 (ProfileService)

### 2.1 获取用户资料
```
GET /profile
```

**响应**:
```typescript
{
  success: true,
  data: UserProfile
}
```

### 2.2 更新用户资料（完整）
```
PUT /profile
```

**请求体**: `Partial<UserProfile>`  
**响应**: 更新后的完整资料

### 2.3 更新基本信息
```
PATCH /profile/demographics
```

**请求体**:
```typescript
{
  demographics: {
    name?: string;
    age?: string;
    gender?: 'male' | 'female' | 'other';
    location?: string;
    hobbies?: string[];
    languages?: string[];
    oneSentenceIntro?: string;
  }
}
```

### 2.4 更新技能
```
PATCH /profile/skills
```

**请求体**: `{ skills: string[] }`

### 2.5 更新资源
```
PATCH /profile/resources
```

**请求体**: `{ resources: string[] }`

### 2.6 项目管理

#### 添加项目
```
POST /profile/projects
```

**请求体**:
```typescript
{
  project: {
    title: string;
    role: string;
    description: string;
    referenceLinks: string[];
  }
}
```

#### 更新项目
```
PUT /profile/projects/{projectId}
```

**请求体**: `{ project: Partial<ProjectInfo> }`

#### 删除项目
```
DELETE /profile/projects/{projectId}
```

### 2.7 更新目标
```
PATCH /profile/goals
```

**请求体**: `{ goals: string[] }`

### 2.8 更新需求
```
PATCH /profile/demands
```

**请求体**: `{ demands: string[] }`

### 2.9 机构管理

#### 添加机构
```
POST /profile/institutions
```

**请求体**:
```typescript
{
  institution: {
    name: string;
    role: string;
    description: string;
    verified: boolean;
  }
}
```

#### 更新机构
```
PUT /profile/institutions/{institutionId}
```

#### 删除机构
```
DELETE /profile/institutions/{institutionId}
```

### 2.10 上传头像
```
POST /profile/avatar (FormData)
```

**请求体**: FormData with `avatar` field

### 2.11 上传照片（高级）
```
POST /profile/photo (FormData)
```

**请求体**:
```typescript
FormData {
  file: File;
  type: 'avatar' | 'profile' | 'project' | 'verification';
  cropData?: string; // JSON序列化的裁剪数据
  quality?: 'low' | 'medium' | 'high';
  autoEnhance?: boolean;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    url: string;
    filename: string;
    size: number;
    type: string;
    thumbnails: {
      small: string;
      medium: string;
      large: string;
    };
    analysis: {
      quality: number;
      appropriateness: number;
      faceDetected: boolean;
      professionalScore: number;
      suggestions?: string[];
    };
  }
}
```

### 2.12 批量更新资料
```
PATCH /profile/batch
```

**请求体**:
```typescript
{
  demographics?: Partial<UserDemographics>;
  skills?: string[];
  resources?: string[];
  goals?: string[];
  demands?: string[];
  projects?: ProjectInfo[];
  institutions?: InstitutionInfo[];
}
```

### 2.13 更新资料指定部分
```
PUT /profile/section
```

**请求体**:
```typescript
{
  section: 'basic-info' | 'skills' | 'resources' | 'projects' | 'goals' | 'demands' | 'institutions' | 'university';
  data: Partial<UserProfile>;
  validateOnly?: boolean;
}
```

### 2.14 获取资料完整度
```
GET /profile/completeness
```

**响应**:
```typescript
{
  success: true,
  data: {
    overall: number; // 0-100
    sections: {
      'basic-info': { completed: boolean; weight: number; suggestions?: string[] };
      'skills': { ... };
      // ... 其他部分
    };
    missingFields: Array<{
      section: ProfileSection;
      field: string;
      importance: 'high' | 'medium' | 'low';
      suggestion: string;
    }>;
  }
}
```

### 2.15 生成个人简介
```
POST /profile/generate-bio
```

**请求体**:
```typescript
{
  style?: 'professional' | 'casual' | 'academic' | 'creative';
  length?: 'short' | 'medium' | 'long';
  includeSkills?: boolean;
  includeGoals?: boolean;
  includeExperience?: boolean;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    original?: string;
    generated: string;
    alternatives: string[];
    reasoning: string[];
  }
}
```

### 2.16 资料分析
```
GET /profile/analyze
```

**响应**: 返回详细的资料分析报告

### 2.17 资料统计
```
GET /profile/stats
```

**响应**:
```typescript
{
  success: true,
  data: {
    viewCount: number;
    matchCount: number;
    contactCount: number;
    responseRate: number;
    topSkills: Array<{ skill: string; matches: number; popularity: number }>;
    // ... 更多统计数据
  }
}
```

### 2.18 批量更新（增强版）
```
POST /profile/batch-update
```

**请求体**:
```typescript
{
  updates: Array<{
    section: ProfileSection;
    data: Partial<UserProfile>;
    priority?: number;
  }>;
  validateAll?: boolean;
  applyImmediately?: boolean;
}
```

### 2.19 验证资料部分
```
POST /profile/section/validate
```

**请求体**:
```typescript
{
  section: ProfileSection;
  data: any;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    suggestions: string[];
  }
}
```

---

## 3. AI资料润色服务 (ProfileAIService)

### 3.1 生成AI改进建议
```
POST /profile/ai-suggestions
```

**请求体**:
```typescript
{
  sections?: ProfileSection[];
  suggestionTypes?: ('enhancement' | 'rewrite' | 'addition' | 'correction' | 'optimization')[];
  focusAreas?: string[];
  targetAudience?: 'general' | 'technical' | 'business' | 'academic';
  style?: 'professional' | 'casual' | 'academic' | 'creative';
}
```

**响应**:
```typescript
{
  success: true,
  data: AISuggestion[] // 建议列表
}
```

### 3.2 应用AI建议
```
POST /profile/ai-suggestions/apply
```

**请求体**:
```typescript
{
  suggestionId: string;
  customizations?: Record<string, any>;
}
```

**响应**: 更新后的资料

### 3.3 批量应用AI建议
```
POST /profile/ai-suggestions/apply/batch
```

**请求体**:
```typescript
{
  suggestionIds: string[];
}
```

### 3.4 生成部分建议
```
POST /profile/ai-suggestions/section
```

**请求体**:
```typescript
{
  section: ProfileSection;
  content: any;
  type?: AISuggestionType;
  style?: string;
  targetAudience?: string;
  focusAreas?: string[];
}
```

### 3.5 批量生成建议
```
POST /profile/ai-suggestions/batch
```

**请求体**:
```typescript
{
  sections: Array<{ section: ProfileSection; content: any }>;
  style?: string;
  targetAudience?: string;
  priority?: 'speed' | 'quality';
}
```

### 3.6 内容增强
```
POST /profile/ai-suggestions/enhance
```

**请求体**:
```typescript
{
  section: ProfileSection;
  content: any;
  enhancementType: 'clarity' | 'professionalism' | 'engagement' | 'completeness' | 'conciseness';
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    original: any;
    enhanced: any;
    improvements: Array<{
      type: string;
      description: string;
      impact: number; // 1-10
    }>;
    confidence: number;
  }
}
```

### 3.7 内容质量分析
```
POST /profile/ai-suggestions/analyze-quality
```

**请求体**:
```typescript
{
  section: ProfileSection;
  content: any;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    overallScore: number; // 1-100
    dimensions: {
      clarity: number;
      professionalism: number;
      completeness: number;
      engagement: number;
      uniqueness: number;
    };
    suggestions: string[];
    strengths: string[];
    weaknesses: string[];
  }
}
```

### 3.8 获取写作建议
```
GET /profile/ai-suggestions/writing-tips?section={section}&userStyle={style}&industry={industry}
```

**响应**:
```typescript
{
  success: true,
  data: {
    tips: Array<{
      category: string;
      title: string;
      description: string;
      example?: string;
      priority: 'high' | 'medium' | 'low';
    }>;
    templates: Array<{
      name: string;
      content: string;
      suitableFor: string[];
    }>;
    commonMistakes: string[];
  }
}
```

---

## 4. 大学验证系统 (UniversityService)

### 4.1 搜索大学
```
GET /universities/search?page={page}&limit={limit}&q={query}&country={country}
```

**响应**:
```typescript
{
  success: true,
  data: {
    data: Array<{
      id: string;
      name: string;
      domain: string[];
      country: string;
      verified: boolean;
      rank?: number;
    }>;
    pagination: { page, limit, total, totalPages };
  }
}
```

### 4.2 获取热门大学
```
GET /universities/search?limit={limit}&popular=true&country={country}
```

### 4.3 根据域名获取大学
```
GET /universities/search/domain/{domain}
```

**响应**: 返回单个大学信息或null

### 4.4 发送大学邮箱验证
```
POST /universities/send-verification
```

**请求体**:
```typescript
{
  universityName: string;
  email: string;
  studentId?: string;
  graduationYear?: number;
  degree?: string;
  major?: string;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    sent: boolean;
    expiresIn: number;
    verificationId: string;
  }
}
```

### 4.5 验证大学邮箱
```
POST /universities/verify/{verificationId}
```

**请求体**:
```typescript
{
  code: string;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    verified: boolean;
    universityInfo?: University;
  }
}
```

### 4.6 获取验证状态
```
GET /universities/verify/status
```

**响应**: 返回验证状态或null

### 4.7 获取增强验证状态
```
GET /universities/verify/status/{verificationId}
```

### 4.8 增强大学验证
```
POST /universities/verify/enhanced
```

**请求体**: 同发送验证  
**响应**: 包含验证状态和后续步骤

### 4.9 验证域名
```
POST /universities/verify/validate-domain
```

**请求体**:
```typescript
{
  email: string;
  universityName: string;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    isValid: boolean;
    university?: University;
    domain: string;
    suggestions: string[];
    confidence: number; // 1-100
  }
}
```

### 4.10 获取验证福利
```
GET /universities/verify/benefits/{universityId}
```

**响应**: 返回可获得的福利和资格要求

### 4.11 请求替代验证方式
```
POST /universities/verify/alternative
```

**请求体**:
```typescript
{
  universityId: string;
  method: 'document' | 'social' | 'third_party' | 'manual';
  data: any;
}
```

### 4.12 获取大学详情
```
GET /universities/search/{universityId}
```

### 4.13 获取大学统计
```
GET /universities/search/stats/{universityId}
```

**响应**: 返回排名、统计数据、项目、校友等信息

---

## 5. 推荐系统 (RecommendationService)

### 5.1 获取推荐用户
```
POST /recommendations
```

**请求体**:
```typescript
{
  query?: string;
  searchMode?: 'inside' | 'global';
  filters?: {
    location?: string[];
    skills?: string[];
    university?: string[];
    industries?: string[];
    experienceLevel?: string[];
    availability?: string[];
  };
  excludeContacts?: string[];
  limit?: number;
  offset?: number;
}
```

**响应**:
```typescript
{
  success: true,
  data: UserRecommendation[]
}
```

### 5.2 获取匹配用户
```
POST /recommendations/matches
```

**请求体**: MatchingCriteria  
**响应**: 分页的推荐列表

### 5.3 更新推荐偏好
```
PUT /recommendations/preferences
```

**请求体**: MatchingCriteria  
**响应**: 更新后的偏好

### 5.4 获取推荐偏好
```
GET /recommendations/preferences
```

### 5.5 智能推荐
```
GET /recommendations/smart?limit={limit}&excludeContacted={boolean}&refreshData={boolean}
```

### 5.6 个性化推荐
```
GET /recommendations/personalized?excludeContacted={boolean}&limit={limit}&includeSimilarToLiked={boolean}
```

---

## 6. 匹配搜索服务 (MatchingService)

### 6.1 搜索用户
```
POST /matching/search
```

**请求体**: SearchParams + criteria  
**响应**: 分页的用户列表

### 6.2 获取匹配分数
```
POST /matching/score/{targetUserId}
```

**请求体**: MatchingCriteria（可选）  
**响应**:
```typescript
{
  success: true,
  data: {
    overall: number;
    skillsMatch: number;
    goalsAlignment: number;
    locationMatch: number;
    networkOverlap: number;
    availabilityMatch: number;
    experienceMatch: number;
  }
}
```

### 6.3 获取匹配解释
```
POST /matching/explanation/{targetUserId}
```

**请求体**: MatchingCriteria（可选）  
**响应**:
```typescript
{
  success: true,
  data: {
    reasons: string[];
    mutualBenefits: string[];
    potentialChallenges?: string[];
    suggestedAction: string;
  }
}
```

### 6.4 更新匹配标准
```
PUT /matching/criteria
```

### 6.5 获取匹配标准
```
GET /matching/criteria
```

### 6.6 高级搜索
```
POST /matching/search/advanced
```

**请求体**:
```typescript
{
  searchMode?: 'inside' | 'global';
  location?: {
    countries?: string[];
    cities?: string[];
    radius?: number;
  };
  demographics?: {
    ageRange?: [number, number];
    genders?: string[];
  };
  skills?: {
    required?: string[];
    preferred?: string[];
    exclude?: string[];
  };
  experience?: {
    levels?: string[];
    industries?: string[];
    roles?: string[];
  };
  education?: {
    universities?: string[];
    degrees?: string[];
    verified?: boolean;
  };
  availability?: {
    collaborationTypes?: string[];
    timeCommitment?: string[];
    remoteFriendly?: boolean;
  };
  other?: {
    hasProjects?: boolean;
    isOnline?: boolean;
    responseRate?: number;
    mutualConnections?: boolean;
  };
  pagination?: { page: number; limit: number };
  sorting?: {
    by: 'relevance' | 'match_score' | 'recent' | 'response_rate';
    order: 'asc' | 'desc';
  };
}
```

### 6.7 搜索建议
```
GET /matching/search/suggestions?q={query}
```

**响应**:
```typescript
{
  success: true,
  data: {
    queries: string[];
    skills: string[];
    locations: string[];
    universities: string[];
    industries: string[];
  }
}
```

### 6.8 热门搜索
```
GET /matching/search/trending
```

### 6.9 保存搜索
```
POST /matching/search/save
```

**请求体**:
```typescript
{
  name: string;
  query?: string;
  filters: any;
}
```

### 6.10 获取保存的搜索
```
GET /matching/search/saved
```

### 6.11 删除保存的搜索
```
DELETE /matching/search/saved/{searchId}
```

### 6.12 搜索分析
```
GET /matching/search/analytics
GET /matching/search/analytics/{searchId}
```

---

## 7. 聊天系统 (ChatService)

### 7.1 发送消息
```
POST /chat/message
```

**请求体**:
```typescript
{
  message: string;
  sessionId?: string;
  searchMode?: 'inside' | 'global';
  quotedContacts?: string[];
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    message: ChatMessage;
    sessionId: string;
    recommendations?: UserRecommendation[];
    suggestedQueries?: string[];
  }
}
```

### 7.2 创建会话
```
POST /chat/session
```

**响应**: ChatSession

### 7.3 获取会话详情
```
GET /chat/session/{sessionId}
```

### 7.4 获取聊天历史
```
GET /chat/history?page={page}&limit={limit}&sessionId={sessionId}
```

**响应**: 分页的会话列表

### 7.5 删除会话
```
DELETE /chat/session/{sessionId}
```

---

## 8. 卡片滑动服务 (SwipeService)

### 8.1 记录滑动
```
POST /swipe/record
```

**请求体**:
```typescript
{
  targetUserId: string;
  action: 'like' | 'ignore' | 'super_like';
  searchQuery?: string;
  searchMode?: 'inside' | 'global';
  matchScore?: number;
  sourceContext?: {
    sessionId?: string;
    recommendationBatch?: string;
    cardPosition?: number;
  };
}
```

**响应**: SwipeRecord

### 8.2 批量记录滑动
```
POST /swipe/record/batch
```

**请求体**:
```typescript
{
  swipes: RecordSwipeRequest[];
}
```

### 8.3 获取滑动历史
```
GET /swipe/history?page={page}&limit={limit}&action={action}&startDate={date}&endDate={date}
```

### 8.4 获取滑动统计
```
GET /swipe/stats?period={period}&startDate={date}&endDate={date}
```

**响应**:
```typescript
{
  success: true,
  data: {
    totalSwipes: number;
    likes: number;
    ignores: number;
    superLikes: number;
    matchRate: number;
    mostSwipedSkills: string[];
    mostSwipedLocations: string[];
    averageMatchScore: number;
    dailySwipeCount: Array<{ date: string; count: number }>;
  }
}
```

### 8.5 获取滑动偏好
```
GET /swipe/stats/preferences
```

**响应**: 偏好技能、位置、大学、滑动模式等

### 8.6 获取滑动建议
```
GET /swipe/stats/suggestions/{targetUserId}
```

**响应**: AI生成的滑动建议

### 8.7 删除滑动记录
```
DELETE /swipe/record/{swipeId}
```

### 8.8 清空滑动历史
```
DELETE /swipe/record/bulk
```

**请求体**:
```typescript
{
  olderThan?: string; // ISO date
  action?: SwipeAction;
}
```

---

## 9. 联系人管理 (ContactService)

### 9.1 获取联系人列表
```
GET /contacts?page={page}&limit={limit}&status={status}&tags[]={tag}&q={query}
```

**响应**: 分页的联系人列表

### 9.2 添加联系人
```
POST /contacts
```

**请求体**:
```typescript
{
  contactId: string;
  notes?: string;
  tags?: string[];
}
```

### 9.3 更新联系人
```
PUT /contacts/{contactId}
```

**请求体**:
```typescript
{
  notes?: string;
  tags?: string[];
  status?: 'active' | 'blocked' | 'archived';
}
```

### 9.4 删除联系人
```
DELETE /contacts/{contactId}
```

### 9.5 举报联系人
```
POST /contacts/report
```

**请求体**:
```typescript
{
  contactId: string;
  reason: string;
  description?: string;
  attachments?: string[];
}
```

### 9.6 获取联系人历史
```
GET /contacts/history/{contactId}
```

**响应**: 交互历史记录

### 9.7 批量添加联系人
```
POST /contacts/batch
```

**请求体**:
```typescript
{
  contacts: Array<{
    contactId: string;
    notes?: string;
    tags?: string[];
  }>;
}
```

### 9.8 获取联系人统计
```
GET /contacts/stats
```

**响应**: 总数、状态分布、热门技能/位置等

### 9.9 搜索联系人
```
POST /contacts/search
```

**请求体**:
```typescript
{
  query: string;
  filters?: {
    skills?: string[];
    location?: string;
    university?: string;
    tags?: string[];
  };
}
```

### 9.10 导出联系人
```
POST /contacts/export
```

**请求体**: `{ format: 'csv' | 'json' }`  
**响应**: 下载链接

---

## 10. 通知系统 (NotificationService)

### 10.1 获取通知列表
```
GET /notifications?page={page}&limit={limit}&type={type}&unreadOnly={boolean}
```

**响应**: 分页的通知列表

### 10.2 标记为已读
```
POST /notifications/read
```

**请求体**:
```typescript
{
  notificationIds: string[];
}
```

### 10.3 删除通知
```
DELETE /notifications/{notificationId}
```

### 10.4 获取好友请求
```
GET /notifications/friend-requests?page={page}&limit={limit}&status={status}&direction={direction}
```

### 10.5 发送好友请求
```
POST /notifications/friend-requests
```

**请求体**:
```typescript
{
  recipientId: string;
  message?: string;
  giftReceives?: number;
}
```

### 10.6 回应好友请求
```
POST /notifications/friend-requests/respond
```

**请求体**:
```typescript
{
  requestId: string;
  action: 'accept' | 'decline';
  message?: string;
}
```

### 10.7 获取未读数量
```
GET /notifications/unread-count
```

**响应**:
```typescript
{
  success: true,
  data: {
    total: number;
    friendRequests: number;
    messages: number;
    matches: number;
    system: number;
    gifts: number;
  }
}
```

### 10.8 批量操作通知
```
POST /notifications/read  // 批量已读
POST /notifications/batch  // 批量删除
```

### 10.9 更新通知偏好
```
PUT /notifications/preferences
```

**请求体**:
```typescript
{
  emailNotifications: boolean;
  pushNotifications: boolean;
  friendRequests: boolean;
  matches: boolean;
  messages: boolean;
  system: boolean;
  gifts: boolean;
}
```

### 10.10 获取通知偏好
```
GET /notifications/preferences
```

### 10.11 接收数量管理

#### 获取接收状态
```
GET /receives/status
```

**响应**:
```typescript
{
  success: true,
  data: {
    remaining: number;
    total: number;
    resetDate: string;
    plan: 'basic' | 'pro';
  }
}
```

#### 充值
```
POST /receives/top-up
```

**请求体**:
```typescript
{
  amount: number;
  paymentMethod?: string;
}
```

#### 赠送
```
POST /receives/gift
```

**请求体**:
```typescript
{
  recipientId: string;
  amount: number;
  message?: string;
}
```

#### 获取历史
```
GET /receives/history?page={page}&limit={limit}&type={type}
```

---

## 11. Whisper消息系统 (WhisperService)

### 11.1 发送Whisper
```
POST /whispers/send
```

**请求体**:
```typescript
{
  recipientId: string;
  message?: string;
  senderProfile: {
    id: string;
    name: string;
    avatar: string;
    location: string;
    skills: string[];
    bio: string;
    matchScore: number;
    wechatId: string;
    // ... 其他资料字段
  };
  context?: {
    searchQuery?: string;
    searchMode?: 'inside' | 'global';
    matchExplanation?: string;
    giftReceives?: number;
  };
}
```

### 11.2 获取收到的Whisper
```
GET /whispers?page={page}&limit={limit}&status={status}
```

### 11.3 获取发送的Whisper
```
GET /whispers/sent?page={page}&limit={limit}&status={status}
```

### 11.4 回复Whisper
```
POST /whispers/respond
```

**请求体**:
```typescript
{
  whisperId: string;
  action: 'accept' | 'decline';
  responseMessage?: string;
}
```

### 11.5 获取Whisper设置
```
GET /whispers/settings
```

**响应**:
```typescript
{
  success: true,
  data: {
    wechatId: string;
    customMessage?: string;
    autoAccept: boolean;
    showOnlineStatus: boolean;
    enableNotifications: boolean;
  }
}
```

### 11.6 更新Whisper设置
```
PUT /whispers/settings
```

**请求体**: Partial<WhisperSettings>

### 11.7 获取Whisper详情
```
GET /whispers/{whisperId}
```

### 11.8 删除Whisper
```
DELETE /whispers/{whisperId}
```

### 11.9 标记为已读
```
PATCH /whispers/{whisperId}/read
```

### 11.10 批量标记已读
```
PATCH /whispers/read/batch
```

**请求体**: `{ whisperIds: string[] }`

---

## 12. 支付系统 (PaymentService)

### 12.1 购买Receives
```
POST /payments/receives
```

**请求体**:
```typescript
{
  amount: number; // 1-100
  paymentMethod?: 'wechat_pay' | 'alipay' | 'credit_card';
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    transactionId: string;
    amount: number;
    cost: number;
    newBalance: number;
    paymentUrl?: string;
    status: 'pending' | 'completed' | 'failed';
    createdAt: string;
  }
}
```

### 12.2 更改计划
```
POST /payments/plan
```

**请求体**:
```typescript
{
  newPlan: 'basic' | 'pro';
  paymentMethod?: 'wechat_pay' | 'alipay' | 'credit_card';
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    transactionId?: string;
    oldPlan: UserPlan;
    newPlan: UserPlan;
    monthlyFee?: number;
    paymentUrl?: string;
    status: 'completed' | 'pending' | 'failed';
    effectiveDate: string;
  }
}
```

### 12.3 获取交易历史
```
GET /payments/transactions?page={page}&limit={limit}&type={type}&status={status}&startDate={date}&endDate={date}
```

**响应**: 分页的交易记录

### 12.4 获取支付方式
```
GET /payments/methods
```

**响应**:
```typescript
{
  success: true,
  data: Array<{
    id: string;
    name: string;
    type: 'wechat_pay' | 'alipay' | 'credit_card';
    enabled: boolean;
    description?: string;
    icon?: string;
  }>
}
```

### 12.5 创建支付会话
```
POST /payments/session
```

**请求体**:
```typescript
{
  type: 'purchase_receives' | 'plan_upgrade';
  amount: number;
  paymentMethod: 'wechat_pay' | 'alipay' | 'credit_card';
  metadata?: Record<string, any>;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    sessionId: string;
    paymentUrl: string;
    qrCode?: string;
    expiresAt: string;
  }
}
```

### 12.6 获取交易详情
```
GET /payments/transactions/{transactionId}
```

### 12.7 取消交易
```
PATCH /payments/transactions/{transactionId}/cancel
```

---

## 13. 设置管理 (SettingsService)

### 13.1 获取用户设置
```
GET /settings
```

**响应**:
```typescript
{
  success: true,
  data: {
    id: string;
    userId: string;
    plan: 'basic' | 'pro';
    receivesLeft: number;
    whisperCount: number;
    notifications: {
      whisperRequests: boolean;
      matches: boolean;
      messages: boolean;
      system: boolean;
    };
    preferences: {
      searchMode: 'inside' | 'global';
      autoAcceptMatches: boolean;
      showOnlineStatus: boolean;
    };
    createdAt: string;
    updatedAt: string;
  }
}
```

### 13.2 更新通知设置
```
PUT /settings/notifications
```

**请求体**:
```typescript
{
  notifications: {
    whisperRequests?: boolean;
    matches?: boolean;
    messages?: boolean;
    system?: boolean;
  };
}
```

### 13.3 更新用户偏好
```
PUT /settings/preferences
```

**请求体**:
```typescript
{
  preferences: {
    searchMode?: 'inside' | 'global';
    autoAcceptMatches?: boolean;
    showOnlineStatus?: boolean;
  };
}
```

### 13.4 获取用户统计
```
GET /settings/stats
```

**响应**:
```typescript
{
  success: true,
  data: {
    totalWhispersSent: number;
    totalWhispersReceived: number;
    totalMatches: number;
    totalReceivesUsed: number;
    joinDate: string;
    lastActiveDate: string;
  }
}
```

### 13.5 账户管理

#### 登出
```
POST /auth/logout
```

**请求体**: `{ allDevices?: boolean }`

#### 删除账户
```
POST /account/delete
```

**请求体**:
```typescript
{
  confirmPassword: string;
  reason?: string;
  feedback?: string;
}
```

**响应**:
```typescript
{
  success: true,
  data: {
    message: string;
    deletedAt: string;
    dataRetentionDays: number;
  }
}
```

#### 导出数据
```
POST /account/export
```

**响应**: `{ downloadUrl: string; expiresAt: string }`

#### 获取账户信息
```
GET /account/info
```

**响应**:
```typescript
{
  success: true,
  data: {
    userId: string;
    email: string;
    createdAt: string;
    lastLoginAt: string;
    dataRetentionDays: number;
  }
}
```

---

## 14. 卡片跟踪服务 (CardTrackingService)

### 14.1 更新最新卡片
```
POST /chat/latest-card
```

**请求体**:
```typescript
{
  cardData: UserRecommendation;
  sessionId?: string;
  messageId?: string;
  context?: {
    searchQuery?: string;
    searchMode?: 'inside' | 'global';
    cardPosition?: number;
  };
}
```

**响应**: LatestCardInfo

### 14.2 获取最新卡片
```
GET /chat/latest-card
```

**响应**:
```typescript
{
  success: true,
  data: {
    hasCard: boolean;
    card?: LatestCardInfo;
    updatedAt?: string;
  }
}
```

### 14.3 清除最新卡片
```
DELETE /chat/latest-card
```

---

## 数据类型定义

### UserProfile
用户完整资料，包含：
- demographics: 基本信息（姓名、年龄、性别、位置等）
- skills: 技能列表
- resources: 资源列表
- projects: 项目经历
- goals: 目标
- demands: 需求
- institutions: 机构背景
- university: 大学信息

### UserRecommendation
推荐用户卡片，包含：
- 用户基本信息
- matchScore: 匹配分数
- whyMatch: 匹配原因
- receivesLeft: 剩余接收数
- isOnline: 在线状态
- mutualConnections: 共同联系人数
- responseRate: 响应率

### AISuggestion
AI润色建议，包含：
- section: 资料部分
- type: 建议类型（enhancement/rewrite/addition等）
- priority: 优先级
- originalContent: 原始内容
- suggestedContent: 建议内容
- reasoning: 理由
- impactScore: 影响分数
- confidence: 置信度

### SwipeRecord
滑动记录，包含：
- targetUserId: 目标用户ID
- action: 滑动动作（like/ignore/super_like）
- searchQuery: 搜索查询
- matchScore: 匹配分数
- sourceContext: 来源上下文

### WhisperMessage
Whisper消息，包含：
- senderProfile: 发送者资料
- status: 状态（pending/accepted/declined/expired）
- context: 上下文信息
- expiresAt: 过期时间

### Transaction
交易记录，包含：
- type: 类型（purchase_receives/plan_upgrade等）
- amount: 数量/金额
- cost: 花费
- status: 状态
- paymentMethod: 支付方式

---

## 错误处理

所有API调用失败时都会抛出 `ApiError`，包含以下信息：
```typescript
class ApiError extends Error {
  status?: number;      // HTTP状态码
  code?: string;        // 错误代码
  details?: any;        // 详细信息
}
```

### 常见错误码
- `401`: 未授权（token失效或缺失）
- `403`: 禁止访问（权限不足）
- `404`: 资源不存在
- `422`: 验证失败
- `429`: 请求过于频繁
- `500`: 服务器错误

---

## 本地缓存策略

### 滑动行为缓存
- SwipeService 自动缓存失败的滑动行为
- 最多缓存50条记录
- 网络恢复后自动同步

### 卡片跟踪缓存
- CardTrackingService 缓存最新卡片
- 1秒内不重复更新（节流）

### 设置本地存储
- 微信ID: `user_wechat_id`
- 自定义Whisper消息: `custom_whisper_message`
- 通知设置: `notification_settings`

---

## 文件上传

### 支持的文件类型
- 图片: JPEG, PNG, GIF, WebP
- 文档: PDF（用于验证）

### 上传流程
1. 创建FormData对象
2. 添加文件和元数据
3. 调用upload方法
4. 监听上传进度（可选）

### 示例
```typescript
const formData = new FormData();
formData.append('file', file);
formData.append('type', 'avatar');

await profileService.uploadAvatar(file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});
```

---

## WebSocket支持

目前前端未实现WebSocket，但后端可能支持实时通知。建议实现：
- 在线状态更新
- 实时消息通知
- 新好友请求提醒
- 匹配通知

---

## API版本控制

当前API版本通过URL路径控制：
- 基础路径: `/api`
- 未来版本可能使用: `/api/v2`, `/api/v3`

---

## 安全建议

### Token管理
- Token存储在LocalStorage
- 每次请求自动添加到Header
- 401错误时自动清除并重定向登录

### 敏感数据
- 密码不在前端存储
- 支付信息使用HTTPS加密传输
- 验证码有时效限制

---

## 性能优化

### 请求优化
- 支持请求去重
- 自动重试失败请求
- 批量操作减少请求次数

### 缓存策略
- 用户资料缓存
- 搜索结果临时缓存
- 本地优先展示

---

## 开发工具

### 类型安全
- 完整TypeScript类型定义
- API响应类型检查
- 编译时错误检测

### 调试支持
- 控制台错误日志
- 网络请求追踪
- 响应数据验证

---

## 附录

### 环境变量
```env
VITE_API_BASE_URL=http://localhost:8000/api  # API基础URL
```

### 常用状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无内容） |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

---

## 更新日志

### v1.0.0 (2025-10-10)
- 初始版本
- 完整API接口文档
- 包含14个主要服务模块
- 100+个API端点

---

**文档维护**: 前端开发团队  
**反馈渠道**: 提交Issue或联系后端团队  
**最后更新**: 2025年10月10日

