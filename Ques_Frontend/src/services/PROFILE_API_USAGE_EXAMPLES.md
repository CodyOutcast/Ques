# 个人资料API使用指南

本文档展示如何使用新实现的个人资料编辑和AI润色API功能。

## 概览

个人资料API提供以下功能：
- 分段编辑用户资料
- AI智能润色建议
- 实时资料完整度分析
- 增强的照片上传功能
- 大学验证增强功能
- 资料统计和分析

## 快速开始

### 1. 基础资料更新

```typescript
import { profileService } from '../services';
import type { UpdateProfileSectionRequest } from '../types/api';

// 更新技能部分
const updateSkills = async (skills: string[]) => {
  try {
    const request: UpdateProfileSectionRequest = {
      section: 'skills',
      data: { skills }
    };
    
    const response = await profileService.updateProfileSection(request);
    if (response.success) {
      console.log('Skills updated:', response.data);
    }
  } catch (error) {
    console.error('Failed to update skills:', error);
  }
};

// 更新基本信息
const updateBasicInfo = async (demographics: any) => {
  try {
    const response = await profileService.updateProfileSection({
      section: 'basic-info',
      data: { demographics }
    });
    
    if (response.success) {
      console.log('Basic info updated:', response.data);
    }
  } catch (error) {
    console.error('Failed to update basic info:', error);
  }
};
```

### 2. 批量更新资料

```typescript
import { profileService } from '../services';
import type { BatchProfileUpdateRequest } from '../types/api';

const batchUpdateProfile = async () => {
  try {
    const request: BatchProfileUpdateRequest = {
      updates: [
        {
          section: 'skills',
          data: { skills: ['Python', 'React', 'TypeScript'] },
          priority: 9
        },
        {
          section: 'goals',
          data: { goals: ['Build innovative products', 'Lead a startup'] },
          priority: 7
        },
        {
          section: 'projects',
          data: { 
            projects: [
              {
                title: 'AI Chat Platform',
                role: 'Lead Developer',
                description: 'Built a conversational AI platform using GPT-4',
                referenceLinks: ['https://github.com/username/ai-chat']
              }
            ]
          },
          priority: 8
        }
      ],
      validateAll: true,
      applyImmediately: true
    };

    const response = await profileService.batchUpdateProfileEnhanced(request);
    if (response.success) {
      console.log('Profile batch updated:', response.data);
    }
  } catch (error) {
    console.error('Batch update failed:', error);
  }
};
```

### 3. AI润色功能

```typescript
import { profileAIService } from '../services';
import type { GenerateAISuggestionsRequest } from '../types/api';

// 生成AI改进建议
const generateSuggestions = async () => {
  try {
    const request: GenerateAISuggestionsRequest = {
      sections: ['skills', 'projects', 'goals'],
      targetAudience: 'technical',
      style: 'professional',
      focusAreas: ['clarity', 'professionalism', 'completeness']
    };

    const response = await profileService.generateAISuggestions(request);
    if (response.success) {
      console.log('AI suggestions:', response.data);
      
      // 显示建议
      response.data.forEach(suggestion => {
        console.log(`Section: ${suggestion.section}`);
        console.log(`Title: ${suggestion.title}`);
        console.log(`Description: ${suggestion.description}`);
        console.log(`Impact Score: ${suggestion.impactScore}/100`);
        console.log(`Confidence: ${suggestion.confidence}/100`);
        console.log('---');
      });
    }
  } catch (error) {
    console.error('Failed to generate suggestions:', error);
  }
};

// 应用AI建议
const applySuggestion = async (suggestionId: string) => {
  try {
    const response = await profileService.applyAISuggestion({
      suggestionId,
      customizations: {
        // 可选的自定义修改
        tone: 'more_confident',
        length: 'shorter'
      }
    });

    if (response.success) {
      console.log('Suggestion applied successfully:', response.data);
    }
  } catch (error) {
    console.error('Failed to apply suggestion:', error);
  }
};
```

### 4. 资料完整度分析

