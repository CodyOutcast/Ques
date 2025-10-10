// API Response 基础类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 用户基本信息类型
export interface UserDemographics {
  name: string;
  age: string;
  gender: 'male' | 'female' | 'other';
  location: string;
  hobbies: string[];
  languages: string[];
  oneSentenceIntro?: string;
  profilePhoto?: string;
}

// 项目信息类型
export interface ProjectInfo {
  title: string;
  role: string;
  description: string;
  referenceLinks: string[];
}

// 机构信息类型
export interface InstitutionInfo {
  name: string;
  role: string;
  description: string;
  email?: string;
  verified: boolean;
}

// 大学信息类型
export interface UniversityInfo {
  name: string;
  verified: boolean;
}

// 完整用户资料类型
export interface UserProfile {
  // 基本信息
  demographics: UserDemographics;
  
  // 技能和资源
  skills: string[];
  resources: string[];
  
  // 项目经历
  projects: ProjectInfo[];
  
  // 目标和需求
  goals: string[];
  demands: string[];
  
  // 机构背景
  institutions: InstitutionInfo[];
  university?: UniversityInfo;
}

// 注册请求类型
export interface RegisterRequest extends UserProfile {
  wechatId?: string;
  universityEmail?: string;
}

// 用户认证信息
export interface UserAuth {
  id: string;
  email?: string;
  wechatId?: string;
  phoneNumber?: string;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

// 登录请求类型
export interface LoginRequest {
  wechatId?: string;
  phoneNumber?: string;
  verificationCode?: string;
}

// 登录响应类型
export interface LoginResponse {
  user: UserAuth;
  profile: UserProfile;
  token: string;
  refreshToken: string;
}

// 大学验证请求
export interface UniversityVerificationRequest {
  universityName: string;
  email: string;
}

// 验证码请求
export interface VerificationCodeRequest {
  email: string;
  type: 'university' | 'phone' | 'wechat';
}

// 验证码验证请求
export interface CodeVerificationRequest {
  email?: string;
  phoneNumber?: string;
  code: string;
  type: 'university' | 'phone' | 'wechat';
}

// 分页参数
export interface PaginationParams {
  page: number;
  limit: number;
}

// 分页响应
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// 搜索参数
export interface SearchParams extends PaginationParams {
  query?: string;
  filters?: Record<string, any>;
}

// 大学列表响应
export interface UniversityListResponse extends PaginatedResponse<{
  id: string;
  name: string;
  domain: string;
  country: string;
  verified: boolean;
}> {}

// 文件上传响应
export interface FileUploadResponse {
  url: string;
  filename: string;
  size: number;
  type: string;
}

// 聊天相关类型
export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: string;
  metadata?: {
    query?: string;
    searchMode?: 'inside' | 'global';
    recommendations?: UserRecommendation[];
  };
}

