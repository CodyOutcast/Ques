# API Endpoints Documentation

## Main Application Endpoints
- **GET** `/`
- **GET** `/health`
- **GET** `/api/v1/info`

## Router Endpoints
### Agent Cards (9 endpoints)
- **GET** `/recommendations`
- **POST** `/swipe`
- **GET** `/likes`
- **GET** `/history`
- **GET** `/statistics`
- **GET** `/preferences`
- **PUT** `/preferences`
- **POST** `/admin/create-cards`
- **GET** `/card/{card_id}`

### Auth (9 endpoints)
- **POST** `/register/email`
- **POST** `/login/email`
- **POST** `/verify-email`
- **POST** `/refresh`
- **POST** `/logout`
- **GET** `/me`
- **POST** `/resend-verification`
- **POST** `/forgot-password`
- **POST** `/reset-password`

### Chats (10 endpoints)
- **POST** `/greeting`
- **POST** `/greeting/respond`
- **POST** `/message`
- **GET** `/`
- **GET** `/pending`
- **GET** `/{chat_id}`
- **POST** `/messages/read`
- **DELETE** `/{chat_id}/block`
- **GET** `/{chat_id}/ws`
- **POST** `/search`

### Location (6 endpoints)
- **GET** `/me`
- **PUT** `/me`
- **POST** `/me/coordinates`
- **POST** `/me/address`
- **POST** `/nearby`
- **GET** `/user/{user_id}`

### Matches (1 endpoints)
- **POST** `/query`

### Matches Simple (2 endpoints)
- **POST** `/query`
- **GET** `/status`

### Membership (10 endpoints)
- **GET** `/status`
- **GET** `/limits`
- **POST** `/upgrade`
- **POST** `/downgrade`
- **GET** `/pricing`
- **GET** `/usage-history`
- **POST** `/subscription/create`
- **GET** `/subscription/status`
- **POST** `/subscription/cancel`
- **GET** `/subscription/pricing`

### Messages (7 endpoints)
- **GET** `/conversations`
- **GET** `/{match_id}/messages`
- **POST** `/{match_id}/messages`
- **DELETE** `/{message_id}`
- **GET** `/{match_id}/search`
- **GET** `/search/global`
- **GET** `/{match_id}/message/{message_id}/context`

### Online Users (7 endpoints)
- **GET** `/count`
- **GET** `/users`
- **GET** `/stats`
- **GET** `/user/{user_id}`
- **GET** `/sessions`
- **POST** `/cleanup`
- **GET** `/public/count`

### Payments (8 endpoints)
- **POST** `/wechat/orders`
- **POST** `/alipay/orders`
- **GET** `/history`
- **GET** `/status/{transaction_id}`
- **POST** `/webhooks/wechat`
- **POST** `/webhooks/alipay`
- **GET** `/subscription/current`
- **GET** `/pricing`

### Payments Broken (8 endpoints)
- **POST** `/alipay/orders`
- **POST** `/alipay/notify`
- **GET** `/alipay/orders/{order_id}`
- **GET** `/plans`
- **POST** `/create`
- **GET** `/status/{order_id}`
- **POST** `/notify`
- **GET** `/history`

### Payments Fixed (8 endpoints)
- **POST** `/wechat/orders`
- **POST** `/alipay/orders`
- **GET** `/history`
- **GET** `/status/{transaction_id}`
- **POST** `/webhooks/wechat`
- **POST** `/webhooks/alipay`
- **GET** `/subscription/current`
- **GET** `/pricing`

### Profile (6 endpoints)
- **GET** `/`
- **PUT** `/`
- **GET** `/links`
- **POST** `/links`
- **DELETE** `/links/{platform}`
- **GET** `/features`

### Projects (9 endpoints)
- **POST** `/`
- **GET** `/{project_id}`
- **PUT** `/{project_id}`
- **DELETE** `/{project_id}`
- **POST** `/{project_id}/users`
- **DELETE** `/{project_id}/users/{target_user_id}`
- **GET** `/users/{user_id}/projects`
- **GET** `/search/`
- **GET** `/`

### Project Cards (4 endpoints)
- **GET** `/my-cards`
- **GET** `/card-limit-status`
- **POST** `/`
- **DELETE** `/{card_id}`

### Project Ideas (3 endpoints)
- **POST** `/generate`
- **GET** `/test-scraping`
- **GET** `/health`

### Project Ideas V2 (4 endpoints)
- **POST** `/generate`
- **GET** `/quota`
- **GET** `/agents`
- **POST** `/test-unifuncs`

### Project Slots (11 endpoints)
- **GET** `/recommendations`
- **POST** `/swipe`
- **GET** `/swipe-history`
- **GET** `/slots`
- **GET** `/slots/{slot_id}`
- **PUT** `/slots/{slot_id}`
- **POST** `/slots/{slot_id}/publish`
- **DELETE** `/slots/{slot_id}`
- **GET** `/statistics`
- **GET** `/configuration`
- ... and 1 more endpoints

### Quota Payments (9 endpoints)
- **GET** `/pricing`
- **POST** `/purchase`
- **POST** `/confirm`
- **GET** `/status`
- **GET** `/history`
- **GET** `/calculate-price`
- **POST** `/webhook/payment`
- **GET** `/admin/stats`
- **GET** `/health`

### Recommendations (3 endpoints)
- **GET** `/users`
- **POST** `/swipe`
- **GET** `/cards`

### Revenue Analytics (11 endpoints)
- **GET** `/overview`
- **GET** `/chart/daily`
- **GET** `/chart/monthly`
- **GET** `/breakdown/membership`
- **GET** `/breakdown/payment-method`
- **GET** `/analytics/users`
- **GET** `/metrics/recurring`
- **GET** `/metrics/churn-retention`
- **GET** `/report/comprehensive`
- **GET** `/health`
- ... and 1 more endpoints

### Sms Router (5 endpoints)
- **POST** `/send-code`
- **POST** `/verify-code`
- **GET** `/status`
- **POST** `/register`
- **POST** `/cleanup-expired`

### Users (11 endpoints)
- **GET** `/profile`
- **PUT** `/profile`
- **GET** `/discover`
- **GET** `/{user_id}`
- **POST** `/swipe`
- **GET** `/search/`
- **GET** `/liked`
- **GET** `/liked/mutual`
- **DELETE** `/account`
- **GET** `/account/deletion-preview`
- ... and 1 more endpoints

### User Reports (10 endpoints)
- **POST** `/create`
- **GET** `/my-reports`
- **GET** `/against-me`
- **GET** `/pending`
- **GET** `/{report_id}`
- **POST** `/{report_id}/assign`
- **POST** `/{report_id}/resolve`
- **POST** `/{report_id}/dismiss`
- **GET** `/statistics/overview`
- **GET** `/user/{user_id}/violations`

### Vector Recommendations (4 endpoints)
- **GET** `/project-cards`
- **POST** `/update-user-vector`
- **POST** `/update-project-vector/{project_id}`
- **GET** `/health`

**Total API Endpoints: 178**