```typescript
import { profileService } from '../services';

const analyzeCompleteness = async () => {
  try {
    const response = await profileService.getProfileCompleteness();
    if (response.success && response.data) {
      const { overall, sections, missingFields } = response.data;
      
      console.log(`Overall completeness: ${overall}%`);
      
      // 显示各部分完成状态
      Object.entries(sections).forEach(([sectionId, sectionInfo]) => {
        console.log(`${sectionId}: ${sectionInfo.completed ? '✅' : '❌'} (Weight: ${sectionInfo.weight})`);
        if (sectionInfo.suggestions?.length) {
          console.log(`  Suggestions: ${sectionInfo.suggestions.join(', ')}`);
        }
      });
      
      // 显示缺失的重要字段
      if (missingFields.length > 0) {
        console.log('\nMissing important fields:');
        missingFields.forEach(field => {
          console.log(`- ${field.field} (${field.importance}): ${field.suggestion}`);
        });
      }
    }
  } catch (error) {
    console.error('Failed to analyze completeness:', error);
  }
};
```

### 5. 高级照片上传

```typescript
import { profileService } from '../services';
import type { PhotoUploadRequest } from '../types/api';

const uploadProfilePhoto = async (file: File) => {
  try {
    const request: PhotoUploadRequest = {
      file,
      type: 'profile',
      quality: 'high',
      autoEnhance: true,
      cropData: {
        x: 10,
        y: 10,
        width: 200,
        height: 200,
        rotate: 0
      }
    };

    const response = await profileService.uploadPhoto(request, (progress) => {
      console.log(`Upload progress: ${progress}%`);
    });

    if (response.success && response.data) {
      console.log('Photo uploaded successfully:', response.data.url);
      console.log('Thumbnails:', response.data.thumbnails);
      console.log('AI Analysis:', response.data.analysis);
      
      // 显示AI分析结果
      const analysis = response.data.analysis;
      console.log(`Photo Quality Score: ${analysis.quality}/100`);
      console.log(`Professional Score: ${analysis.professionalScore}/100`);
      console.log(`Face Detected: ${analysis.faceDetected ? 'Yes' : 'No'}`);
      
      if (analysis.suggestions?.length) {
        console.log('Improvement suggestions:');
        analysis.suggestions.forEach(suggestion => {
          console.log(`- ${suggestion}`);
        });
      }
    }
  } catch (error) {
    console.error('Photo upload failed:', error);
  }
};
```

## 高级功能

### 1. AI内容增强

```typescript
import { profileAIService } from '../services';

const enhanceContent = async (section: string, content: any) => {
  try {
    const response = await profileAIService.enhanceContent(
      section as any,
      content,
      'professionalism' // 或 'clarity', 'engagement', 'completeness', 'conciseness'
    );

    if (response.success && response.data) {
      console.log('Original:', response.data.original);
      console.log('Enhanced:', response.data.enhanced);
      console.log('Improvements:');
      
      response.data.improvements.forEach(improvement => {
        console.log(`- ${improvement.type}: ${improvement.description} (Impact: ${improvement.impact}/10)`);
      });
      
      console.log(`Confidence: ${response.data.confidence}/100`);
    }
  } catch (error) {
    console.error('Content enhancement failed:', error);
  }
};
```

### 2. 内容质量分析

```typescript
import { profileAIService } from '../services';

const analyzeContentQuality = async (section: string, content: any) => {
  try {
    const response = await profileAIService.analyzeContentQuality(section as any, content);
    
    if (response.success && response.data) {
      const { overallScore, dimensions, suggestions, strengths, weaknesses } = response.data;
      
      console.log(`Overall Quality Score: ${overallScore}/100`);
      console.log('Dimensions:');
      console.log(`- Clarity: ${dimensions.clarity}/100`);
      console.log(`- Professionalism: ${dimensions.professionalism}/100`);
      console.log(`- Completeness: ${dimensions.completeness}/100`);
      console.log(`- Engagement: ${dimensions.engagement}/100`);
      console.log(`- Uniqueness: ${dimensions.uniqueness}/100`);
      
      if (strengths.length > 0) {
        console.log('Strengths:', strengths);
      }
      
      if (weaknesses.length > 0) {
        console.log('Weaknesses:', weaknesses);
      }
      
      if (suggestions.length > 0) {
        console.log('Suggestions:', suggestions);
      }
    }
  } catch (error) {
    console.error('Quality analysis failed:', error);
  }
};
```

### 3. 大学验证增强功能

