// API 配置
export { API_CONFIG, isDevelopment, isProduction, getApiUrl } from './config';

// HTTP 客户端
export { httpClient, ApiError, get, post, put, patch, del as delete, upload } from './httpClient';

// 认证服务
export { authService, default as AuthService } from './authService';

// 用户资料服务
export { profileService, default as ProfileService } from './profileService';

// 大学验证服务
export { universityService, default as UniversityService } from './universityService';
export type { University, UniversityVerification } from './universityService';

// 聊天服务
export { chatService, default as ChatService } from './chatService';

// 推荐服务
export { recommendationService, default as RecommendationService } from './recommendationService';

// 联系人服务
export { contactService, default as ContactService } from './contactService';

// 通知服务
export { notificationService, default as NotificationService } from './notificationService';

// 匹配服务
export { matchingService, default as MatchingService } from './matchingService';

// 滑动行为服务
export { swipeService, default as SwipeService } from './swipeService';

// Whisper消息服务
export { whisperService, default as WhisperService } from './whisperService';

// 设置管理服务
export { settingsService, default as SettingsService } from './settingsService';

// 支付服务
export { paymentService, default as PaymentService } from './paymentService';

// AI润色服务
export { profileAIService, default as ProfileAIService } from './profileAIService';

// 卡片跟踪服务
export { cardTrackingService, default as CardTrackingService } from './cardTrackingService';

// 导入服务实例
import { authService } from './authService';
import { profileService } from './profileService';
import { universityService } from './universityService';
import { chatService } from './chatService';
import { recommendationService } from './recommendationService';
import { contactService } from './contactService';
import { notificationService } from './notificationService';
import { matchingService } from './matchingService';
import { swipeService } from './swipeService';
import { whisperService } from './whisperService';
import { settingsService } from './settingsService';
import { paymentService } from './paymentService';
import { profileAIService } from './profileAIService';
import { cardTrackingService } from './cardTrackingService';

// 导出所有服务的统一对象
export const apiServices = {
  auth: authService,
  profile: profileService,
  university: universityService,
  chat: chatService,
  recommendation: recommendationService,
  contact: contactService,
  notification: notificationService,
  matching: matchingService,
  swipe: swipeService,
  whisper: whisperService,
  settings: settingsService,
  payment: paymentService,
  profileAI: profileAIService,
  cardTracking: cardTrackingService,
};

// 默认导出
export default apiServices; 