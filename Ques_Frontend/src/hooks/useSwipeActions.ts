import { useCallback, useRef } from 'react';
import { recommendationService } from '../services';
import type { UserRecommendation } from '../types/api';

interface UseSwipeActionsParams {
  searchQuery?: string;
  searchMode?: 'inside' | 'global';
  sessionId?: string;
  onSwipeComplete?: (recommendation: UserRecommendation, action: 'like' | 'ignore') => void;
  onError?: (error: Error, action: string) => void;
}

export function useSwipeActions({
  searchQuery,
  searchMode = 'inside',
  sessionId,
  onSwipeComplete,
  onError
}: UseSwipeActionsParams = {}) {
  const cardPositionRef = useRef(0);

  // 处理右滑（喜欢）
  const handleLike = useCallback(async (recommendation: UserRecommendation) => {
    try {
      await recommendationService.handleCardLike(recommendation, {
        searchQuery,
        searchMode,
        sessionId,
        cardPosition: cardPositionRef.current
      });

      onSwipeComplete?.(recommendation, 'like');
      cardPositionRef.current += 1;
    } catch (error) {
      console.error('Failed to handle like:', error);
      onError?.(error as Error, 'like');
    }
  }, [searchQuery, searchMode, sessionId, onSwipeComplete, onError]);

  // 处理左滑（忽略）
  const handleIgnore = useCallback(async (recommendation: UserRecommendation) => {
    try {
      await recommendationService.handleCardIgnore(recommendation, {
        searchQuery,
        searchMode,
        sessionId,
        cardPosition: cardPositionRef.current
      });

      onSwipeComplete?.(recommendation, 'ignore');
      cardPositionRef.current += 1;
    } catch (error) {
      console.error('Failed to handle ignore:', error);
      onError?.(error as Error, 'ignore');
    }
  }, [searchQuery, searchMode, sessionId, onSwipeComplete, onError]);

  // 处理超级喜欢
  const handleSuperLike = useCallback(async (recommendation: UserRecommendation) => {
    try {
      await recommendationService.handleCardSuperLike(recommendation, {
        searchQuery,
        searchMode,
        sessionId,
        cardPosition: cardPositionRef.current
      });

      onSwipeComplete?.(recommendation, 'like'); // Super like counts as like
      cardPositionRef.current += 1;
    } catch (error) {
      console.error('Failed to handle super like:', error);
      onError?.(error as Error, 'super_like');
    }
  }, [searchQuery, searchMode, sessionId, onSwipeComplete, onError]);

  // 同步离线缓存
  const syncCache = useCallback(async () => {
    try {
      await recommendationService.syncSwipeCache();
    } catch (error) {
      console.error('Failed to sync swipe cache:', error);
      onError?.(error as Error, 'sync_cache');
    }
  }, [onError]);

  // 重置卡片位置计数器
  const resetCardPosition = useCallback(() => {
    cardPositionRef.current = 0;
  }, []);

  return {
    handleLike,
    handleIgnore,
    handleSuperLike,
    syncCache,
    resetCardPosition,
    currentCardPosition: cardPositionRef.current
  };
}

export default useSwipeActions; 