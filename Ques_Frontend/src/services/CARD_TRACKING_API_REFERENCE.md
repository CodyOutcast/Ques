# 卡片跟踪API参考文档 (Card Tracking API Reference)

## 概述

这个文档为后端开发者提供卡片跟踪功能的API实现指南。前端通过这些API端点向后端报告用户当前正在查看的卡片信息。

---

## API端点列表

### 1. 更新最新卡片 (Update Latest Card)

更新或创建用户当前查看的最新卡片信息。

**端点**: `POST /api/chat/latest-card`

**认证**: 需要Bearer Token

**请求头**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**请求体**:
```json
{
  "cardData": {
    "id": "user_123",
    "name": "Sarah Chen",
    "age": "24",
    "gender": "Female",
    "avatar": "👩‍💻",
    "location": "Beijing, China",
    "hobbies": ["Rock Climbing", "Photography", "Cooking"],
    "languages": ["English", "Mandarin", "Python"],
    "skills": ["Python", "Machine Learning", "TensorFlow"],
    "resources": ["GPU Cluster Access", "Research Lab"],
    "projects": [
      {
        "title": "ML Ethics Framework",
        "role": "Lead Developer",
        "description": "Open-source framework for evaluating bias in ML models",
        "referenceLinks": ["https://github.com/example/ml-ethics"]
      }
    ],
    "goals": ["Build ethical AI products", "Start a tech company"],
    "demands": ["Co-founder with business experience", "Funding connections"],
    "institutions": [
      {
        "name": "Tsinghua University",
        "role": "PhD Student - Computer Science",
        "description": "Research focus on ethical AI",
        "verified": true
      }
    ],
    "university": {
      "name": "Tsinghua University",
      "verified": true
    },
    "matchScore": 95,
    "bio": "AI researcher passionate about ethical machine learning...",
    "oneSentenceIntro": "I build AI systems that solve real-world problems...",
    "whyMatch": "Perfect co-founder match! You both have strong Python skills...",
    "receivesLeft": 5
  },
  "sessionId": "session_abc123",
  "messageId": "msg_xyz789",
  "context": {
    "searchQuery": "Find me a Python co-founder",
    "searchMode": "inside",
    "cardPosition": 0
  }
}
```

**响应 200 OK**:
```json
{
  "success": true,
  "data": {
    "cardData": { /* 完整卡片数据 */ },
    "sessionId": "session_abc123",
    "messageId": "msg_xyz789",
    "displayedAt": "2025-10-10T10:30:00Z",
    "context": {
      "searchQuery": "Find me a Python co-founder",
      "searchMode": "inside",
      "cardPosition": 0
    }
  },
  "message": "Latest card updated successfully"
}
```

**错误响应**:

- **400 Bad Request**: 请求数据格式错误
```json
{
  "success": false,
  "error": "Invalid card data format"
}
```

- **401 Unauthorized**: 未认证或token过期
```json
{
  "success": false,
  "error": "Authentication required"
}
```

- **500 Internal Server Error**: 服务器错误
```json
{
  "success": false,
  "error": "Failed to update latest card"
}
```

---

### 2. 查询最新卡片 (Get Latest Card)

获取用户当前查看的最新卡片信息。

**端点**: `GET /api/chat/latest-card`

**认证**: 需要Bearer Token

**请求头**:
```
Authorization: Bearer {token}
```

**查询参数**: 无

**响应 200 OK (有卡片)**:
```json
{
  "success": true,
  "data": {
    "hasCard": true,
    "card": {
      "cardData": { /* 完整卡片数据 */ },
      "sessionId": "session_abc123",
      "messageId": "msg_xyz789",
      "displayedAt": "2025-10-10T10:30:00Z",
      "context": {
        "searchQuery": "Find me a Python co-founder",
        "searchMode": "inside",
        "cardPosition": 0
      }
    },
    "updatedAt": "2025-10-10T10:30:00Z"
  }
}
```

**响应 200 OK (无卡片)**:
```json
{
  "success": true,
  "data": {
    "hasCard": false
  }
}
```

**错误响应**:

- **401 Unauthorized**: 未认证或token过期
```json
{
  "success": false,
  "error": "Authentication required"
}
```

- **500 Internal Server Error**: 服务器错误
```json
{
  "success": false,
  "error": "Failed to retrieve latest card"
}
```

---

### 3. 清除最新卡片 (Clear Latest Card)

清除用户当前的最新卡片记录。

**端点**: `DELETE /api/chat/latest-card`

**认证**: 需要Bearer Token

**请求头**:
```
Authorization: Bearer {token}
```

**响应 200 OK**:
```json
{
  "success": true,
  "message": "Latest card cleared successfully"
}
```

**错误响应**:

