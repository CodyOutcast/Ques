import { httpClient, ApiError } from './httpClient';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  PurchaseReceivesRequest,
  PurchaseReceivesResponse,
  ChangePlanRequest,
  ChangePlanResponse,
  Transaction,
  GetTransactionsRequest,
  PaginatedResponse,
  UserPlan
} from '../types/api';

class PaymentService {
  /**
   * 购买receives
   */
  async purchaseReceives(request: PurchaseReceivesRequest): Promise<ApiResponse<PurchaseReceivesResponse>> {
    try {
      // 验证请求
      const validation = this.validatePurchaseReceivesRequest(request);
      if (!validation.isValid) {
        throw new Error(`Purchase validation failed: ${validation.errors.join(', ')}`);
      }

      const response = await httpClient.post<PurchaseReceivesResponse>(
        API_CONFIG.ENDPOINTS.PAYMENTS.PURCHASE_RECEIVES,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to purchase receives:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 升级/降级计划
   */
  async changePlan(request: ChangePlanRequest): Promise<ApiResponse<ChangePlanResponse>> {
    try {
      // 验证请求
      const validation = this.validateChangePlanRequest(request);
      if (!validation.isValid) {
        throw new Error(`Plan change validation failed: ${validation.errors.join(', ')}`);
      }

      const response = await httpClient.post<ChangePlanResponse>(
        API_CONFIG.ENDPOINTS.PAYMENTS.CHANGE_PLAN,
        request
      );

      return response;
    } catch (error) {
      console.error('Failed to change plan:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取交易历史
   */
  async getTransactions(params?: GetTransactionsRequest): Promise<ApiResponse<PaginatedResponse<Transaction>>> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params?.page) {
        searchParams.append('page', params.page.toString());
      }
      if (params?.limit) {
        searchParams.append('limit', params.limit.toString());
      }
      if (params?.type) {
        searchParams.append('type', params.type);
      }
      if (params?.status) {
        searchParams.append('status', params.status);
      }
      if (params?.startDate) {
        searchParams.append('startDate', params.startDate);
      }
      if (params?.endDate) {
        searchParams.append('endDate', params.endDate);
      }

      const url = `${API_CONFIG.ENDPOINTS.PAYMENTS.GET_TRANSACTIONS}${
        searchParams.toString() ? `?${searchParams.toString()}` : ''
      }`;

      const response = await httpClient.get<PaginatedResponse<Transaction>>(url);

      return response;
    } catch (error) {
      console.error('Failed to get transactions:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取支持的支付方式
   */
  async getPaymentMethods(): Promise<ApiResponse<Array<{
    id: string;
    name: string;
    type: 'wechat_pay' | 'alipay' | 'credit_card';
    enabled: boolean;
    description?: string;
    icon?: string;
  }>>> {
    try {
      const response = await httpClient.get<Array<{
        id: string;
        name: string;
        type: 'wechat_pay' | 'alipay' | 'credit_card';
        enabled: boolean;
        description?: string;
        icon?: string;
      }>>(API_CONFIG.ENDPOINTS.PAYMENTS.GET_PAYMENT_METHODS);

      return response;
    } catch (error) {
      console.error('Failed to get payment methods:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 创建支付会话
   */
  async createPaymentSession(params: {
    type: 'purchase_receives' | 'plan_upgrade';
    amount: number;
    paymentMethod: 'wechat_pay' | 'alipay' | 'credit_card';
    metadata?: Record<string, any>;
  }): Promise<ApiResponse<{
    sessionId: string;
    paymentUrl: string;
    qrCode?: string;
    expiresAt: string;
  }>> {
    try {
      const response = await httpClient.post<{
        sessionId: string;
        paymentUrl: string;
        qrCode?: string;
        expiresAt: string;
      }>(API_CONFIG.ENDPOINTS.PAYMENTS.CREATE_PAYMENT_SESSION, params);

      return response;
    } catch (error) {
      console.error('Failed to create payment session:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 获取特定交易详情
   */
  async getTransaction(transactionId: string): Promise<ApiResponse<Transaction>> {
    try {
      const response = await httpClient.get<Transaction>(
        `${API_CONFIG.ENDPOINTS.PAYMENTS.GET_TRANSACTIONS}/${transactionId}`
      );

      return response;
    } catch (error) {
      console.error('Failed to get transaction:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 取消未完成的交易
   */
  async cancelTransaction(transactionId: string): Promise<ApiResponse<void>> {
    try {
      const response = await httpClient.patch<void>(
        `${API_CONFIG.ENDPOINTS.PAYMENTS.GET_TRANSACTIONS}/${transactionId}/cancel`
      );

      return response;
    } catch (error) {
      console.error('Failed to cancel transaction:', error);
      throw this.handleError(error);
    }
  }

  /**
   * 验证购买receives请求
   */
  validatePurchaseReceivesRequest(request: PurchaseReceivesRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!request.amount || request.amount <= 0) {
      errors.push('Amount must be greater than 0');
    }

    if (request.amount > 100) {
      errors.push('Maximum purchase amount is 100 receives per transaction');
    }

    if (request.paymentMethod && !['wechat_pay', 'alipay', 'credit_card'].includes(request.paymentMethod)) {
      errors.push('Invalid payment method');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 验证计划变更请求
   */
  validateChangePlanRequest(request: ChangePlanRequest): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!request.newPlan || !['basic', 'pro'].includes(request.newPlan)) {
      errors.push('Valid plan is required (basic or pro)');
    }

    if (request.paymentMethod && !['wechat_pay', 'alipay', 'credit_card'].includes(request.paymentMethod)) {
      errors.push('Invalid payment method');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 计算购买费用
   */
  calculatePurchaseCost(amount: number): {
    amount: number;
    unitPrice: number; // 每个receive的价格
    totalCost: number;
    currency: string;
  } {
    const unitPrice = 1; // ¥1 per receive
    return {
      amount,
      unitPrice,
      totalCost: amount * unitPrice,
      currency: 'CNY'
    };
  }

  /**
   * 计算计划费用
   */
  calculatePlanCost(newPlan: UserPlan): {
    plan: UserPlan;
    monthlyFee: number;
    currency: string;
    features: string[];
  } {
    const planConfigs = {
      basic: {
        monthlyFee: 0,
        features: ['5 whispers per month', '5 receives per month']
      },
      pro: {
        monthlyFee: 10,
        features: ['Unlimited whispers', 'Unlimited receives', 'Custom whisper messages']
      }
    };

    const config = planConfigs[newPlan];
    return {
      plan: newPlan,
      monthlyFee: config.monthlyFee,
      currency: 'CNY',
      features: config.features
    };
  }

  /**
   * 格式化交易金额
   */
  formatAmount(amount: number, currency: string = 'CNY'): string {
    const formatters = {
      CNY: new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' }),
      USD: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })
    };

    const formatter = formatters[currency as keyof typeof formatters] || formatters.CNY;
    return formatter.format(amount);
  }

  /**
   * 获取交易状态的显示文本
   */
  getTransactionStatusText(status: Transaction['status']): string {
    const statusTexts = {
      pending: '处理中',
      completed: '已完成',
      failed: '失败',
      refunded: '已退款'
    };

    return statusTexts[status] || status;
  }

  /**
   * 统一错误处理
   */
  private handleError(error: any): Error {
    if (error instanceof ApiError) {
      return error;
    }
    
    if (error instanceof Error) {
      return new ApiError(error.message);
    }
    
    return new ApiError('Unknown error occurred');
  }
}

// 创建并导出支付服务实例
export const paymentService = new PaymentService();

// 导出默认实例
export default paymentService; 