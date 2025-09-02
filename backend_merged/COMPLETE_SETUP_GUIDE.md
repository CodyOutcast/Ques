# 🚀 Complete Setup Guide for Payment System

## ✅ **Current Status Check**
Your `.env` file has placeholder values that need to be updated with real credentials.

## 🔧 **Step 1: Tencent Cloud Console Setup**

### 1.1 WeChat Pay Setup
1. **Login to Tencent Cloud Console**: https://console.cloud.tencent.com/cpay
2. **Create Service Provider (服务商)**:
   - Service Provider Name: Your Company Name
   - Service Provider Abbreviation: Short Name
   - Administrator Phone: Your phone number
   - Callback URL: `https://ques.chat/api/v1/payments/notify`
   - Payment Success Page URL: `https://ques.chat/payment/success`

3. **Configure WeChat Pay Information**:
   - WeChat Pay Merchant ID (from WeChat Pay Platform)
   - API Key (from WeChat Pay Platform)
   - API Certificate (.p12 file from WeChat Pay Platform)
   - AppID (from WeChat Official Account Platform)

### 1.2 Alipay Setup (Optional)
1. **Configure Alipay Information**:
   - Service Provider App ID
   - Alipay App Signing Private Key
   - Alipay Verification Public Key
   - Partner ID

## 🔑 **Step 2: Required API Keys & Credentials**

### 2.1 WeChat Official Account Setup
**Required for WeChat login and WeChat Pay**

1. **Go to WeChat Official Account Platform**: https://mp.weixin.qq.com/
2. **Create/Configure Official Account**:
   - Account Type: Service Account (服务号)
   - Verification: Required for payment functionality
3. **Get Credentials**:
   - AppID: Found in Development > Basic Configuration
   - AppSecret: Found in Development > Basic Configuration
4. **Configure OAuth Domain**:
   - Add `ques.chat` to OAuth callback domains
   - Path: Development > Interface Permissions > Web Authorization

### 2.2 WeChat Pay Merchant Setup
**Required for payment processing**

1. **Apply for WeChat Pay**: https://pay.weixin.qq.com/
2. **Get Merchant Credentials**:
   - Merchant ID (mch_id)
   - API Key (API密钥)
   - API Certificate (apiclient_cert.p12)
3. **Configure Merchant Settings**:
   - Callback URL: `https://ques.chat/api/v1/payments/notify`
   - Domain whitelist: Add `ques.chat`

### 2.3 Alipay Merchant Setup (Optional)
1. **Create Alipay App**: https://open.alipay.com/
2. **Get App Credentials**:
   - App ID
   - Private Key (RSA2)
   - Public Key (RSA2)
   - Partner ID

## 📝 **Step 3: Update .env File**

Replace the placeholder values in your `.env` file:

```bash
# WeChat OAuth Configuration
WECHAT_APP_ID=wx1234567890abcdef  # From WeChat Official Account
WECHAT_SECRET=your_actual_secret_here  # From WeChat Official Account

# WeChat Pay Configuration
WECHAT_PAY_MCH_ID=1234567890  # From WeChat Pay Merchant
WECHAT_PAY_API_KEY=your_32_character_api_key_here  # From WeChat Pay Merchant
WECHAT_PAY_NOTIFY_URL=https://ques.chat/api/v1/payments/notify
WECHAT_PAY_SANDBOX=false  # Set to true for testing

# Alipay Configuration (if using Alipay)
ALIPAY_APP_ID=2023123456789012  # From Alipay Open Platform
ALIPAY_PRIVATE_KEY=MIIEvQIBADANBg...  # Your RSA private key
ALIPAY_PUBLIC_KEY=MIIBIjANBgkqhkiG9w0...  # Alipay's public key
ALIPAY_PARTNER_ID=2088123456789012  # From Alipay
```

## 🛡️ **Step 4: Certificate Setup**

### 4.1 WeChat Pay Certificate
1. **Download Certificate**: From WeChat Pay Merchant Platform
2. **Save Certificate**: Save `apiclient_cert.p12` file
3. **Update Code**: Add certificate path to payment service

### 4.2 SSL Certificate (Production)
Ensure your domain `ques.chat` has valid SSL certificate for HTTPS callbacks.

## 🔧 **Step 5: Domain Configuration**

### 5.1 WeChat Pay Domain Whitelist
Add these domains to WeChat Pay merchant settings:
- `ques.chat`
- Your actual production domain

### 5.2 WeChat OAuth Domains
Add these to WeChat Official Account OAuth settings:
- `ques.chat`

## 🧪 **Step 6: Testing Configuration**

### 6.1 Test Environment
1. **Set Sandbox Mode**:
   ```bash
   WECHAT_PAY_SANDBOX=true
   ```

2. **Use Test Credentials**: WeChat provides sandbox credentials for testing

### 6.2 Production Environment
1. **Set Production Mode**:
   ```bash
   WECHAT_PAY_SANDBOX=false
   ```

2. **Use Live Credentials**: Real merchant credentials

## 🚨 **Step 7: Security Checklist**

### 7.1 Callback URL Security
- ✅ Use HTTPS for all callback URLs
- ✅ Verify payment signatures
- ✅ Implement idempotency for payment callbacks

### 7.2 API Key Security
- ✅ Store API keys in environment variables only
- ✅ Never commit real credentials to version control
- ✅ Rotate API keys regularly

## 📋 **Step 8: Required Actions Summary**

### Immediate Actions Needed:
1. **Apply for WeChat Official Account** (if not done)
2. **Apply for WeChat Pay Merchant** (requires business license)
3. **Configure Tencent Cloud Payment Service**
4. **Update .env file with real credentials**
5. **Test payment flow in sandbox mode**

### Business Requirements:
- ✅ Business License (required for WeChat Pay)
- ✅ Bank Account for settlement
- ✅ Legal business entity

## 🔍 **Step 9: Verification Steps**

After configuration, test these endpoints:
1. **WeChat Login**: `GET /api/v1/auth/wechat/login`
2. **Create Payment**: `POST /api/v1/payments/create`
3. **Payment Callback**: `POST /api/v1/payments/notify`
4. **Payment Status**: `GET /api/v1/payments/{payment_id}/status`

## 📞 **Support Resources**

### WeChat Pay Support:
- Developer Documentation: https://pay.weixin.qq.com/wiki/doc/api/index.html
- Merchant Support: Contact through WeChat Pay Merchant Platform

### Tencent Cloud Support:
- Console: https://console.cloud.tencent.com/cpay
- Documentation: https://cloud.tencent.com/document/product/569

### Alipay Support:
- Developer Portal: https://open.alipay.com/
- Documentation: https://opendocs.alipay.com/

## ⚠️ **Important Notes**

1. **WeChat Pay requires business verification** - Individual accounts cannot apply
2. **Payment callbacks must use HTTPS** - HTTP will be rejected
3. **Domain verification is required** - Add your domain to all payment platforms
4. **Test thoroughly in sandbox** before going live
5. **Keep API keys secure** - Never expose them in client-side code

## 🎯 **Next Steps After Setup**

1. **Run Payment Tests**: `python test_payment_integration.py`
2. **Monitor Payment Logs**: Check `/logs` directory
3. **Set up Production Monitoring**: Configure alerting for payment failures
4. **Document Payment Flows**: For your team and users