export interface ChatSession {
  id: string;
  userId: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

export interface ChatRequest {
  message: string;
  sessionId?: string;
  searchMode?: 'inside' | 'global';
  quotedContacts?: string[];
}

export interface ChatResponse {
  message: ChatMessage;
  sessionId: string;
  recommendations?: UserRecommendation[];
  suggestedQueries?: string[];
}

// 用户推荐类型
export interface UserRecommendation {
  id: string;
  name: string;
  age: string;
  gender: string;
  avatar: string;
  location: string;
  hobbies: string[];
  languages: string[];
  skills: string[];
  resources: string[];
  projects: ProjectInfo[];
  goals: string[];
  demands: string[];
  institutions: InstitutionInfo[];
  university?: UniversityInfo;
  matchScore: number;
  bio: string;
  oneSentenceIntro?: string;
  whyMatch: string;
  receivesLeft?: number;
  isOnline?: boolean;
  lastSeen?: string;
  mutualConnections?: number;
  responseRate?: number;
}

// 推荐请求参数
export interface RecommendationRequest {
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

// 联系人管理类型
export interface ContactedUser {
  id: string;
  name: string;
  age: string;
  gender: string;
  avatar: string;
  location: string;
  hobbies: string[];
  languages: string[];
  skills: string[];
  resources: string[];
  projects: ProjectInfo[];
  goals: string[];
  demands: string[];
  institutions: InstitutionInfo[];
  university?: UniversityInfo;
  matchScore: number;
  bio: string;
  oneSentenceIntro?: string;
  whyMatch?: string;
  receivesLeft?: number;
  contactedAt: string;
  lastContactedAt?: string;
  conversationCount?: number;
  reported: boolean;
  reportReason?: string;
  reportAttachments?: any[];
  status: 'active' | 'blocked' | 'archived';
  tags?: string[];
  notes?: string;
}

export interface AddContactRequest {
  contactId: string;
  notes?: string;
  tags?: string[];
}

export interface UpdateContactRequest {
  contactId: string;
  notes?: string;
  tags?: string[];
  status?: 'active' | 'blocked' | 'archived';
}

export interface ReportContactRequest {
  contactId: string;
  reason: string;
  description?: string;
  attachments?: string[];
}

// 好友请求类型
export interface FriendRequest {
  id: string;
  name: string;
  age: string;
  gender: string;
  avatar: string;
  location: string;
  hobbies: string[];
  languages: string[];
  skills: string[];
  resources: string[];
  projects: ProjectInfo[];
  goals: string[];
  demands: string[];
  institutions: InstitutionInfo[];
  university?: UniversityInfo;
  matchScore: number;
  bio: string;
  oneSentenceIntro?: string;
  mutualInterest: string;
  receivesLeft: number;
  requestedAt: string;
  wechatId?: string;
  giftedReceives?: number;
  message?: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
}

export interface SendFriendRequestRequest {
  recipientId: string;
  message?: string;
  giftReceives?: number;
}

export interface RespondFriendRequestRequest {
  requestId: string;
  action: 'accept' | 'decline';
  message?: string;
}

// 通知类型
export interface Notification {
  id: string;
  type: 'friend_request' | 'message' | 'match' | 'system' | 'gift';
  title: string;
  content: string;
  data?: any;
  read: boolean;
  createdAt: string;
  expiresAt?: string;
}

// 匹配算法类型
export interface MatchingCriteria {
  skills?: string[];
  goals?: string[];
  demands?: string[];
  location?: string;
  university?: string;
  industries?: string[];
  projectTypes?: string[];
  collaborationType?: 'co-founder' | 'mentor' | 'investor' | 'collaborator' | 'employee';
}

export interface MatchScore {
  overall: number;
  skillsMatch: number;
  goalsAlignment: number;
  locationMatch: number;
  networkOverlap: number;
  availabilityMatch: number;
  experienceMatch: number;
}

export interface MatchExplanation {
  reasons: string[];
  mutualBenefits: string[];
  potentialChallenges?: string[];
  suggestedAction: string;
}

// 接收数量相关
export interface ReceivesStatus {
  remaining: number;
  total: number;
  resetDate: string;
  plan: 'basic' | 'pro';
}

export interface TopUpRequest {
  amount: number;
  paymentMethod?: string;
}

export interface GiftReceivesRequest {
  recipientId: string;
  amount: number;
  message?: string;
} 

// 个人资料编辑相关类型
export type ProfileSection = 
  | 'basic-info' 
  | 'skills' 
  | 'resources' 
  | 'projects' 
  | 'goals' 
  | 'demands' 
  | 'institutions' 
  | 'university';

export interface UpdateProfileSectionRequest {
  section: ProfileSection;
  data: Partial<UserProfile>;
  validateOnly?: boolean; // 仅验证，不保存
}

export interface ProfileCompleteness {
  overall: number; // 总体完整度百分比
  sections: Record<ProfileSection, {
    completed: boolean;
    weight: number;
    suggestions?: string[];
  }>;
  missingFields: Array<{
    section: ProfileSection;
    field: string;
    importance: 'high' | 'medium' | 'low';
    suggestion: string;
  }>;
}

// AI润色相关类型
export type AISuggestionType = 
  | 'enhancement' // 增强现有内容
  | 'rewrite' // 重写内容
  | 'addition' // 添加新内容
  | 'correction' // 纠正错误
  | 'optimization'; // 优化表达

export interface AISuggestion {
  id: string;
  section: ProfileSection;
  type: AISuggestionType;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  originalContent: any;
  suggestedContent: any;
  reasoning: string[];
  impactScore: number; // 1-100, 预期改进效果
  confidence: number; // 1-100, AI建议的置信度
  tags: string[]; // 标签，如 ['professional', 'concise', 'detailed']
  createdAt: string;
  appliedAt?: string;
}

export interface GenerateAISuggestionsRequest {
  sections?: ProfileSection[]; // 指定要分析的部分，默认全部
  suggestionTypes?: AISuggestionType[]; // 指定建议类型
  focusAreas?: string[]; // 重点关注领域，如 ['clarity', 'professionalism', 'completeness']
  targetAudience?: 'general' | 'technical' | 'business' | 'academic'; // 目标受众
  style?: 'professional' | 'casual' | 'academic' | 'creative'; // 期望风格
}

export interface ApplyAISuggestionRequest {
  suggestionId: string;
  customizations?: Record<string, any>; // 用户自定义修改
}

// 批量更新相关类型
export interface BatchProfileUpdateRequest {
  updates: Array<{
    section: ProfileSection;
    data: Partial<UserProfile>;
    priority?: number; // 更新优先级
  }>;
  validateAll?: boolean;
  applyImmediately?: boolean;
}

// 资料分析相关类型
export interface ProfileAnalysis {
  strengths: Array<{
    area: string;
    description: string;
    examples: string[];
  }>;
  improvementAreas: Array<{
    area: string;
    description: string;
    suggestions: string[];
    priority: 'high' | 'medium' | 'low';
  }>;
  marketability: {
    score: number; // 1-100
    factors: Array<{
      factor: string;
      impact: number;
      description: string;
    }>;
  };
  competitiveness: {
    score: number; // 1-100
    comparison: {
      stronger: string[];
      weaker: string[];
      similar: string[];
    };
  };
  recommendations: Array<{
    type: 'skill' | 'experience' | 'networking' | 'presentation';
    title: string;
    description: string;
    actionable: boolean;
  }>;
}

export interface ProfileStats {
  viewCount: number;
  matchCount: number;
  contactCount: number;
  responseRate: number;
  topSkills: Array<{ skill: string; matches: number; popularity: number }>;
  topLocations: Array<{ location: string; matches: number }>;
  profileRanking: {
    percentile: number; // 在同类用户中的排名百分位
    category: string; // 用户类别
    totalUsers: number;
  };
  activityMetrics: {
    lastActive: string;
    profileUpdates: number;
    avgUpdateFrequency: number; // 天
  };
}

// 大学验证增强类型
export interface UniversityVerificationRequest {
  universityName: string;
  email: string;
  studentId?: string;
  graduationYear?: number;
  degree?: string;
  major?: string;
}

export interface UniversityVerificationStatus {
  status: 'pending' | 'verified' | 'failed' | 'expired';
  university: {
    name: string;
    domain: string;
    country: string;
    rank?: number;
    verified: boolean;
  };
  verificationDetails: {
    method: 'email' | 'document' | 'third_party';
    verifiedAt?: string;
    expiresAt?: string;
    confidence: number; // 1-100
  };
  benefits: Array<{
    type: 'badge' | 'priority' | 'access' | 'discount';
    description: string;
    active: boolean;
  }>;
}

// 文件上传增强类型
export interface PhotoUploadRequest {
  file: File;
  type: 'avatar' | 'profile' | 'project' | 'verification';
  cropData?: {
    x: number;
    y: number;
    width: number;
    height: number;
    rotate?: number;
  };
  quality?: 'low' | 'medium' | 'high';
  autoEnhance?: boolean;
}

export interface PhotoUploadResponse extends FileUploadResponse {
  thumbnails: {
    small: string;   // 64x64
    medium: string;  // 128x128
    large: string;   // 256x256
  };
  analysis: {
    quality: number;        // 1-100
    appropriateness: number; // 1-100
    faceDetected: boolean;
    professionalScore: number; // 1-100
    suggestions?: string[];
  };
}

// 卡片滑动相关类型
export type SwipeAction = 'like' | 'ignore' | 'super_like';

export interface SwipeRecord {
  id: string;
  userId: string;
  targetUserId: string;
  action: SwipeAction;
  swipedAt: string;
  searchQuery?: string;
  searchMode?: 'inside' | 'global';
  matchScore?: number;
  sourceContext?: {
    sessionId?: string;
    recommendationBatch?: string;
    cardPosition?: number;
  };
}

export interface RecordSwipeRequest {
  targetUserId: string;
  action: SwipeAction;
  searchQuery?: string;
  searchMode?: 'inside' | 'global';
  matchScore?: number;
  sourceContext?: {
    sessionId?: string;
    recommendationBatch?: string;
    cardPosition?: number;
  };
}

export interface SwipeStats {
  totalSwipes: number;
  likes: number;
  ignores: number;
  superLikes: number;
  matchRate: number; // percentage of likes that resulted in matches
  mostSwipedSkills: string[];
  mostSwipedLocations: string[];
  averageMatchScore: number;
  dailySwipeCount: Array<{
    date: string;
    count: number;
  }>;
}

// Whisper消息系统相关类型
export interface WhisperSettings {
  wechatId: string;
  customMessage?: string;
  autoAccept: boolean;
  showOnlineStatus: boolean;
  enableNotifications: boolean;
}

export interface SendWhisperRequest {
  recipientId: string;
  message?: string; // 可选的自定义消息
  senderProfile: {
    id: string;
    name: string;
    avatar: string;
    age?: string;
    gender?: string;
    location: string;
    skills: string[];
    resources?: string[];
    projects: Array<{
      title: string;
      role: string;
      description: string;
      referenceLinks: string[];
    }>;
    goals?: string[];
    demands?: string[];
    institutions?: Array<{
      name: string;
      role: string;
      description: string;
      verified: boolean;
    }>;
    university?: {
      name: string;
      verified: boolean;
    };
    bio: string;
    oneSentenceIntro?: string;
    hobbies?: string[];
    languages?: string[];
    matchScore: number;
    wechatId: string; // 发送者的微信号
  };
  context?: {
    searchQuery?: string;
    searchMode?: 'inside' | 'global';
    matchExplanation?: string; // AI生成的匹配解释
    giftReceives?: number; // 赠送的receives数量
  };
}

export interface WhisperMessage {
  id: string;
  senderId: string;
  recipientId: string;
  senderProfile: SendWhisperRequest['senderProfile'];
  message?: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  context?: SendWhisperRequest['context'];
  sentAt: string;
  respondedAt?: string;
  expiresAt: string;
}

export interface RespondWhisperRequest {
  whisperId: string;
  action: 'accept' | 'decline';
  responseMessage?: string; // 可选的回复消息
}

// 设置相关类型定义

// 用户计划类型
export type UserPlan = 'basic' | 'pro';

// 用户设置
export interface UserSettings {
  id: string;
  userId: string;
  plan: UserPlan;
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

// 购买receives请求
export interface PurchaseReceivesRequest {
  amount: number; // 购买数量 (1-100)
  paymentMethod?: 'wechat_pay' | 'alipay' | 'credit_card';
}

// 购买receives响应
export interface PurchaseReceivesResponse {
  transactionId: string;
  amount: number;
  cost: number; // 总费用（人民币）
  newBalance: number; // 购买后的余额
  paymentUrl?: string; // 支付链接（如果需要跳转支付）
  status: 'pending' | 'completed' | 'failed';
  createdAt: string;
}

// 计划升级/降级请求
export interface ChangePlanRequest {
  newPlan: UserPlan;
  paymentMethod?: 'wechat_pay' | 'alipay' | 'credit_card';
}

// 计划升级/降级响应
export interface ChangePlanResponse {
  transactionId?: string; // 升级时有交易ID
  oldPlan: UserPlan;
  newPlan: UserPlan;
  monthlyFee?: number; // 月费（升级到Pro时）
  paymentUrl?: string; // 支付链接
  status: 'completed' | 'pending' | 'failed';
  effectiveDate: string;
}

// 通知设置更新请求
export interface UpdateNotificationSettingsRequest {
  notifications: {
    whisperRequests?: boolean;
    matches?: boolean;
    messages?: boolean;
    system?: boolean;
  };
}

// 用户偏好设置更新请求
export interface UpdateUserPreferencesRequest {
  preferences: {
    searchMode?: 'inside' | 'global';
    autoAcceptMatches?: boolean;
    showOnlineStatus?: boolean;
  };
}

// 账户删除请求
export interface DeleteAccountRequest {
  confirmPassword: string;
  reason?: string; // 删除原因
  feedback?: string; // 反馈意见
}

// 账户删除响应
export interface DeleteAccountResponse {
  message: string;
  deletedAt: string;
  dataRetentionDays: number; // 数据保留天数
}

// 登出请求
export interface LogoutRequest {
  allDevices?: boolean; // 是否登出所有设备
}

// 用户统计信息
export interface UserStats {
  totalWhispersSent: number;
  totalWhispersReceived: number;
  totalMatches: number;
  totalReceivesUsed: number;
  joinDate: string;
  lastActiveDate: string;
}

// 交易历史
export interface Transaction {
  id: string;
  type: 'purchase_receives' | 'plan_upgrade' | 'plan_downgrade' | 'refund';
  amount: number; // 购买数量或费用
  cost: number; // 实际花费
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  paymentMethod: 'wechat_pay' | 'alipay' | 'credit_card';
  description: string;
  createdAt: string;
  completedAt?: string;
}

// 获取交易历史请求
export interface GetTransactionsRequest {
  page?: number;
  limit?: number;
  type?: Transaction['type'];
  status?: Transaction['status'];
  startDate?: string;
  endDate?: string;
}

// 卡片跟踪相关类型
export interface LatestCardInfo {
  cardData: UserRecommendation; // 完整的卡片数据
  sessionId?: string; // 所属的聊天会话ID
  messageId?: string; // 关联的消息ID
  displayedAt: string; // 卡片显示时间
  context?: {
    searchQuery?: string; // 触发显示的搜索查询
    searchMode?: 'inside' | 'global'; // 搜索模式
    cardPosition?: number; // 卡片在推荐列表中的位置
  };
}

export interface UpdateLatestCardRequest {
  cardData: UserRecommendation;
  sessionId?: string;
  messageId?: string;
  context?: {
    searchQuery?: string;
    searchMode?: 'inside' | 'global';
    cardPosition?: number;
  };
}

export interface GetLatestCardResponse {
  hasCard: boolean;
  card?: LatestCardInfo;
  updatedAt?: string;
} 