# Frontend API Documentation

> **Document Version**: 1.0.0  
> **Generated**: October 10, 2025  
> **Scope**: All API interfaces for Ques Frontend Application

## Table of Contents
- [Overview](#overview)
- [Base Configuration](#base-configuration)
- [Authentication System](#1-authentication-system-authservice)
- [User Profile](#2-user-profile-system-profileservice)
- [AI Profile Enhancement](#3-ai-profile-enhancement-service-profileaiservice)
- [University Verification](#4-university-verification-system-universityservice)
- [Recommendation System](#5-recommendation-system-recommendationservice)
- [Matching & Search](#6-matching--search-service-matchingservice)
- [Chat System](#7-chat-system-chatservice)
- [Card Swiping](#8-card-swiping-service-swipeservice)
- [Contact Management](#9-contact-management-contactservice)
- [Notification System](#10-notification-system-notificationservice)
- [Whisper Messaging](#11-whisper-messaging-system-whisperservice)
- [Payment System](#12-payment-system-paymentservice)
- [Settings Management](#13-settings-management-settingsservice)
- [Card Tracking](#14-card-tracking-service-cardtrackingservice)
- [Data Types](#data-type-definitions)

---

## Overview

This document describes all API interfaces between the Ques frontend application and backend. The frontend is developed in TypeScript, with all API calls handled through a unified HTTP client that supports:

- ✅ Automatic Token Management
- ✅ Request/Response Interception
- ✅ Unified Error Handling
- ✅ Automatic Retry Mechanism
- ✅ Offline Caching Support
- ✅ File Upload Progress Tracking

---

## Base Configuration

### API Base URL
```typescript
BASE_URL: 'http://localhost:8000/api' // Development environment
// Production environment reads from VITE_API_BASE_URL environment variable
```

### Authentication Mechanism
- **Header**: `Authorization: Bearer {token}`
- **Token Storage**: LocalStorage (`auth_token`)
- **Refresh Token**: LocalStorage (`refresh_token`)
- **User Info**: LocalStorage (`user_info`)

### Common Response Format
```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
```

### Paginated Response Format
```typescript
interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}
```

---

## 1. Authentication System (AuthService)

### 1.1 User Registration
```
POST /auth/register
```

**Request Body**:
```typescript
{
  // Basic Information
  demographics: {
    name: string;
    age: string;
    gender: 'male' | 'female' | 'other';
    location: string;
    hobbies: string[];
    languages: string[];
    oneSentenceIntro?: string;
    profilePhoto?: string;
  };
  
  // Skills and Resources
  skills: string[];
  resources: string[];
  
  // Project Experience
  projects: Array<{
    title: string;
    role: string;
    description: string;
    referenceLinks: string[];
  }>;
  
  // Goals and Demands
  goals: string[];
  demands: string[];
  
  // Institution Background
  institutions: Array<{
    name: string;
    role: string;
    description: string;
    verified: boolean;
  }>;
  
  // Optional Fields
  wechatId?: string;
  universityEmail?: string;
  university?: {
    name: string;
    verified: boolean;
  };
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    user: UserAuth;
    profile: UserProfile;
    token: string;
    refreshToken: string;
  }
}
```

### 1.2 User Login
```
POST /auth/login
```

**Request Body**:
```typescript
{
  wechatId?: string;
  phoneNumber?: string;
  verificationCode?: string;
}
```

**Response**: Same as registration response

### 1.3 Send Verification Code
```
POST /auth/send-code
```

**Request Body**:
```typescript
{
  email: string;
  type: 'university' | 'phone' | 'wechat';
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    sent: boolean;
    expiresIn: number; // Expiration time in seconds
  }
}
```

### 1.4 Verify Code
```
POST /auth/verify-code
```

**Request Body**:
```typescript
{
  email?: string;
  phoneNumber?: string;
  code: string;
  type: 'university' | 'phone' | 'wechat';
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    verified: boolean;
    token?: string;
  }
}
```

### 1.5 Refresh Token
```
POST /auth/refresh
```

**Request Body**:
```typescript
{
  refreshToken: string;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    token: string;
    refreshToken: string;
  }
}
```

### 1.6 Logout
```
POST /auth/logout
```

**Request Body**: None  
**Response**: `{ success: true }`

### 1.7 Upload Avatar
```
POST /upload/image (FormData)
```

**Request Body**:
```typescript
FormData {
  file: File;
  type: 'avatar';
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    url: string;
    filename: string;
    size: number;
    type: string;
  }
}
```

### 1.8 WeChat Login Authorization
```
GET /auth/wechat/authorize
```

**Response**:
```typescript
{
  success: true,
  data: {
    authUrl: string;
    state: string;
  }
}
```

### 1.9 WeChat Login Callback
```
POST /auth/wechat/callback
```

**Request Body**:
```typescript
{
  code: string;
  state: string;
}
```

**Response**: Same as login response

---

## 2. User Profile System (ProfileService)

### 2.1 Get User Profile
```
GET /profile
```

**Response**:
```typescript
{
  success: true,
  data: UserProfile
}
```

### 2.2 Update User Profile (Complete)
```
PUT /profile
```

**Request Body**: `Partial<UserProfile>`  
**Response**: Updated complete profile

### 2.3 Update Basic Information
```
PATCH /profile/demographics
```

**Request Body**:
```typescript
{
  demographics: {
    name?: string;
    age?: string;
    gender?: 'male' | 'female' | 'other';
    location?: string;
    hobbies?: string[];
    languages?: string[];
    oneSentenceIntro?: string;
  }
}
```

### 2.4 Update Skills
```
PATCH /profile/skills
```

**Request Body**: `{ skills: string[] }`

### 2.5 Update Resources
```
PATCH /profile/resources
```

**Request Body**: `{ resources: string[] }`

### 2.6 Project Management

#### Add Project
```
POST /profile/projects
```

**Request Body**:
```typescript
{
  project: {
    title: string;
    role: string;
    description: string;
    referenceLinks: string[];
  }
}
```

#### Update Project
```
PUT /profile/projects/{projectId}
```

**Request Body**: `{ project: Partial<ProjectInfo> }`

#### Delete Project
```
DELETE /profile/projects/{projectId}
```

### 2.7 Update Goals
```
PATCH /profile/goals
```

**Request Body**: `{ goals: string[] }`

### 2.8 Update Demands
```
PATCH /profile/demands
```

**Request Body**: `{ demands: string[] }`

### 2.9 Institution Management

#### Add Institution
```
POST /profile/institutions
```

**Request Body**:
```typescript
{
  institution: {
    name: string;
    role: string;
    description: string;
    verified: boolean;
  }
}
```

#### Update Institution
```
PUT /profile/institutions/{institutionId}
```

#### Delete Institution
```
DELETE /profile/institutions/{institutionId}
```

### 2.10 Upload Avatar
```
POST /profile/avatar (FormData)
```

**Request Body**: FormData with `avatar` field

### 2.11 Upload Photo (Advanced)
```
POST /profile/photo (FormData)
```

**Request Body**:
```typescript
FormData {
  file: File;
  type: 'avatar' | 'profile' | 'project' | 'verification';
  cropData?: string; // JSON serialized crop data
  quality?: 'low' | 'medium' | 'high';
  autoEnhance?: boolean;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    url: string;
    filename: string;
    size: number;
    type: string;
    thumbnails: {
      small: string;
      medium: string;
      large: string;
    };
    analysis: {
      quality: number;
      appropriateness: number;
      faceDetected: boolean;
      professionalScore: number;
      suggestions?: string[];
    };
  }
}
```

### 2.12 Batch Update Profile
```
PATCH /profile/batch
```

**Request Body**:
```typescript
{
  demographics?: Partial<UserDemographics>;
  skills?: string[];
  resources?: string[];
  goals?: string[];
  demands?: string[];
  projects?: ProjectInfo[];
  institutions?: InstitutionInfo[];
}
```

### 2.13 Update Profile Section
```
PUT /profile/section
```

**Request Body**:
```typescript
{
  section: 'basic-info' | 'skills' | 'resources' | 'projects' | 'goals' | 'demands' | 'institutions' | 'university';
  data: Partial<UserProfile>;
  validateOnly?: boolean;
}
```

### 2.14 Get Profile Completeness
```
GET /profile/completeness
```

**Response**:
```typescript
{
  success: true,
  data: {
    overall: number; // 0-100
    sections: {
      'basic-info': { completed: boolean; weight: number; suggestions?: string[] };
      'skills': { ... };
      // ... other sections
    };
    missingFields: Array<{
      section: ProfileSection;
      field: string;
      importance: 'high' | 'medium' | 'low';
      suggestion: string;
    }>;
  }
}
```

### 2.15 Generate Bio
```
POST /profile/generate-bio
```

**Request Body**:
```typescript
{
  style?: 'professional' | 'casual' | 'academic' | 'creative';
  length?: 'short' | 'medium' | 'long';
  includeSkills?: boolean;
  includeGoals?: boolean;
  includeExperience?: boolean;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    original?: string;
    generated: string;
    alternatives: string[];
    reasoning: string[];
  }
}
```

### 2.16 Analyze Profile
```
GET /profile/analyze
```

**Response**: Returns detailed profile analysis report

### 2.17 Profile Statistics
```
GET /profile/stats
```

**Response**:
```typescript
{
  success: true,
  data: {
    viewCount: number;
    matchCount: number;
    contactCount: number;
    responseRate: number;
    topSkills: Array<{ skill: string; matches: number; popularity: number }>;
    // ... more statistics
  }
}
```

### 2.18 Batch Update (Enhanced)
```
POST /profile/batch-update
```

**Request Body**:
```typescript
{
  updates: Array<{
    section: ProfileSection;
    data: Partial<UserProfile>;
    priority?: number;
  }>;
  validateAll?: boolean;
  applyImmediately?: boolean;
}
```

### 2.19 Validate Profile Section
```
POST /profile/section/validate
```

**Request Body**:
```typescript
{
  section: ProfileSection;
  data: any;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    suggestions: string[];
  }
}
```

---

## 3. AI Profile Enhancement Service (ProfileAIService)

### 3.1 Generate AI Suggestions
```
POST /profile/ai-suggestions
```

**Request Body**:
```typescript
{
  sections?: ProfileSection[];
  suggestionTypes?: ('enhancement' | 'rewrite' | 'addition' | 'correction' | 'optimization')[];
  focusAreas?: string[];
  targetAudience?: 'general' | 'technical' | 'business' | 'academic';
  style?: 'professional' | 'casual' | 'academic' | 'creative';
}
```

**Response**:
```typescript
{
  success: true,
  data: AISuggestion[] // List of suggestions
}
```

### 3.2 Apply AI Suggestion
```
POST /profile/ai-suggestions/apply
```

**Request Body**:
```typescript
{
  suggestionId: string;
  customizations?: Record<string, any>;
}
```

**Response**: Updated profile

### 3.3 Batch Apply AI Suggestions
```
POST /profile/ai-suggestions/apply/batch
```

**Request Body**:
```typescript
{
  suggestionIds: string[];
}
```

### 3.4 Generate Section Suggestion
```
POST /profile/ai-suggestions/section
```

**Request Body**:
```typescript
{
  section: ProfileSection;
  content: any;
  type?: AISuggestionType;
  style?: string;
  targetAudience?: string;
  focusAreas?: string[];
}
```

### 3.5 Batch Generate Suggestions
```
POST /profile/ai-suggestions/batch
```

**Request Body**:
```typescript
{
  sections: Array<{ section: ProfileSection; content: any }>;
  style?: string;
  targetAudience?: string;
  priority?: 'speed' | 'quality';
}
```

### 3.6 Enhance Content
```
POST /profile/ai-suggestions/enhance
```

**Request Body**:
```typescript
{
  section: ProfileSection;
  content: any;
  enhancementType: 'clarity' | 'professionalism' | 'engagement' | 'completeness' | 'conciseness';
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    original: any;
    enhanced: any;
    improvements: Array<{
      type: string;
      description: string;
      impact: number; // 1-10
    }>;
    confidence: number;
  }
}
```

### 3.7 Analyze Content Quality
```
POST /profile/ai-suggestions/analyze-quality
```

**Request Body**:
```typescript
{
  section: ProfileSection;
  content: any;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    overallScore: number; // 1-100
    dimensions: {
      clarity: number;
      professionalism: number;
      completeness: number;
      engagement: number;
      uniqueness: number;
    };
    suggestions: string[];
    strengths: string[];
    weaknesses: string[];
  }
}
```

### 3.8 Get Writing Tips
```
GET /profile/ai-suggestions/writing-tips?section={section}&userStyle={style}&industry={industry}
```

**Response**:
```typescript
{
  success: true,
  data: {
    tips: Array<{
      category: string;
      title: string;
      description: string;
      example?: string;
      priority: 'high' | 'medium' | 'low';
    }>;
    templates: Array<{
      name: string;
      content: string;
      suitableFor: string[];
    }>;
    commonMistakes: string[];
  }
}
```

---

## 4. University Verification System (UniversityService)

### 4.1 Search Universities
```
GET /universities/search?page={page}&limit={limit}&q={query}&country={country}
```

**Response**:
```typescript
{
  success: true,
  data: {
    data: Array<{
      id: string;
      name: string;
      domain: string[];
      country: string;
      verified: boolean;
      rank?: number;
    }>;
    pagination: { page, limit, total, totalPages };
  }
}
```

### 4.2 Get Popular Universities
```
GET /universities/search?limit={limit}&popular=true&country={country}
```

### 4.3 Get University by Domain
```
GET /universities/search/domain/{domain}
```

**Response**: Returns single university info or null

### 4.4 Send University Email Verification
```
POST /universities/send-verification
```

**Request Body**:
```typescript
{
  universityName: string;
  email: string;
  studentId?: string;
  graduationYear?: number;
  degree?: string;
  major?: string;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    sent: boolean;
    expiresIn: number;
    verificationId: string;
  }
}
```

### 4.5 Verify University Email
```
POST /universities/verify/{verificationId}
```

**Request Body**:
```typescript
{
  code: string;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    verified: boolean;
    universityInfo?: University;
  }
}
```

### 4.6 Get Verification Status
```
GET /universities/verify/status
```

**Response**: Returns verification status or null

### 4.7 Get Enhanced Verification Status
```
GET /universities/verify/status/{verificationId}
```

### 4.8 Enhanced University Verification
```
POST /universities/verify/enhanced
```

**Request Body**: Same as send verification  
**Response**: Includes verification status and next steps

### 4.9 Validate Domain
```
POST /universities/verify/validate-domain
```

**Request Body**:
```typescript
{
  email: string;
  universityName: string;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    isValid: boolean;
    university?: University;
    domain: string;
    suggestions: string[];
    confidence: number; // 1-100
  }
}
```

### 4.10 Get Verification Benefits
```
GET /universities/verify/benefits/{universityId}
```

**Response**: Returns available benefits and eligibility requirements

### 4.11 Request Alternative Verification
```
POST /universities/verify/alternative
```

**Request Body**:
```typescript
{
  universityId: string;
  method: 'document' | 'social' | 'third_party' | 'manual';
  data: any;
}
```

### 4.12 Get University Details
```
GET /universities/search/{universityId}
```

### 4.13 Get University Statistics
```
GET /universities/search/stats/{universityId}
```

**Response**: Returns rankings, statistics, programs, alumni info

---

## 5. Recommendation System (RecommendationService)

### 5.1 Get Recommendations
```
POST /recommendations
```

**Request Body**:
```typescript
{
  query?: string;
  searchMode?: 'inside' | 'global';
  filters?: {
    location?: string[];
    skills?: string[];
    university?: string[];
    industries?: string[];
    experienceLevel?: string[];
    availability?: string[];
  };
  excludeContacts?: string[];
  limit?: number;
  offset?: number;
}
```

**Response**:
```typescript
{
  success: true,
  data: UserRecommendation[]
}
```

### 5.2 Get Matches
```
POST /recommendations/matches
```

**Request Body**: MatchingCriteria  
**Response**: Paginated recommendation list

### 5.3 Update Preferences
```
PUT /recommendations/preferences
```

**Request Body**: MatchingCriteria  
**Response**: Updated preferences

### 5.4 Get Preferences
```
GET /recommendations/preferences
```

### 5.5 Smart Recommendations
```
GET /recommendations/smart?limit={limit}&excludeContacted={boolean}&refreshData={boolean}
```

### 5.6 Personalized Recommendations
```
GET /recommendations/personalized?excludeContacted={boolean}&limit={limit}&includeSimilarToLiked={boolean}
```

---

## 6. Matching & Search Service (MatchingService)

### 6.1 Search Users
```
POST /matching/search
```

**Request Body**: SearchParams + criteria  
**Response**: Paginated user list

### 6.2 Get Match Score
```
POST /matching/score/{targetUserId}
```

**Request Body**: MatchingCriteria (optional)  
**Response**:
```typescript
{
  success: true,
  data: {
    overall: number;
    skillsMatch: number;
    goalsAlignment: number;
    locationMatch: number;
    networkOverlap: number;
    availabilityMatch: number;
    experienceMatch: number;
  }
}
```

### 6.3 Get Match Explanation
```
POST /matching/explanation/{targetUserId}
```

**Request Body**: MatchingCriteria (optional)  
**Response**:
```typescript
{
  success: true,
  data: {
    reasons: string[];
    mutualBenefits: string[];
    potentialChallenges?: string[];
    suggestedAction: string;
  }
}
```

### 6.4 Update Matching Criteria
```
PUT /matching/criteria
```

### 6.5 Get Matching Criteria
```
GET /matching/criteria
```

### 6.6 Advanced Search
```
POST /matching/search/advanced
```

**Request Body**:
```typescript
{
  searchMode?: 'inside' | 'global';
  location?: {
    countries?: string[];
    cities?: string[];
    radius?: number;
  };
  demographics?: {
    ageRange?: [number, number];
    genders?: string[];
  };
  skills?: {
    required?: string[];
    preferred?: string[];
    exclude?: string[];
  };
  experience?: {
    levels?: string[];
    industries?: string[];
    roles?: string[];
  };
  education?: {
    universities?: string[];
    degrees?: string[];
    verified?: boolean;
  };
  availability?: {
    collaborationTypes?: string[];
    timeCommitment?: string[];
    remoteFriendly?: boolean;
  };
  other?: {
    hasProjects?: boolean;
    isOnline?: boolean;
    responseRate?: number;
    mutualConnections?: boolean;
  };
  pagination?: { page: number; limit: number };
  sorting?: {
    by: 'relevance' | 'match_score' | 'recent' | 'response_rate';
    order: 'asc' | 'desc';
  };
}
```

### 6.7 Search Suggestions
```
GET /matching/search/suggestions?q={query}
```

**Response**:
```typescript
{
  success: true,
  data: {
    queries: string[];
    skills: string[];
    locations: string[];
    universities: string[];
    industries: string[];
  }
}
```

### 6.8 Trending Searches
```
GET /matching/search/trending
```

### 6.9 Save Search
```
POST /matching/search/save
```

**Request Body**:
```typescript
{
  name: string;
  query?: string;
  filters: any;
}
```

### 6.10 Get Saved Searches
```
GET /matching/search/saved
```

### 6.11 Delete Saved Search
```
DELETE /matching/search/saved/{searchId}
```

### 6.12 Search Analytics
```
GET /matching/search/analytics
GET /matching/search/analytics/{searchId}
```

---

## 7. Chat System (ChatService)

### 7.1 Send Message
```
POST /chat/message
```

**Request Body**:
```typescript
{
  message: string;
  sessionId?: string;
  searchMode?: 'inside' | 'global';
  quotedContacts?: string[];
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    message: ChatMessage;
    sessionId: string;
    recommendations?: UserRecommendation[];
    suggestedQueries?: string[];
  }
}
```

### 7.2 Create Session
```
POST /chat/session
```

**Response**: ChatSession

### 7.3 Get Session Details
```
GET /chat/session/{sessionId}
```

### 7.4 Get Chat History
```
GET /chat/history?page={page}&limit={limit}&sessionId={sessionId}
```

**Response**: Paginated session list

### 7.5 Delete Session
```
DELETE /chat/session/{sessionId}
```

---

## 8. Card Swiping Service (SwipeService)

### 8.1 Record Swipe
```
POST /swipe/record
```

**Request Body**:
```typescript
{
  targetUserId: string;
  action: 'like' | 'ignore' | 'super_like';
  searchQuery?: string;
  searchMode?: 'inside' | 'global';
  matchScore?: number;
  sourceContext?: {
    sessionId?: string;
    recommendationBatch?: string;
    cardPosition?: number;
  };
}
```

**Response**: SwipeRecord

### 8.2 Batch Record Swipes
```
POST /swipe/record/batch
```

**Request Body**:
```typescript
{
  swipes: RecordSwipeRequest[];
}
```

### 8.3 Get Swipe History
```
GET /swipe/history?page={page}&limit={limit}&action={action}&startDate={date}&endDate={date}
```

### 8.4 Get Swipe Statistics
```
GET /swipe/stats?period={period}&startDate={date}&endDate={date}
```

**Response**:
```typescript
{
  success: true,
  data: {
    totalSwipes: number;
    likes: number;
    ignores: number;
    superLikes: number;
    matchRate: number;
    mostSwipedSkills: string[];
    mostSwipedLocations: string[];
    averageMatchScore: number;
    dailySwipeCount: Array<{ date: string; count: number }>;
  }
}
```

### 8.5 Get Swipe Preferences
```
GET /swipe/stats/preferences
```

**Response**: Preferred skills, locations, universities, swipe patterns, etc.

### 8.6 Get Swipe Suggestions
```
GET /swipe/stats/suggestions/{targetUserId}
```

**Response**: AI-generated swipe suggestions

### 8.7 Delete Swipe Record
```
DELETE /swipe/record/{swipeId}
```

### 8.8 Clear Swipe History
```
DELETE /swipe/record/bulk
```

**Request Body**:
```typescript
{
  olderThan?: string; // ISO date
  action?: SwipeAction;
}
```

---

## 9. Contact Management (ContactService)

### 9.1 Get Contact List
```
GET /contacts?page={page}&limit={limit}&status={status}&tags[]={tag}&q={query}
```

**Response**: Paginated contact list

### 9.2 Add Contact
```
POST /contacts
```

**Request Body**:
```typescript
{
  contactId: string;
  notes?: string;
  tags?: string[];
}
```

### 9.3 Update Contact
```
PUT /contacts/{contactId}
```

**Request Body**:
```typescript
{
  notes?: string;
  tags?: string[];
  status?: 'active' | 'blocked' | 'archived';
}
```

### 9.4 Delete Contact
```
DELETE /contacts/{contactId}
```

### 9.5 Report Contact
```
POST /contacts/report
```

**Request Body**:
```typescript
{
  contactId: string;
  reason: string;
  description?: string;
  attachments?: string[];
}
```

### 9.6 Get Contact History
```
GET /contacts/history/{contactId}
```

**Response**: Interaction history records

### 9.7 Batch Add Contacts
```
POST /contacts/batch
```

**Request Body**:
```typescript
{
  contacts: Array<{
    contactId: string;
    notes?: string;
    tags?: string[];
  }>;
}
```

### 9.8 Get Contact Statistics
```
GET /contacts/stats
```

**Response**: Total count, status distribution, top skills/locations, etc.

### 9.9 Search Contacts
```
POST /contacts/search
```

**Request Body**:
```typescript
{
  query: string;
  filters?: {
    skills?: string[];
    location?: string;
    university?: string;
    tags?: string[];
  };
}
```

### 9.10 Export Contacts
```
POST /contacts/export
```

**Request Body**: `{ format: 'csv' | 'json' }`  
**Response**: Download link

---

## 10. Notification System (NotificationService)

### 10.1 Get Notification List
```
GET /notifications?page={page}&limit={limit}&type={type}&unreadOnly={boolean}
```

**Response**: Paginated notification list

### 10.2 Mark as Read
```
POST /notifications/read
```

**Request Body**:
```typescript
{
  notificationIds: string[];
}
```

### 10.3 Delete Notification
```
DELETE /notifications/{notificationId}
```

### 10.4 Get Friend Requests
```
GET /notifications/friend-requests?page={page}&limit={limit}&status={status}&direction={direction}
```

### 10.5 Send Friend Request
```
POST /notifications/friend-requests
```

**Request Body**:
```typescript
{
  recipientId: string;
  message?: string;
  giftReceives?: number;
}
```

### 10.6 Respond to Friend Request
```
POST /notifications/friend-requests/respond
```

**Request Body**:
```typescript
{
  requestId: string;
  action: 'accept' | 'decline';
  message?: string;
}
```

### 10.7 Get Unread Count
```
GET /notifications/unread-count
```

**Response**:
```typescript
{
  success: true,
  data: {
    total: number;
    friendRequests: number;
    messages: number;
    matches: number;
    system: number;
    gifts: number;
  }
}
```

### 10.8 Batch Operations
```
POST /notifications/read  // Batch mark as read
POST /notifications/batch  // Batch delete
```

### 10.9 Update Notification Preferences
```
PUT /notifications/preferences
```

**Request Body**:
```typescript
{
  emailNotifications: boolean;
  pushNotifications: boolean;
  friendRequests: boolean;
  matches: boolean;
  messages: boolean;
  system: boolean;
  gifts: boolean;
}
```

### 10.10 Get Notification Preferences
```
GET /notifications/preferences
```

### 10.11 Receives Management

#### Get Receives Status
```
GET /receives/status
```

**Response**:
```typescript
{
  success: true,
  data: {
    remaining: number;
    total: number;
    resetDate: string;
    plan: 'basic' | 'pro';
  }
}
```

#### Top Up
```
POST /receives/top-up
```

**Request Body**:
```typescript
{
  amount: number;
  paymentMethod?: string;
}
```

#### Gift
```
POST /receives/gift
```

**Request Body**:
```typescript
{
  recipientId: string;
  amount: number;
  message?: string;
}
```

#### Get History
```
GET /receives/history?page={page}&limit={limit}&type={type}
```

---

## 11. Whisper Messaging System (WhisperService)

### 11.1 Send Whisper
```
POST /whispers/send
```

**Request Body**:
```typescript
{
  recipientId: string;
  message?: string;
  senderProfile: {
    id: string;
    name: string;
    avatar: string;
    location: string;
    skills: string[];
    bio: string;
    matchScore: number;
    wechatId: string;
    // ... other profile fields
  };
  context?: {
    searchQuery?: string;
    searchMode?: 'inside' | 'global';
    matchExplanation?: string;
    giftReceives?: number;
  };
}
```

### 11.2 Get Received Whispers
```
GET /whispers?page={page}&limit={limit}&status={status}
```

### 11.3 Get Sent Whispers
```
GET /whispers/sent?page={page}&limit={limit}&status={status}
```

### 11.4 Respond to Whisper
```
POST /whispers/respond
```

**Request Body**:
```typescript
{
  whisperId: string;
  action: 'accept' | 'decline';
  responseMessage?: string;
}
```

### 11.5 Get Whisper Settings
```
GET /whispers/settings
```

**Response**:
```typescript
{
  success: true,
  data: {
    wechatId: string;
    customMessage?: string;
    autoAccept: boolean;
    showOnlineStatus: boolean;
    enableNotifications: boolean;
  }
}
```

### 11.6 Update Whisper Settings
```
PUT /whispers/settings
```

**Request Body**: Partial<WhisperSettings>

### 11.7 Get Whisper Details
```
GET /whispers/{whisperId}
```

### 11.8 Delete Whisper
```
DELETE /whispers/{whisperId}
```

### 11.9 Mark as Read
```
PATCH /whispers/{whisperId}/read
```

### 11.10 Batch Mark as Read
```
PATCH /whispers/read/batch
```

**Request Body**: `{ whisperIds: string[] }`

---

## 12. Payment System (PaymentService)

### 12.1 Purchase Receives
```
POST /payments/receives
```

**Request Body**:
```typescript
{
  amount: number; // 1-100
  paymentMethod?: 'wechat_pay' | 'alipay' | 'credit_card';
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    transactionId: string;
    amount: number;
    cost: number;
    newBalance: number;
    paymentUrl?: string;
    status: 'pending' | 'completed' | 'failed';
    createdAt: string;
  }
}
```

### 12.2 Change Plan
```
POST /payments/plan
```

**Request Body**:
```typescript
{
  newPlan: 'basic' | 'pro';
  paymentMethod?: 'wechat_pay' | 'alipay' | 'credit_card';
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    transactionId?: string;
    oldPlan: UserPlan;
    newPlan: UserPlan;
    monthlyFee?: number;
    paymentUrl?: string;
    status: 'completed' | 'pending' | 'failed';
    effectiveDate: string;
  }
}
```

### 12.3 Get Transaction History
```
GET /payments/transactions?page={page}&limit={limit}&type={type}&status={status}&startDate={date}&endDate={date}
```

**Response**: Paginated transaction records

### 12.4 Get Payment Methods
```
GET /payments/methods
```

**Response**:
```typescript
{
  success: true,
  data: Array<{
    id: string;
    name: string;
    type: 'wechat_pay' | 'alipay' | 'credit_card';
    enabled: boolean;
    description?: string;
    icon?: string;
  }>
}
```

### 12.5 Create Payment Session
```
POST /payments/session
```

**Request Body**:
```typescript
{
  type: 'purchase_receives' | 'plan_upgrade';
  amount: number;
  paymentMethod: 'wechat_pay' | 'alipay' | 'credit_card';
  metadata?: Record<string, any>;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    sessionId: string;
    paymentUrl: string;
    qrCode?: string;
    expiresAt: string;
  }
}
```

### 12.6 Get Transaction Details
```
GET /payments/transactions/{transactionId}
```

### 12.7 Cancel Transaction
```
PATCH /payments/transactions/{transactionId}/cancel
```

---

## 13. Settings Management (SettingsService)

### 13.1 Get User Settings
```
GET /settings
```

**Response**:
```typescript
{
  success: true,
  data: {
    id: string;
    userId: string;
    plan: 'basic' | 'pro';
    receivesLeft: number;
    whisperCount: number;
    notifications: {
      whisperRequests: boolean;
      matches: boolean;
      messages: boolean;
      system: boolean;
    };
    preferences: {
      searchMode: 'inside' | 'global';
      autoAcceptMatches: boolean;
      showOnlineStatus: boolean;
    };
    createdAt: string;
    updatedAt: string;
  }
}
```

### 13.2 Update Notification Settings
```
PUT /settings/notifications
```

**Request Body**:
```typescript
{
  notifications: {
    whisperRequests?: boolean;
    matches?: boolean;
    messages?: boolean;
    system?: boolean;
  };
}
```

### 13.3 Update User Preferences
```
PUT /settings/preferences
```

**Request Body**:
```typescript
{
  preferences: {
    searchMode?: 'inside' | 'global';
    autoAcceptMatches?: boolean;
    showOnlineStatus?: boolean;
  };
}
```

### 13.4 Get User Statistics
```
GET /settings/stats
```

**Response**:
```typescript
{
  success: true,
  data: {
    totalWhispersSent: number;
    totalWhispersReceived: number;
    totalMatches: number;
    totalReceivesUsed: number;
    joinDate: string;
    lastActiveDate: string;
  }
}
```

### 13.5 Account Management

#### Logout
```
POST /auth/logout
```

**Request Body**: `{ allDevices?: boolean }`

#### Delete Account
```
POST /account/delete
```

**Request Body**:
```typescript
{
  confirmPassword: string;
  reason?: string;
  feedback?: string;
}
```

**Response**:
```typescript
{
  success: true,
  data: {
    message: string;
    deletedAt: string;
    dataRetentionDays: number;
  }
}
```

#### Export Data
```
POST /account/export
```

**Response**: `{ downloadUrl: string; expiresAt: string }`

#### Get Account Info
```
GET /account/info
```

**Response**:
```typescript
{
  success: true,
  data: {
    userId: string;
    email: string;
    createdAt: string;
    lastLoginAt: string;
    dataRetentionDays: number;
  }
}
```

---

## 14. Card Tracking Service (CardTrackingService)

### 14.1 Update Latest Card
```
POST /chat/latest-card
```

**Request Body**:
```typescript
{
  cardData: UserRecommendation;
  sessionId?: string;
  messageId?: string;
  context?: {
    searchQuery?: string;
    searchMode?: 'inside' | 'global';
    cardPosition?: number;
  };
}
```

**Response**: LatestCardInfo

### 14.2 Get Latest Card
```
GET /chat/latest-card
```

**Response**:
```typescript
{
  success: true,
  data: {
    hasCard: boolean;
    card?: LatestCardInfo;
    updatedAt?: string;
  }
}
```

### 14.3 Clear Latest Card
```
DELETE /chat/latest-card
```

---

## Data Type Definitions

### UserProfile
Complete user profile, including:
- demographics: Basic information (name, age, gender, location, etc.)
- skills: Skills list
- resources: Resources list
- projects: Project experience
- goals: Goals
- demands: Demands
- institutions: Institution background
- university: University information

### UserRecommendation
Recommended user card, including:
- User basic information
- matchScore: Match score
- whyMatch: Match reason
- receivesLeft: Remaining receives
- isOnline: Online status
- mutualConnections: Mutual connections count
- responseRate: Response rate

### AISuggestion
AI enhancement suggestion, including:
- section: Profile section
- type: Suggestion type (enhancement/rewrite/addition, etc.)
- priority: Priority
- originalContent: Original content
- suggestedContent: Suggested content
- reasoning: Reasons
- impactScore: Impact score
- confidence: Confidence level

### SwipeRecord
Swipe record, including:
- targetUserId: Target user ID
- action: Swipe action (like/ignore/super_like)
- searchQuery: Search query
- matchScore: Match score
- sourceContext: Source context

### WhisperMessage
Whisper message, including:
- senderProfile: Sender profile
- status: Status (pending/accepted/declined/expired)
- context: Context information
- expiresAt: Expiration time

### Transaction
Transaction record, including:
- type: Type (purchase_receives/plan_upgrade, etc.)
- amount: Quantity/amount
- cost: Cost
- status: Status
- paymentMethod: Payment method

---

## Error Handling

All failed API calls throw `ApiError` with the following information:
```typescript
class ApiError extends Error {
  status?: number;      // HTTP status code
  code?: string;        // Error code
  details?: any;        // Detailed information
}
```

### Common Error Codes
- `401`: Unauthorized (token invalid or missing)
- `403`: Forbidden (insufficient permissions)
- `404`: Resource not found
- `422`: Validation failed
- `429`: Too many requests
- `500`: Server error

---

## Local Caching Strategy

### Swipe Behavior Cache
- SwipeService automatically caches failed swipe actions
- Maximum 50 records cached
- Auto-sync when network recovers

### Card Tracking Cache
- CardTrackingService caches latest card
- No duplicate updates within 1 second (throttled)

### Settings Local Storage
- WeChat ID: `user_wechat_id`
- Custom Whisper message: `custom_whisper_message`
- Notification settings: `notification_settings`

---

## File Upload

### Supported File Types
- Images: JPEG, PNG, GIF, WebP
- Documents: PDF (for verification)

### Upload Process
1. Create FormData object
2. Add file and metadata
3. Call upload method
4. Monitor upload progress (optional)

### Example
```typescript
const formData = new FormData();
formData.append('file', file);
formData.append('type', 'avatar');

await profileService.uploadAvatar(file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});
```

---

## WebSocket Support

Currently not implemented in frontend, but backend may support real-time notifications. Suggested implementation:
- Online status updates
- Real-time message notifications
- New friend request alerts
- Match notifications

---

## API Versioning

Current API version controlled through URL path:
- Base path: `/api`
- Future versions may use: `/api/v2`, `/api/v3`

---

## Security Recommendations

### Token Management
- Tokens stored in LocalStorage
- Automatically added to Header in each request
- Auto-clear and redirect to login on 401 error

### Sensitive Data
- Passwords not stored in frontend
- Payment information transmitted via HTTPS encryption
- Verification codes have time limits

---

## Performance Optimization

### Request Optimization
- Request deduplication support
- Auto-retry failed requests
- Batch operations to reduce request count

### Caching Strategy
- User profile caching
- Temporary search result caching
- Local-first display

---

## Development Tools

### Type Safety
- Complete TypeScript type definitions
- API response type checking
- Compile-time error detection

### Debugging Support
- Console error logging
- Network request tracking
- Response data validation

---

## Appendix

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000/api  # API Base URL
```

### Common Status Codes
| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | Deleted (No Content) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Failed |
| 429 | Too Many Requests |
| 500 | Server Error |

---

## Changelog

### v1.0.0 (October 10, 2025)
- Initial release
- Complete API interface documentation
- Includes 14 major service modules
- 100+ API endpoints

---

**Document Maintainer**: Frontend Development Team  
**Feedback Channel**: Submit issues or contact backend team  
**Last Updated**: October 10, 2025

