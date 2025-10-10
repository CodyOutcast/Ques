# API 服务文档

本目录包含了前端应用与后端API通信所需的所有服务。

## 文件结构

```
src/services/
├── config.ts           # API配置和端点定义
├── httpClient.ts       # HTTP客户端和错误处理
├── authService.ts      # 认证相关API服务
├── profileService.ts   # 用户资料API服务
├── universityService.ts # 大学验证API服务
├── index.ts            # 统一导出文件
└── README.md          # 本文档
```

## 主要服务

### 1. 认证服务 (authService)

处理用户注册、登录、认证等功能。

```typescript
import { authService } from '../services';

// 用户注册
const response = await authService.register({
  demographics: {
    name: 'John Doe',
    age: '25',
    gender: 'male',
    // ...其他信息
  },
  // ...完整用户资料
});

// 用户登录
const loginResponse = await authService.login({
  wechatId: 'user_wechat_id',
});

// 检查登录状态
const isLoggedIn = authService.isAuthenticated();

// 获取当前用户
const user = authService.getCurrentUser();

// 登出
await authService.logout();
```

### 2. 用户资料服务 (profileService)

管理用户资料的增删改查。

```typescript
import { profileService } from '../services';

// 获取用户资料
const profile = await profileService.getProfile();

// 更新基本信息
await profileService.updateDemographics({
  name: 'New Name',
  location: 'New Location',
});

// 更新技能
await profileService.updateSkills(['JavaScript', 'React', 'Node.js']);

// 上传头像
const uploadResponse = await profileService.uploadAvatar(file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});

// 批量更新资料
await profileService.batchUpdateProfile({
  skills: ['New Skill'],
  resources: ['New Resource'],
});
```

### 3. 大学验证服务 (universityService)

处理大学搜索、邮箱验证等功能。

```typescript
import { universityService } from '../services';

// 搜索大学
const universities = await universityService.searchUniversities({
  page: 1,
  limit: 10,
  query: 'Tsinghua',
  filters: { country: 'China' }
});

// 发送大学验证邮件
const verificationResponse = await universityService.sendUniversityVerification({
  universityName: 'Tsinghua University',
  email: 'student@tsinghua.edu.cn'
});

// 验证邮箱
const verifyResponse = await universityService.verifyUniversity(
  verificationId,
  '123456'
);

// 验证中国大学邮箱格式
const validation = universityService.validateChineseUniversityEmail(
  'student@tsinghua.edu.cn'
);
```

## 错误处理

所有API调用都会返回统一的响应格式：

```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
```

使用try-catch处理错误：

```typescript
try {
  const response = await authService.login(loginData);
  if (response.success) {
    // 处理成功响应
    console.log('Login successful:', response.data);
  } else {
    // 处理业务错误
    console.error('Login failed:', response.error);
  }
} catch (error) {
  // 处理网络错误或其他异常
  if (error instanceof ApiError) {
    console.error('API Error:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## 自定义Hook示例

推荐使用自定义Hook来封装API逻辑：

```typescript
// hooks/useProfileWizard.ts
import { useState, useCallback } from 'react';
import { authService, profileService } from '../services';

export function useProfileWizard() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitRegistration = useCallback(async (profile) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await authService.register(profile);
      
      if (response.success) {
        return true;
      } else {
        setError(response.error || 'Registration failed');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    submitRegistration,
  };
}
```

## 环境配置

在项目根目录创建 `.env.local` 文件：

```env
# API基础URL
VITE_API_BASE_URL=http://localhost:8000/api

# 开发模式
VITE_APP_MODE=development
VITE_APP_DEBUG=true

# 微信配置
VITE_WECHAT_APP_ID=your_wechat_app_id

# 文件上传配置
VITE_MAX_FILE_SIZE=10485760
VITE_ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif
```

## 类型定义

所有API相关的类型定义都在 `src/types/api.ts` 中：

```typescript
import type {
  ApiResponse,
  UserProfile,
  RegisterRequest,
  LoginRequest,
  LoginResponse,
  // ...其他类型
} from '../types/api';
```

## 最佳实践

1. **错误处理**: 始终处理API调用的错误情况
2. **加载状态**: 在API调用期间显示加载指示器
3. **类型安全**: 使用TypeScript类型确保数据安全
4. **缓存策略**: 对不经常变化的数据进行适当缓存
5. **网络优化**: 使用适当的请求超时和重试机制

## 与后端集成

确保后端API遵循以下约定：

- 使用标准HTTP状态码
- 返回统一的JSON响应格式
- 支持Bearer Token认证
- 实现适当的CORS策略
- 提供详细的API文档

## 测试

使用Mock Service Worker (MSW) 进行API测试：

```typescript
// __tests__/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.post('/api/auth/register', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        data: {
          token: 'mock_token',
          user: { id: '1', name: 'Test User' }
        }
      })
    );
  }),
];
```

这些API服务为前端应用提供了完整的后端通信能力，支持用户注册流程的所有功能。 