```typescript
import { universityService } from '../services';
import type { UniversityVerificationRequest } from '../types/api';

const enhancedUniversityVerification = async () => {
  try {
    // 1. 验证邮箱域名
    const domainValidation = await universityService.validateUniversityDomain(
      'student@tsinghua.edu.cn',
      'Tsinghua University'
    );
    
    console.log('Domain validation:', domainValidation);
    console.log(`Is valid: ${domainValidation.isValid}`);
    console.log(`Confidence: ${domainValidation.confidence}/100`);
    
    if (!domainValidation.isValid) {
      console.log('Suggestions:', domainValidation.suggestions);
      return;
    }

    // 2. 发起增强验证
    const verificationRequest: UniversityVerificationRequest = {
      universityName: 'Tsinghua University',
      email: 'student@tsinghua.edu.cn',
      studentId: '2021012345',
      graduationYear: 2025,
      degree: 'Bachelor',
      major: 'Computer Science'
    };

    const verificationResponse = await universityService.requestEnhancedVerification(verificationRequest);
    
    if (verificationResponse.success && verificationResponse.data) {
      console.log('Verification ID:', verificationResponse.data.verificationId);
      console.log('Status:', verificationResponse.data.status);
      console.log('Next steps:');
      
      verificationResponse.data.nextSteps.forEach(step => {
        console.log(`- ${step.action}: ${step.description} ${step.required ? '(Required)' : '(Optional)'}`);
        if (step.deadline) {
          console.log(`  Deadline: ${step.deadline}`);
        }
      });
    }

    // 3. 查看验证福利
    const benefitsResponse = await universityService.getVerificationBenefits('university_123');
    
    if (benefitsResponse.success && benefitsResponse.data) {
      console.log('Available benefits:');
      benefitsResponse.data.benefits.forEach(benefit => {
        console.log(`- ${benefit.title} (${benefit.type}): ${benefit.description}`);
        console.log(`  Active: ${benefit.active}, Value: ${benefit.value || 'N/A'}`);
      });

      const eligibility = benefitsResponse.data.eligibility;
      console.log(`Eligibility status: ${eligibility.currentStatus}`);
      if (eligibility.missingRequirements.length > 0) {
        console.log('Missing requirements:', eligibility.missingRequirements);
      }
    }
  } catch (error) {
    console.error('University verification failed:', error);
  }
};
```

### 4. 个人简介生成

```typescript
import { profileService } from '../services';

const generateBio = async () => {
  try {
    const response = await profileService.generateBio({
      style: 'professional', // 'casual', 'academic', 'creative'
      length: 'medium',       // 'short', 'long'
      includeSkills: true,
      includeGoals: true,
      includeExperience: true
    });

    if (response.success && response.data) {
      console.log('Generated bio:', response.data.generated);
      
      if (response.data.original) {
        console.log('Original bio:', response.data.original);
      }
      
      console.log('Alternative versions:');
      response.data.alternatives.forEach((alt, index) => {
        console.log(`${index + 1}. ${alt}`);
      });
      
      console.log('AI reasoning:');
      response.data.reasoning.forEach(reason => {
        console.log(`- ${reason}`);
      });
    }
  } catch (error) {
    console.error('Bio generation failed:', error);
  }
};
```

## React Hook集成

### 使用自定义Hook管理资料编辑

