# 聊天页面 API 集成文档

本文档详细说明了聊天页面（主页面）的数据接口实现和使用方法。

## 📁 文件结构

```
src/
├── types/api.ts                     # API 类型定义（已扩展）
├── services/
│   ├── config.ts                    # API 配置（已扩展）
│   ├── httpClient.ts                # HTTP 客户端
│   ├── chatService.ts               # 聊天 API 服务
│   ├── recommendationService.ts     # 推荐算法 API 服务
│   ├── contactService.ts           # 联系人管理 API 服务
│   ├── notificationService.ts      # 通知 API 服务
│   ├── matchingService.ts          # 匹配搜索 API 服务
│   └── index.ts                    # 统一导出（已更新）
├── hooks/
│   └── useChatInterface.ts         # 聊天界面自定义 hook
└── components/
    ├── ChatInterfaceAPI.tsx        # API 集成示例组件
    └── ui/
        ├── loading.tsx             # 加载状态组件
        └── error.tsx               # 错误显示组件
```

## 🔧 核心服务

### 1. 聊天服务 (ChatService)

**功能**: 处理 AI 对话、会话管理、消息历史

```typescript
import { chatService } from '../services';

// 发送消息
const response = await chatService.sendMessage({
  message: 'Find me a Python co-founder',
  sessionId: 'session_123',
  searchMode: 'inside',
  quotedContacts: ['user_1', 'user_2']
});

// 创建会话
const session = await chatService.createSession();

// 获取历史记录
const history = await chatService.getChatHistory({
  page: 1,
  limit: 20
});

// 模拟 AI 响应（开发环境）
const aiResponse = await chatService.simulateAIResponse(
  'Looking for startup mentors',
  'inside',
  userProfile
);
```

### 2. 推荐服务 (RecommendationService)

**功能**: 智能推荐、匹配计算、偏好设置

```typescript
import { recommendationService } from '../services';

// 获取智能推荐
const recommendations = await recommendationService.getIntelligentRecommendations(
  'Find AI researchers',
  'inside',
  userProfile,
  ['excluded_id_1']
);

// 计算匹配分数
const matchScore = await recommendationService.calculateMatchScore(
  'target_user_id',
  { skills: ['Python', 'AI'], collaborationType: 'co-founder' }
);

// 获取匹配解释
const explanation = await recommendationService.getMatchExplanation(
  'target_user_id',
  matchingCriteria
);
```

### 3. 联系人服务 (ContactService)

**功能**: 联系人增删改查、标签管理、举报

```typescript
import { contactService } from '../services';

// 添加联系人
const contact = await contactService.addContact({
  contactId: 'user_123',
  notes: 'Met through AI recommendations',
  tags: ['Co-founder Potential', 'AI Expert']
});

// 获取联系人列表
const contacts = await contactService.getContacts({
  page: 1,
  limit: 20,
  status: 'active',
  tags: ['High Priority']
});

// 举报联系人
await contactService.reportContact({
  contactId: 'user_123',
  reason: 'spam',
  description: 'Inappropriate behavior'
});

// 从推荐转换为联系人
const contactData = contactService.convertRecommendationToContact(recommendation);
```

### 4. 通知服务 (NotificationService)

**功能**: 通知管理、好友请求、接收数量

```typescript
import { notificationService } from '../services';

// 获取好友请求
const friendRequests = await notificationService.getFriendRequests({
  page: 1,
  limit: 10,
  status: 'pending'
});

// 发送好友请求
await notificationService.sendFriendRequest({
  recipientId: 'user_123',
  message: 'Would love to collaborate!',
  giftReceives: 2
});

// 获取未读通知数量
const unreadCount = await notificationService.getUnreadCount();

// 获取接收数量状态
const receivesStatus = await notificationService.getReceivesStatus();

// 充值接收数量
await notificationService.topUpReceives({
  amount: 10,
  paymentMethod: 'wechat'
});
```

### 5. 匹配服务 (MatchingService)

**功能**: 高级搜索、匹配算法、搜索分析

```typescript
import { matchingService } from '../services';

// 高级搜索
const searchResults = await matchingService.advancedSearch({
  searchMode: 'global',
  location: {
    countries: ['China'],
    cities: ['Beijing', 'Shanghai']
  },
  skills: {
    required: ['Python'],
    preferred: ['AI', 'Machine Learning']
  },
  pagination: { page: 1, limit: 20 },
  sorting: { by: 'match_score', order: 'desc' }
});

// 获取搜索建议
const suggestions = await matchingService.getSearchSuggestions('AI research');

// 保存搜索
await matchingService.saveSearch({
  name: 'AI Co-founders in Beijing',
  query: 'Python AI co-founder',
  filters: { location: ['Beijing'], skills: ['AI', 'Python'] }
});
```

## 🎯 自定义 Hook

### `useChatInterface` Hook

