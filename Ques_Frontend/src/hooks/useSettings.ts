import { useState, useEffect, useCallback } from 'react';
import { settingsService, paymentService } from '../services';
import type {
  UserSettings,
  UserPlan,
  PurchaseReceivesRequest,
  ChangePlanRequest,
  DeleteAccountRequest,
  Transaction
} from '../types/api';

interface UseSettingsState {
  // 用户设置
  userSettings: UserSettings | null;
  isLoadingSettings: boolean;
  settingsError: string | null;

  // 支付相关
  isProcessingPayment: boolean;
  paymentError: string | null;
  lastTransaction: Transaction | null;

  // UI状态
  showDeleteAccountModal: boolean;
  showTopUpModal: boolean;
  showTransactionHistory: boolean;

  // 本地设置
  wechatId: string;
  customWhisperMessage: string;
  notificationSettings: {
    whisperRequests: boolean;
  };
}

export function useSettings() {
  const [state, setState] = useState<UseSettingsState>({
    userSettings: null,
    isLoadingSettings: false,
    settingsError: null,
    isProcessingPayment: false,
    paymentError: null,
    lastTransaction: null,
    showDeleteAccountModal: false,
    showTopUpModal: false,
    showTransactionHistory: false,
    wechatId: settingsService.getLocalWechatId() || 'your_wechat_id',
    customWhisperMessage: settingsService.getLocalCustomWhisperMessage() || 'Hi! I found your profile through Ques and would love to connect. Looking forward to chatting!',
    notificationSettings: settingsService.getLocalNotificationSettings(),
  });

  // 更新状态的辅助函数
  const updateState = useCallback((updates: Partial<UseSettingsState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  // 加载用户设置
  const loadUserSettings = useCallback(async () => {
    try {
      updateState({ isLoadingSettings: true, settingsError: null });

      const response = await settingsService.getUserSettings();
      if (response.success) {
        updateState({ 
          userSettings: response.data,
          isLoadingSettings: false 
        });
      } else {
        throw new Error(response.error || 'Failed to load settings');
      }
    } catch (error) {
      console.error('Failed to load user settings:', error);
      updateState({
        isLoadingSettings: false,
        settingsError: error instanceof Error ? error.message : 'Failed to load settings'
      });
    }
  }, [updateState]);

  // 更新微信ID
  const updateWechatId = useCallback((newWechatId: string) => {
    settingsService.setLocalWechatId(newWechatId);
    updateState({ wechatId: newWechatId });
  }, [updateState]);

  // 更新自定义whisper消息
  const updateCustomWhisperMessage = useCallback((message: string) => {
    settingsService.setLocalCustomWhisperMessage(message);
    updateState({ customWhisperMessage: message });
  }, [updateState]);

  // 更新通知设置
  const updateNotificationSettings = useCallback(async (newSettings: { whisperRequests: boolean }) => {
    try {
      // 先更新本地设置
      settingsService.setLocalNotificationSettings(newSettings);
      updateState({ notificationSettings: newSettings });

      // 然后同步到服务器
      const response = await settingsService.updateNotificationSettings({
        notifications: newSettings
      });

      if (!response.success) {
        throw new Error(response.error || 'Failed to update notification settings');
      }
    } catch (error) {
      console.error('Failed to update notification settings:', error);
      // 如果服务器更新失败，恢复本地设置
      const oldSettings = settingsService.getLocalNotificationSettings();
      settingsService.setLocalNotificationSettings(oldSettings);
      updateState({ 
        notificationSettings: oldSettings,
        settingsError: error instanceof Error ? error.message : 'Failed to update notifications'
      });
    }
  }, [updateState]);

  // 购买receives
  const purchaseReceives = useCallback(async (amount: number, paymentMethod: 'wechat_pay' | 'alipay' | 'credit_card' = 'wechat_pay') => {
    try {
      updateState({ isProcessingPayment: true, paymentError: null });

      const request: PurchaseReceivesRequest = {
        amount,
        paymentMethod
      };

      const response = await paymentService.purchaseReceives(request);
      if (response.success && response.data) {
        updateState({
          isProcessingPayment: false,
          lastTransaction: {
            id: response.data.transactionId,
            type: 'purchase_receives',
            amount: response.data.amount,
            cost: response.data.cost,
            status: response.data.status,
            paymentMethod,
            description: `Purchase ${response.data.amount} receives`,
            createdAt: response.data.createdAt
          }
        });

        // 如果需要跳转支付页面
        if (response.data.paymentUrl) {
          window.open(response.data.paymentUrl, '_blank');
        }

        // 重新加载用户设置以获取最新余额
        await loadUserSettings();
      } else {
        throw new Error(response.error || 'Failed to purchase receives');
      }
    } catch (error) {
      console.error('Failed to purchase receives:', error);
      updateState({
        isProcessingPayment: false,
        paymentError: error instanceof Error ? error.message : 'Failed to purchase receives'
      });
    }
  }, [updateState, loadUserSettings]);

  // 升级/降级计划
  const changePlan = useCallback(async (newPlan: UserPlan, paymentMethod: 'wechat_pay' | 'alipay' | 'credit_card' = 'wechat_pay') => {
    try {
      updateState({ isProcessingPayment: true, paymentError: null });

      const request: ChangePlanRequest = {
        newPlan,
        paymentMethod
      };

      const response = await paymentService.changePlan(request);
      if (response.success && response.data) {
        updateState({
          isProcessingPayment: false,
          lastTransaction: response.data.transactionId ? {
            id: response.data.transactionId,
            type: newPlan === 'pro' ? 'plan_upgrade' : 'plan_downgrade',
            amount: response.data.monthlyFee || 0,
            cost: response.data.monthlyFee || 0,
            status: response.data.status,
            paymentMethod,
            description: `${newPlan === 'pro' ? 'Upgrade' : 'Downgrade'} to ${newPlan} plan`,
            createdAt: response.data.effectiveDate
          } : null
        });

        // 如果需要跳转支付页面（升级到Pro时）
        if (response.data.paymentUrl) {
          window.open(response.data.paymentUrl, '_blank');
        }

        // 重新加载用户设置以获取最新计划状态
        await loadUserSettings();
      } else {
        throw new Error(response.error || 'Failed to change plan');
      }
    } catch (error) {
      console.error('Failed to change plan:', error);
      updateState({
        isProcessingPayment: false,
        paymentError: error instanceof Error ? error.message : 'Failed to change plan'
      });
    }
  }, [updateState, loadUserSettings]);

  // 登出
  const logout = useCallback(async (allDevices: boolean = false) => {
    try {
      await settingsService.logout({ allDevices });
      
      // 清除本地设置
      settingsService.clearLocalSettings();
      
      // 重定向到登录页面或刷新页面
      window.location.reload();
    } catch (error) {
      console.error('Failed to logout:', error);
      updateState({
        settingsError: error instanceof Error ? error.message : 'Failed to logout'
      });
    }
  }, [updateState]);

  // 删除账户
  const deleteAccount = useCallback(async (request: DeleteAccountRequest) => {
    try {
      const validation = settingsService.validateDeleteAccountRequest(request);
      if (!validation.isValid) {
        throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
      }

      const response = await settingsService.deleteAccount(request);
      if (response.success && response.data) {
        // 清除所有本地数据
        settingsService.clearLocalSettings();
        
        // 显示删除成功消息并重定向
        alert(`Account deleted successfully. Your data will be retained for ${response.data.dataRetentionDays} days.`);
        window.location.href = '/';
      } else {
        throw new Error(response.error || 'Failed to delete account');
      }
    } catch (error) {
      console.error('Failed to delete account:', error);
      updateState({
        settingsError: error instanceof Error ? error.message : 'Failed to delete account'
      });
    }
  }, [updateState]);

  // UI控制函数
  const showDeleteAccountModal = useCallback(() => {
    updateState({ showDeleteAccountModal: true });
  }, [updateState]);

  const hideDeleteAccountModal = useCallback(() => {
    updateState({ showDeleteAccountModal: false });
  }, [updateState]);

  const showTopUpModal = useCallback(() => {
    updateState({ showTopUpModal: true });
  }, [updateState]);

  const hideTopUpModal = useCallback(() => {
    updateState({ showTopUpModal: false });
  }, [updateState]);

  // 清除错误
  const clearErrors = useCallback(() => {
    updateState({ settingsError: null, paymentError: null });
  }, [updateState]);

  // 初始化时加载设置
  useEffect(() => {
    loadUserSettings();
  }, [loadUserSettings]);

  return {
    // 状态
    ...state,
    
    // 操作函数
    loadUserSettings,
    updateWechatId,
    updateCustomWhisperMessage,
    updateNotificationSettings,
    purchaseReceives,
    changePlan,
    logout,
    deleteAccount,
    
    // UI控制
    showDeleteAccountModal,
    hideDeleteAccountModal,
    showTopUpModal,
    hideTopUpModal,
    clearErrors,
    
    // 计算属性
    currentPlan: state.userSettings?.plan || 'basic',
    receivesLeft: state.userSettings?.receivesLeft || 0,
    whisperCount: state.userSettings?.whisperCount || 0,
  };
} 