```typescript
import React from 'react';
import { useProfileEditor } from '../hooks/useProfileEditor';
import type { UserProfile } from '../types/api';

interface ProfileEditorProps {
  initialProfile: UserProfile;
}

function ProfileEditor({ initialProfile }: ProfileEditorProps) {
  const {
    profile,
    editingSections,
    aiSuggestions,
    completeness,
    isLoading,
    isSaving,
    startEditing,
    cancelEditing,
    updateEditingData,
    saveEditing,
    saveAllEditing,
    generateAISuggestions,
    applyAISuggestion,
    isEditing,
    getEditingData,
    getSectionSuggestions,
    hasUnsavedChanges
  } = useProfileEditor({
    initialProfile,
    onProfileUpdate: (updatedProfile) => {
      console.log('Profile updated:', updatedProfile);
    },
    onError: (error, action) => {
      console.error(`Error during ${action}:`, error);
    },
    autoSave: true,
    autoSaveDelay: 3000
  });

  const handleEditSkills = async () => {
    if (isEditing('skills')) {
      // 保存编辑
      const success = await saveEditing('skills');
      if (success) {
        console.log('Skills saved successfully');
      }
    } else {
      // 开始编辑
      startEditing('skills');
    }
  };

  const handleUpdateSkills = (newSkills: string[]) => {
    updateEditingData('skills', newSkills);
  };

  const handleGenerateSuggestions = async () => {
    await generateAISuggestions(['skills', 'projects', 'goals']);
  };

  const handleApplySuggestion = async (suggestionId: string) => {
    await applyAISuggestion(suggestionId);
  };

  return (
    <div className="profile-editor">
      {/* 完整度显示 */}
      {completeness && (
        <div className="completeness-bar">
          <div className="progress" style={{ width: `${completeness.overall}%` }} />
          <span>{completeness.overall}% Complete</span>
        </div>
      )}

      {/* 技能编辑区域 */}
      <div className="skills-section">
        <h3>Skills</h3>
        <button onClick={handleEditSkills} disabled={isSaving}>
          {isEditing('skills') ? 'Save Skills' : 'Edit Skills'}
        </button>
        
        {isEditing('skills') && (
          <div className="editing-area">
            <input
              type="text"
              placeholder="Add a skill"
              onChange={(e) => {
                const currentSkills = getEditingData('skills') || [];
                if (e.target.value && e.key === 'Enter') {
                  handleUpdateSkills([...currentSkills, e.target.value]);
                  e.target.value = '';
                }
              }}
            />
            <button onClick={() => cancelEditing('skills')}>
              Cancel
            </button>
          </div>
        )}

        {/* AI建议显示 */}
        {getSectionSuggestions('skills').map(suggestion => (
          <div key={suggestion.id} className="ai-suggestion">
            <h4>{suggestion.title}</h4>
            <p>{suggestion.description}</p>
            <p>Impact: {suggestion.impactScore}/100</p>
            <button onClick={() => handleApplySuggestion(suggestion.id)}>
              Apply Suggestion
            </button>
          </div>
        ))}
      </div>

      {/* 控制按钮 */}
      <div className="controls">
        <button onClick={handleGenerateSuggestions} disabled={isLoading}>
          {isLoading ? 'Generating...' : 'Get AI Suggestions'}
        </button>
        
        <button onClick={saveAllEditing} disabled={!hasUnsavedChanges() || isSaving}>
          {isSaving ? 'Saving...' : 'Save All Changes'}
        </button>
      </div>
    </div>
  );
}
```

## 错误处理最佳实践

### 1. 统一错误处理

```typescript
import { ApiError } from '../services/httpClient';

const handleProfileOperation = async (operation: () => Promise<any>) => {
  try {
    const result = await operation();
    return { success: true, data: result };
  } catch (error) {
    console.error('Profile operation failed:', error);
    
    if (error instanceof ApiError) {
      // API错误
      return { 
        success: false, 
        error: error.message,
        type: 'api_error' 
      };
    } else if (error instanceof Error) {
      // 一般错误
      return { 
        success: false, 
        error: error.message,
        type: 'general_error' 
      };
    } else {
      // 未知错误
      return { 
        success: false, 
        error: 'An unknown error occurred',
        type: 'unknown_error' 
      };
    }
  }
};

// 使用示例
const updateSkillsWithErrorHandling = async (skills: string[]) => {
  const result = await handleProfileOperation(async () => {
    return await profileService.updateProfileSection({
      section: 'skills',
      data: { skills }
    });
  });

  if (result.success) {
    console.log('Skills updated:', result.data);
  } else {
    console.error(`Error (${result.type}):`, result.error);
    // 显示用户友好的错误消息
    showErrorMessage(result.error);
  }
};
```

### 2. 网络状态处理

```typescript
// 检查网络状态并相应处理
const handleOfflineScenarios = () => {
  const isOnline = navigator.onLine;
  
  if (!isOnline) {
    console.log('Offline mode - changes will be saved locally');
    // 显示离线提示
    showOfflineNotification();
  }

  // 监听网络状态变化
  window.addEventListener('online', async () => {
    console.log('Back online - syncing changes');
    await syncOfflineChanges();
  });

  window.addEventListener('offline', () => {
    console.log('Gone offline - enabling local mode');
    enableOfflineMode();
  });
};
```

## 性能优化建议

1. **批量操作**: 使用批量更新API减少网络请求
2. **智能缓存**: 缓存完整度分析和AI建议结果
3. **延迟加载**: 按需加载AI功能和统计数据
4. **本地优化**: 提供本地验证和计算作为备用方案

这个API系统为个人资料管理提供了完整的解决方案，包括智能编辑、AI润色、验证和分析等功能，支持离线使用和错误恢复。 