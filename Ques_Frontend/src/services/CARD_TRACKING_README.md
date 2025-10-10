# 卡片跟踪功能 (Card Tracking Feature)

## 功能概述

卡片跟踪功能允许前端追踪并向后端报告当前聊天窗口中最新显示的卡片信息。后端可以通过API接口查询到这张最新的卡片。

## 使用场景

- **实时状态同步**: 后端可以了解用户当前正在查看哪张推荐卡片
- **用户行为分析**: 追踪用户在聊天界面中的卡片浏览行为
- **个性化推荐**: 基于用户当前查看的卡片优化后续推荐
- **跨设备同步**: 在多设备间同步用户的浏览状态

## API端点

### 1. 更新最新卡片
**端点**: `POST /api/chat/latest-card`

**请求体**:
```typescript
{
  cardData: UserRecommendation;      // 完整的卡片数据
  sessionId?: string;                // 所属的聊天会话ID
  messageId?: string;                // 关联的消息ID
  context?: {
    searchQuery?: string;            // 触发显示的搜索查询
    searchMode?: 'inside' | 'global'; // 搜索模式
    cardPosition?: number;           // 卡片在推荐列表中的位置
  };
}
```

**响应**:
```typescript
{
  success: boolean;
  data?: LatestCardInfo;
  message?: string;
}
```

### 2. 查询最新卡片
**端点**: `GET /api/chat/latest-card`

**响应**:
```typescript
{
  success: boolean;
  data?: {
    hasCard: boolean;                // 是否有最新卡片
    card?: LatestCardInfo;           // 卡片信息
    updatedAt?: string;              // 最后更新时间
  };
}
```

### 3. 清除最新卡片
**端点**: `DELETE /api/chat/latest-card`

**响应**:
```typescript
{
  success: boolean;
  message?: string;
}
```

## 前端使用方法

### 基础使用

```typescript
import { cardTrackingService } from '../services';

// 更新最新卡片
await cardTrackingService.updateLatestCard({
  cardData: recommendationCard,
  sessionId: 'session_123',
  context: {
    searchQuery: 'Find Python developers',
    searchMode: 'inside',
    cardPosition: 0
  }
});

// 查询最新卡片
const response = await cardTrackingService.getLatestCard();
if (response.success && response.data?.hasCard) {
  console.log('Latest card:', response.data.card);
}

// 清除最新卡片
await cardTrackingService.clearLatestCard();
```

### 快速更新（推荐）

```typescript
// 使用快捷方法，自动构建请求
await cardTrackingService.quickUpdateCard(card, {
  sessionId: 'session_123',
  searchQuery: 'Python co-founder',
  searchMode: 'inside',
  cardPosition: 0
});
```

### 批量卡片堆栈更新

```typescript
// 从卡片堆栈中自动选择当前显示的卡片
await cardTrackingService.updateFromCardStack(
  cards,              // 卡片数组
  currentIndex,       // 当前显示的卡片索引
  {
    sessionId: 'session_123',
    searchQuery: 'AI researchers',
    searchMode: 'global'
  }
);
```

### 本地缓存

```typescript
// 获取本地缓存的最新卡片（不调用API）
const cachedCard = cardTrackingService.getCachedLatestCard();

// 检查是否有最新卡片
if (cardTrackingService.hasLatestCard()) {
  console.log('Has latest card in cache');
}
```

## 自动集成

卡片跟踪功能已经自动集成到 `useChatInterface` Hook 中，在以下情况会自动更新：

1. **新卡片显示**: 当聊天返回推荐结果并显示卡片时
2. **单张卡片查看**: 当用户查看单张卡片详情时
3. **卡片切换**: 当用户滑动忽略当前卡片，显示下一张时
4. **发送Whisper**: 当用户向右滑动发送whisper后，更新为下一张卡片
5. **卡片关闭**: 当卡片堆栈关闭时，清除最新卡片

## 数据类型

