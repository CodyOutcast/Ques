# 卡片滑动API使用指南

本文档展示如何在前端组件中使用新实现的卡片滑动API功能。

## 概览

卡片滑动API提供以下功能：
- 记录用户的滑动行为（喜欢/忽略/超级喜欢）
- 离线缓存滑动行为，网络恢复时自动同步
- 基于滑动历史提供个性化推荐
- 滑动行为统计和分析

## 快速开始

### 1. 使用自定义Hook（推荐方式）

```typescript
import React from 'react';
import { useSwipeActions } from '../hooks/useSwipeActions';
import type { UserRecommendation } from '../types/api';

interface SwipeCardProps {
  recommendation: UserRecommendation;
  searchQuery?: string;
  searchMode?: 'inside' | 'global';
  sessionId?: string;
}

function SwipeCard({ recommendation, searchQuery, searchMode, sessionId }: SwipeCardProps) {
  const { handleLike, handleIgnore, handleSuperLike, syncCache } = useSwipeActions({
    searchQuery,
    searchMode,
    sessionId,
    onSwipeComplete: (rec, action) => {
      console.log(`Swiped ${action} on ${rec.name}`);
    },
    onError: (error, action) => {
      console.error(`Error during ${action}:`, error);
    }
  });

  return (
    <div className="swipe-card">
      {/* 卡片内容 */}
      <div className="card-content">
        <h3>{recommendation.name}</h3>
        <p>{recommendation.bio}</p>
      </div>

      {/* 滑动按钮 */}
      <div className="swipe-actions">
        <button onClick={() => handleIgnore(recommendation)}>
          忽略
        </button>
        <button onClick={() => handleSuperLike(recommendation)}>
          超级喜欢
        </button>
        <button onClick={() => handleLike(recommendation)}>
          喜欢
        </button>
      </div>

      {/* 同步缓存按钮（可选） */}
      <button onClick={syncCache}>
        同步离线数据
      </button>
    </div>
  );
}
```

### 2. 直接使用API服务

```typescript
import { recommendationService } from '../services';
import type { UserRecommendation } from '../types/api';

// 处理右滑（喜欢）
const handleRightSwipe = async (recommendation: UserRecommendation) => {
  try {
    await recommendationService.handleCardLike(recommendation, {
      searchQuery: "找一个Python合作伙伴",
      searchMode: 'inside',
      sessionId: 'session_123',
      cardPosition: 0
    });
    console.log('Successfully recorded like');
  } catch (error) {
    console.error('Failed to record like:', error);
  }
};

// 处理左滑（忽略）
const handleLeftSwipe = async (recommendation: UserRecommendation) => {
  try {
    await recommendationService.handleCardIgnore(recommendation, {
      searchQuery: "找一个Python合作伙伴",
      searchMode: 'inside',
      sessionId: 'session_123',
      cardPosition: 0
    });
    console.log('Successfully recorded ignore');
  } catch (error) {
    console.error('Failed to record ignore:', error);
  }
};
```

### 3. 在SwipeableCardStack中集成

```typescript
import React, { useState, useEffect } from 'react';
import { useSwipeActions } from '../hooks/useSwipeActions';
import { SwipeableCardStack } from '../components/SwipeableCardStack';
import type { UserRecommendation } from '../types/api';

interface EnhancedSwipeableCardStackProps {
  recommendations: UserRecommendation[];
  searchQuery?: string;
  searchMode?: 'inside' | 'global';
  sessionId?: string;
  onComplete?: () => void;
}

function EnhancedSwipeableCardStack({
  recommendations,
  searchQuery,
  searchMode,
  sessionId,
  onComplete
}: EnhancedSwipeableCardStackProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const { handleLike, handleIgnore, resetCardPosition, syncCache } = useSwipeActions({
    searchQuery,
    searchMode,
    sessionId,
    onSwipeComplete: (rec, action) => {
      console.log(`Swiped ${action} on ${rec.name}`);
      // 移动到下一张卡片
      setCurrentIndex(prev => prev + 1);
      
      // 如果所有卡片都滑完了
      if (currentIndex >= recommendations.length - 1) {
        onComplete?.();
      }
    },
    onError: (error, action) => {
      console.error(`Error during ${action}:`, error);
    }
  });

  // 组件挂载时重置卡片位置计数器
  useEffect(() => {
    resetCardPosition();
  }, [resetCardPosition]);

  // 页面可见性变化时同步缓存
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        syncCache();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [syncCache]);

  const currentRecommendation = recommendations[currentIndex];

  if (!currentRecommendation) {
    return <div>没有更多推荐了</div>;
  }

  return (
    <SwipeableCardStack
      recommendations={recommendations.slice(currentIndex)}
      onWhisper={(rec) => handleLike(rec)}
      onIgnore={(rec) => handleIgnore(rec)}
      onClose={onComplete}
      // 其他原有的props...
    />
  );
}
```