集成了所有聊天相关的状态管理和 API 调用：

```typescript
import { useChatInterface } from '../hooks/useChatInterface';

const {
  // 状态
  messages,
  isTyping,
  isLoading,
  error,
  searchMode,
  showCards,
  currentRecommendations,
  unreadNotifications,
  
  // 操作方法
  sendMessage,
  toggleSearchMode,
  addContact,
  handleCardWhisper,
  handleCardIgnore,
  addQuotedContact,
  showSingleCard,
  
  // 工具方法
  formatTime,
  getSuggestedQueries,
  clearError,
  
  // Refs
  messagesEndRef,
  cardsRef
} = useChatInterface(userProfile, addedContactIds);
```

## 💡 使用示例

### 完整的聊天界面集成

```typescript
// ChatInterfaceAPI.tsx - 完整示例
export function ChatInterfaceAPI({ userProfile, addedContactIds }) {
  const [inputValue, setInputValue] = useState('');
  
  const {
    messages,
    isTyping,
    error,
    sendMessage,
    handleCardWhisper,
    clearError
  } = useChatInterface(userProfile, addedContactIds);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    await sendMessage(inputValue);
    setInputValue('');
  };

  return (
    <div className="h-full flex flex-col">
      {/* 错误显示 */}
      {error && (
        <ErrorMessage 
          message={error} 
          onClose={clearError} 
        />
      )}
      
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto">
        {messages.map(message => (
          <div key={message.id}>
            {message.content}
          </div>
        ))}
      </div>
      
      {/* 输入区域 */}
      <div className="p-4">
        <input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask me to find connections..."
        />
        <button onClick={handleSendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}
```

### 错误处理

```typescript
try {
  const response = await chatService.sendMessage(request);
  
  if (response.success && response.data) {
    // 处理成功响应
    handleSuccessResponse(response.data);
  } else {
    // 处理业务错误
    setError(response.error || 'Request failed');
  }
} catch (error) {
  // 处理网络错误
  if (error instanceof ApiError) {
    setError(error.message);
  } else {
    setError('Network error occurred');
  }
}
```

### 加载状态管理

```typescript
const [isLoading, setIsLoading] = useState(false);

const handleAsyncOperation = async () => {
  try {
    setIsLoading(true);
    const result = await apiOperation();
    // 处理结果
  } finally {
    setIsLoading(false);
  }
};

return (
  <div>
    {isLoading && <LoadingOverlay message="Processing..." />}
    {/* 其他内容 */}
  </div>
);
```

## ⚙️ 配置

### 环境变量设置

创建 `.env.local` 文件：

```env
# API 基础 URL
VITE_API_BASE_URL=http://localhost:8000/api

# 开发模式设置
VITE_APP_MODE=development
VITE_APP_DEBUG=true

# 微信配置
VITE_WECHAT_APP_ID=your_wechat_app_id
```

### API 端点配置

在 `config.ts` 中已定义的端点：

```typescript
const ENDPOINTS = {
  CHAT: {
    SEND_MESSAGE: '/chat/message',
    GET_HISTORY: '/chat/history',
    CREATE_SESSION: '/chat/session',
  },
  RECOMMENDATIONS: {
    GET_RECOMMENDATIONS: '/recommendations',
    GET_MATCHES: '/recommendations/matches',
  },
  // ... 其他端点
};
```

## 🔄 开发 vs 生产环境

### 开发环境

- 使用模拟数据和响应
- 本地存储状态管理
- 详细的错误日志

```typescript
if ((import.meta as any).env?.MODE === 'development') {
  // 使用模拟响应
  const response = await chatService.simulateAIResponse(message);
} else {
  // 调用真实 API
  const response = await chatService.sendMessage(request);
}
```

### 生产环境

- 连接真实后端 API
- 错误监控和上报
- 性能优化

## 🚀 部署和集成

1. **安装依赖**:
   ```bash
   npm install
   ```

2. **配置环境变量**:
   ```bash
   cp .env.example .env.local
   # 编辑 .env.local 文件
   ```

3. **开发模式运行**:
   ```bash
   npm run dev
   ```

4. **生产构建**:
   ```bash
   npm run build
   ```

## 📈 性能优化

- 使用 React.memo 优化组件重渲染
- 实现虚拟滚动处理大量消息
- 缓存推荐结果减少 API 调用
- 防抖输入避免频繁搜索

## 🧪 测试

```typescript
// 使用 MSW 进行 API 模拟
import { rest } from 'msw';

export const handlers = [
  rest.post('/api/chat/message', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        data: {
          message: { /* AI 响应 */ },
          recommendations: [ /* 推荐用户 */ ]
        }
      })
    );
  }),
];
```

这个完整的 API 集成为聊天页面提供了全面的后端支持，包括智能对话、用户推荐、联系人管理等核心功能。所有服务都具有完整的类型安全、错误处理和开发/生产环境支持。 