### LatestCardInfo
```typescript
interface LatestCardInfo {
  cardData: UserRecommendation;     // 完整的卡片数据
  sessionId?: string;               // 所属的聊天会话ID
  messageId?: string;               // 关联的消息ID
  displayedAt: string;              // 卡片显示时间
  context?: {
    searchQuery?: string;           // 触发显示的搜索查询
    searchMode?: 'inside' | 'global'; // 搜索模式
    cardPosition?: number;          // 卡片在推荐列表中的位置
  };
}
```

## 后端实现要求

后端需要实现以下三个端点：

1. **POST /api/chat/latest-card** - 接收并存储最新卡片信息
2. **GET /api/chat/latest-card** - 返回当前用户的最新卡片
3. **DELETE /api/chat/latest-card** - 清除当前用户的最新卡片

### 存储建议

- 使用用户ID作为主键，每个用户只存储一张最新卡片
- 考虑添加过期时间（如30分钟无更新自动清除）
- 可以使用Redis等内存数据库提高查询性能

### 示例后端实现（伪代码）

```python
# 存储最新卡片
@app.post("/api/chat/latest-card")
async def update_latest_card(
    card_info: LatestCardInfo,
    user_id: str = Depends(get_current_user_id)
):
    # 存储到数据库或缓存
    await redis_client.setex(
        f"latest_card:{user_id}",
        1800,  # 30分钟过期
        json.dumps(card_info)
    )
    return {"success": True, "data": card_info}

# 查询最新卡片
@app.get("/api/chat/latest-card")
async def get_latest_card(
    user_id: str = Depends(get_current_user_id)
):
    card_data = await redis_client.get(f"latest_card:{user_id}")
    if card_data:
        return {
            "success": True,
            "data": {
                "hasCard": True,
                "card": json.loads(card_data),
                "updatedAt": datetime.now().isoformat()
            }
        }
    return {"success": True, "data": {"hasCard": False}}

# 清除最新卡片
@app.delete("/api/chat/latest-card")
async def clear_latest_card(
    user_id: str = Depends(get_current_user_id)
):
    await redis_client.delete(f"latest_card:{user_id}")
    return {"success": True, "message": "Latest card cleared"}
```

## 性能优化

### 节流机制
服务内置了1秒的更新节流，防止频繁的API调用：

```typescript
private readonly UPDATE_THROTTLE_MS = 1000; // 1秒内不重复更新
```

### 本地缓存
服务维护本地缓存，减少不必要的网络请求：

```typescript
// 自动缓存最后一次更新的卡片
private latestCardCache: LatestCardInfo | null = null;
```

## 错误处理

所有卡片跟踪操作都不会阻塞主要的用户交互流程。如果API调用失败，只会记录错误日志：

```typescript
cardTrackingService.quickUpdateCard(card, options)
  .catch(error => {
    console.error('Failed to update latest card:', error);
    // 不阻塞主流程
  });
```

## 调试和监控

### 控制台日志
服务会输出关键操作的日志：

```typescript
console.log('Latest card updated successfully:', cardInfo.cardData.name);
console.log('Latest card cleared');
```

### 验证方法

```typescript
// 验证卡片数据完整性
const validation = cardTrackingService.validateCardData(card);
if (!validation.isValid) {
  console.error('Invalid card data:', validation.errors);
}
```

### 格式化显示

```typescript
// 格式化卡片信息用于显示
const formatted = cardTrackingService.formatCardInfo(latestCard);
console.log(`${formatted.displayName} at ${formatted.displayTime}`);
console.log(`Context: ${formatted.displayContext}`);
```

## 最佳实践

1. **不要过度依赖**: 卡片跟踪是辅助功能，不应影响核心功能
2. **异步处理**: 所有卡片跟踪操作都应该是异步的，不阻塞用户操作
3. **错误容忍**: 即使卡片跟踪失败，应用也应正常运行
4. **隐私保护**: 确保只有授权用户可以访问自己的卡片信息
5. **定期清理**: 后端应定期清理过期的卡片数据

## 未来扩展

- 支持多卡片历史记录
- 添加卡片浏览时长统计
- 跨设备卡片状态同步
- 基于卡片浏览行为的智能推荐
- 卡片交互热力图分析