## 高级功能

### 1. 批量处理滑动行为

```typescript
import { recommendationService } from '../services';

const handleBatchSwipes = async (swipeActions: Array<{
  recommendation: UserRecommendation;
  action: 'like' | 'ignore' | 'super_like';
}>) => {
  try {
    await recommendationService.handleBatchSwipes(
      swipeActions.map(swipe => ({
        recommendation: swipe.recommendation,
        action: swipe.action,
        context: {
          searchQuery: "批量处理",
          searchMode: 'inside' as const,
          sessionId: 'batch_session'
        }
      }))
    );
    console.log('Batch swipes recorded successfully');
  } catch (error) {
    console.error('Failed to record batch swipes:', error);
  }
};
```

### 2. 获取滑动统计

```typescript
import { swipeService } from '../services';

const getSwipeStats = async () => {
  try {
    const response = await swipeService.getSwipeStats({
      period: 'week'
    });
    
    if (response.success && response.data) {
      console.log('Swipe stats:', response.data);
      // 显示统计数据：
      // - 总滑动次数
      // - 喜欢/忽略比例
      // - 匹配成功率
      // - 最常滑动的技能/位置
    }
  } catch (error) {
    console.error('Failed to get swipe stats:', error);
  }
};
```

### 3. 获取个性化推荐

```typescript
import { recommendationService } from '../services';

const getPersonalizedRecommendations = async () => {
  try {
    const response = await recommendationService.getPersonalizedRecommendations({
      excludeContacted: true,
      limit: 10,
      includeSimilarToLiked: true
    });
    
    if (response.success && response.data) {
      console.log('Personalized recommendations:', response.data);
      // 基于滑动历史的个性化推荐
    }
  } catch (error) {
    console.error('Failed to get personalized recommendations:', error);
  }
};
```

### 4. 智能滑动建议

```typescript
import { swipeService } from '../services';

const getSwipeSuggestions = async (targetUserId: string) => {
  try {
    const response = await swipeService.getSwipeSuggestions(targetUserId);
    
    if (response.success && response.data) {
      const { suggestedAction, confidence, reasoning } = response.data;
      
      console.log(`建议动作: ${suggestedAction}`);
      console.log(`置信度: ${confidence}%`);
      console.log(`理由: ${reasoning.join(', ')}`);
      
      // 可以在UI中显示这些建议
    }
  } catch (error) {
    console.error('Failed to get swipe suggestions:', error);
  }
};
```

## 错误处理和离线支持

API自动提供离线支持，当网络请求失败时，滑动行为会被缓存到本地存储，网络恢复时自动同步。

```typescript
import { useEffect } from 'react';
import { swipeService } from '../services';

// 在应用启动时同步离线缓存
useEffect(() => {
  const syncOfflineData = async () => {
    try {
      await swipeService.syncLocalCache();
      console.log('Offline data synced successfully');
    } catch (error) {
      console.error('Failed to sync offline data:', error);
    }
  };

  // 应用启动时同步
  syncOfflineData();

  // 网络恢复时同步
  window.addEventListener('online', syncOfflineData);
  
  return () => {
    window.removeEventListener('online', syncOfflineData);
  };
}, []);
```

## API端点

滑动相关的API端点配置在 `config.ts` 中：

```typescript
SWIPE: {
  RECORD_SWIPE: '/swipe/record',
  GET_SWIPE_HISTORY: '/swipe/history', 
  GET_SWIPE_STATS: '/swipe/stats',
}
```

## 类型定义

主要的TypeScript类型定义：

```typescript
// 滑动动作类型
export type SwipeAction = 'like' | 'ignore' | 'super_like';

// 滑动记录请求
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

// 滑动统计数据
export interface SwipeStats {
  totalSwipes: number;
  likes: number;
  ignores: number;
  superLikes: number;
  matchRate: number;
  mostSwipedSkills: string[];
  mostSwipedLocations: string[];
  averageMatchScore: number;
  dailySwipeCount: Array<{
    date: string;
    count: number;
  }>;
}
```

## 最佳实践

1. **使用自定义Hook**: 推荐使用 `useSwipeActions` Hook来简化滑动逻辑的集成。

2. **错误处理**: 总是包含适当的错误处理，API会自动缓存失败的请求。

3. **上下文信息**: 提供尽可能多的上下文信息（搜索查询、会话ID等）以便进行更好的分析。

4. **离线支持**: 利用内置的离线缓存功能，无需额外处理网络状态。

5. **性能优化**: 对于快速滑动场景，考虑使用批量API来减少网络请求。

这个API系统为AI搜索返回的卡片滑动功能提供了完整的后端支持，包括行为记录、统计分析和个性化推荐等功能。 