- **401 Unauthorized**: 未认证或token过期
```json
{
  "success": false,
  "error": "Authentication required"
}
```

- **404 Not Found**: 没有找到卡片记录
```json
{
  "success": true,
  "message": "No card to clear"
}
```

- **500 Internal Server Error**: 服务器错误
```json
{
  "success": false,
  "error": "Failed to clear latest card"
}
```

---

## 数据模型

### LatestCardInfo

完整的最新卡片信息对象。

```typescript
interface LatestCardInfo {
  cardData: UserRecommendation;     // 用户推荐卡片的完整数据
  sessionId?: string;               // 所属的聊天会话ID
  messageId?: string;               // 关联的AI消息ID
  displayedAt: string;              // ISO 8601格式的显示时间
  context?: {                       // 上下文信息
    searchQuery?: string;           // 触发这张卡片显示的搜索查询
    searchMode?: 'inside' | 'global'; // 搜索模式（校内或全局）
    cardPosition?: number;          // 卡片在推荐列表中的位置（从0开始）
  };
}
```

### UserRecommendation

用户推荐卡片的数据结构（简化版，完整定义见类型文件）。

```typescript
interface UserRecommendation {
  id: string;                       // 用户唯一ID
  name: string;                     // 姓名
  age: string;                      // 年龄
  gender: string;                   // 性别
  avatar: string;                   // 头像（emoji或URL）
  location: string;                 // 地理位置
  hobbies: string[];                // 爱好列表
  languages: string[];              // 语言列表
  skills: string[];                 // 技能列表
  resources: string[];              // 资源列表
  projects: ProjectInfo[];          // 项目经历
  goals: string[];                  // 目标列表
  demands: string[];                // 需求列表
  institutions: InstitutionInfo[];  // 机构背景
  university?: UniversityInfo;      // 大学信息
  matchScore: number;               // 匹配分数 (0-100)
  bio: string;                      // 个人简介
  oneSentenceIntro?: string;        // 一句话介绍
  whyMatch: string;                 // AI生成的匹配原因
  receivesLeft?: number;            // 剩余接收次数
  isOnline?: boolean;               // 是否在线
  lastSeen?: string;                // 最后在线时间
  mutualConnections?: number;       // 共同联系人数量
  responseRate?: number;            // 回复率百分比
}
```

---

## 实现建议

### 1. 数据存储

**选项A: Redis (推荐用于生产环境)**

优点:
- 高性能的内存存储
- 原生支持TTL（自动过期）
- 易于横向扩展

```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def save_latest_card(user_id: str, card_info: dict):
    key = f"latest_card:{user_id}"
    # 30分钟后自动过期
    redis_client.setex(
        key,
        timedelta(minutes=30),
        json.dumps(card_info)
    )

def get_latest_card(user_id: str):
    key = f"latest_card:{user_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def clear_latest_card(user_id: str):
    key = f"latest_card:{user_id}"
    redis_client.delete(key)
```

**选项B: 关系型数据库**

适用于需要持久化存储和复杂查询的场景。

```sql
CREATE TABLE latest_cards (
    user_id VARCHAR(255) PRIMARY KEY,
    card_data JSON NOT NULL,
    session_id VARCHAR(255),
    message_id VARCHAR(255),
    displayed_at TIMESTAMP NOT NULL,
    context JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    INDEX idx_expires_at (expires_at)
);

-- 定期清理过期记录
DELETE FROM latest_cards WHERE expires_at < NOW();
```

### 2. 认证和授权

确保只有授权用户可以访问自己的卡片数据：

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """从JWT token中提取用户ID"""
    token = credentials.credentials
    try:
        # 解析JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

### 3. 完整API实现示例 (FastAPI)

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import json

app = FastAPI()

class CardContext(BaseModel):
    searchQuery: Optional[str] = None
    searchMode: Optional[str] = "inside"
    cardPosition: Optional[int] = 0

class LatestCardRequest(BaseModel):
    cardData: dict
    sessionId: Optional[str] = None
    messageId: Optional[str] = None
    context: Optional[CardContext] = None

class LatestCardResponse(BaseModel):
    cardData: dict
    sessionId: Optional[str]
    messageId: Optional[str]
    displayedAt: str
    context: Optional[CardContext]

@app.post("/api/chat/latest-card")
async def update_latest_card(
    request: LatestCardRequest,
    user_id: str = Depends(get_current_user_id)
):
    """更新用户的最新卡片"""
    try:
        card_info = {
            "cardData": request.cardData,
            "sessionId": request.sessionId,
            "messageId": request.messageId,
            "displayedAt": datetime.utcnow().isoformat() + "Z",
            "context": request.context.dict() if request.context else None
        }
        
        # 保存到Redis，30分钟后过期
        key = f"latest_card:{user_id}"
        redis_client.setex(
            key,
            timedelta(minutes=30),
            json.dumps(card_info)
        )
        
        return {
            "success": True,
            "data": card_info,
            "message": "Latest card updated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update latest card: {str(e)}"
        )

