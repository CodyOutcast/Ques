// API 配置
export const API_CONFIG = {
  // 后端API基础URL (开发环境)
  BASE_URL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api',
  
  // 超时设置 (毫秒)
  TIMEOUT: 10000,
  
  // 重试次数
  MAX_RETRIES: 3,
  
  // 认证相关
  AUTH: {
    TOKEN_KEY: 'auth_token',
    REFRESH_TOKEN_KEY: 'refresh_token',
    USER_KEY: 'user_info',
  },
  
  // API端点
  ENDPOINTS: {
    // 认证相关
    AUTH: {
      REGISTER: '/auth/register',
      LOGIN: '/auth/login',
      REFRESH: '/auth/refresh',
      LOGOUT: '/auth/logout',
      VERIFY_CODE: '/auth/verify-code',
      SEND_CODE: '/auth/send-code',
    },
    
    // 用户资料
    PROFILE: {
      GET: '/profile',
      UPDATE: '/profile',
      UPDATE_SECTION: '/profile/section',
      UPLOAD_AVATAR: '/profile/avatar',
      UPLOAD_PHOTO: '/profile/photo',
      GET_COMPLETENESS: '/profile/completeness',
      GENERATE_BIO: '/profile/generate-bio',
      
      // AI润色功能
      AI_SUGGESTIONS: '/profile/ai-suggestions',
      APPLY_AI_SUGGESTION: '/profile/ai-suggestions/apply',
      
      // 资料分析
      ANALYZE_PROFILE: '/profile/analyze',
      GET_PROFILE_STATS: '/profile/stats',
      
      // 批量操作
      BATCH_UPDATE: '/profile/batch-update',
    },
    
    // 大学验证
    UNIVERSITY: {
      SEARCH: '/universities/search',
      VERIFY: '/universities/verify',
      SEND_VERIFICATION: '/universities/send-verification',
    },
    
    // 文件上传
    UPLOAD: {
      IMAGE: '/upload/image',
      FILE: '/upload/file',
    },

    // 聊天相关
    CHAT: {
      SEND_MESSAGE: '/chat/message',
      GET_HISTORY: '/chat/history',
      GET_SESSION: '/chat/session',
      CREATE_SESSION: '/chat/session',
      DELETE_SESSION: '/chat/session',
    },

    // 推荐系统
    RECOMMENDATIONS: {
      GET_RECOMMENDATIONS: '/recommendations',
      GET_MATCHES: '/recommendations/matches',
      UPDATE_PREFERENCES: '/recommendations/preferences',
      GET_PREFERENCES: '/recommendations/preferences',
    },

    // 联系人管理
    CONTACTS: {
      GET_CONTACTS: '/contacts',
      ADD_CONTACT: '/contacts',
      UPDATE_CONTACT: '/contacts',
      DELETE_CONTACT: '/contacts',
      REPORT_CONTACT: '/contacts/report',
      GET_CONTACT_HISTORY: '/contacts/history',
    },

    // 好友请求和通知
    NOTIFICATIONS: {
      GET_NOTIFICATIONS: '/notifications',
      MARK_AS_READ: '/notifications/read',
      GET_FRIEND_REQUESTS: '/notifications/friend-requests',
      SEND_FRIEND_REQUEST: '/notifications/friend-requests',
      RESPOND_FRIEND_REQUEST: '/notifications/friend-requests/respond',
      DELETE_NOTIFICATION: '/notifications',
    },

    // 匹配和搜索
    MATCHING: {
      SEARCH_USERS: '/matching/search',
      GET_MATCH_SCORE: '/matching/score',
      GET_MATCH_EXPLANATION: '/matching/explanation',
      UPDATE_CRITERIA: '/matching/criteria',
      GET_CRITERIA: '/matching/criteria',
    },

    // 接收数量管理
    RECEIVES: {
      GET_STATUS: '/receives/status',
      TOP_UP: '/receives/top-up',
      GIFT: '/receives/gift',
      GET_HISTORY: '/receives/history',
    },

    // 卡片滑动行为
    SWIPE: {
      RECORD_SWIPE: '/swipe/record',
      GET_SWIPE_HISTORY: '/swipe/history',
      GET_SWIPE_STATS: '/swipe/stats',
    },

    // Whisper消息系统
    WHISPERS: {
      SEND_WHISPER: '/whispers/send',
      GET_WHISPERS: '/whispers',
      RESPOND_WHISPER: '/whispers/respond',
      GET_WHISPER_SETTINGS: '/whispers/settings',
      UPDATE_WHISPER_SETTINGS: '/whispers/settings',
    },

    // 用户设置管理
    SETTINGS: {
      GET_USER_SETTINGS: '/settings',
      UPDATE_NOTIFICATION_SETTINGS: '/settings/notifications',
      UPDATE_USER_PREFERENCES: '/settings/preferences',
      GET_USER_STATS: '/settings/stats',
    },

    // 支付和订阅管理
    PAYMENTS: {
      PURCHASE_RECEIVES: '/payments/receives',
      CHANGE_PLAN: '/payments/plan',
      GET_TRANSACTIONS: '/payments/transactions',
      GET_PAYMENT_METHODS: '/payments/methods',
      CREATE_PAYMENT_SESSION: '/payments/session',
    },

    // 账户管理
    ACCOUNT: {
      LOGOUT: '/auth/logout',
      DELETE_ACCOUNT: '/account/delete',
      EXPORT_DATA: '/account/export',
      GET_ACCOUNT_INFO: '/account/info',
    },

    // 卡片跟踪 - 跟踪当前聊天窗口中最新的卡片
    CARD_TRACKING: {
      UPDATE_LATEST_CARD: '/chat/latest-card',
      GET_LATEST_CARD: '/chat/latest-card',
      CLEAR_LATEST_CARD: '/chat/latest-card',
    }
  }
};

// 环境检测
export const isDevelopment = (import.meta as any).env?.MODE === 'development';
export const isProduction = (import.meta as any).env?.MODE === 'production';

// 获取完整的API URL
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
}; 