@app.get("/api/chat/latest-card")
async def get_latest_card(
    user_id: str = Depends(get_current_user_id)
):
    """获取用户的最新卡片"""
    try:
        key = f"latest_card:{user_id}"
        data = redis_client.get(key)
        
        if data:
            card_info = json.loads(data)
            return {
                "success": True,
                "data": {
                    "hasCard": True,
                    "card": card_info,
                    "updatedAt": card_info.get("displayedAt")
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "hasCard": False
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest card: {str(e)}"
        )

@app.delete("/api/chat/latest-card")
async def clear_latest_card(
    user_id: str = Depends(get_current_user_id)
):
    """清除用户的最新卡片"""
    try:
        key = f"latest_card:{user_id}"
        result = redis_client.delete(key)
        
        return {
            "success": True,
            "message": "Latest card cleared successfully" if result else "No card to clear"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear latest card: {str(e)}"
        )
```

### 4. 性能优化建议

1. **使用连接池**: 对Redis或数据库连接使用连接池
2. **异步IO**: 使用异步框架（如FastAPI）提高并发处理能力
3. **缓存策略**: 实现多层缓存（Redis + 本地缓存）
4. **批量清理**: 定期批量清理过期的卡片记录
5. **监控告警**: 监控API响应时间和错误率

### 5. 安全考虑

1. **数据验证**: 验证所有输入数据的格式和大小
2. **权限控制**: 确保用户只能访问自己的卡片数据
3. **速率限制**: 实现API速率限制防止滥用
4. **数据脱敏**: 在日志中脱敏敏感用户信息
5. **HTTPS**: 生产环境必须使用HTTPS

### 6. 监控和日志

```python
import logging
from prometheus_client import Counter, Histogram

# 定义指标
card_updates = Counter('card_updates_total', 'Total card updates')
card_queries = Counter('card_queries_total', 'Total card queries')
card_update_duration = Histogram('card_update_duration_seconds', 'Card update duration')

@app.post("/api/chat/latest-card")
async def update_latest_card(request: LatestCardRequest, user_id: str = Depends(get_current_user_id)):
    with card_update_duration.time():
        card_updates.inc()
        logging.info(f"Updating latest card for user: {user_id}")
        # ... 实现逻辑
```

---

## 测试

### 使用cURL测试

```bash
# 1. 更新最新卡片
curl -X POST http://localhost:8000/api/chat/latest-card \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cardData": {
      "id": "user_123",
      "name": "Sarah Chen",
      "age": "24",
      ...
    },
    "sessionId": "session_abc",
    "context": {
      "searchQuery": "Python developers",
      "searchMode": "inside"
    }
  }'

# 2. 查询最新卡片
curl -X GET http://localhost:8000/api/chat/latest-card \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 清除最新卡片
curl -X DELETE http://localhost:8000/api/chat/latest-card \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Python测试脚本

```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 测试更新
card_data = {
    "cardData": {"id": "user_123", "name": "Test User"},
    "sessionId": "session_test",
    "context": {"searchQuery": "test"}
}

response = requests.post(f"{BASE_URL}/chat/latest-card", 
                        json=card_data, 
                        headers=headers)
print("Update:", response.json())

# 测试查询
response = requests.get(f"{BASE_URL}/chat/latest-card", 
                       headers=headers)
print("Query:", response.json())

# 测试清除
response = requests.delete(f"{BASE_URL}/chat/latest-card", 
                          headers=headers)
print("Clear:", response.json())
```

---

## 常见问题 (FAQ)

**Q: 为什么需要卡片跟踪功能？**
A: 卡片跟踪帮助后端了解用户的实时浏览状态，可用于个性化推荐、行为分析和跨设备同步。

**Q: 卡片数据会永久保存吗？**
A: 不会。建议设置30分钟的自动过期时间，避免存储过期数据。

**Q: 如何处理并发更新？**
A: 每个用户只保存一张最新卡片，新的更新会覆盖旧的记录。

**Q: 前端更新失败会影响用户体验吗？**
A: 不会。卡片跟踪是非阻塞的辅助功能，失败不影响主流程。

**Q: 需要支持多卡片历史吗？**
A: 当前版本只支持单卡片，如需历史记录可扩展为列表存储。

---

## 版本历史

- **v1.0.0** (2025-10-10): 初始版本，支持基本的卡片跟踪功能

---

## 联系支持

如有问题或建议，请联系开发团队或提交Issue。

