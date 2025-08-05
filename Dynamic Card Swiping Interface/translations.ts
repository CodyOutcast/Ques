// Translations for the app
export const translations = {
  en: {
    // App name
    appName: "Ques",
    
    // Navigation
    home: "Home",
    search: "Search",
    messages: "Messages",
    profile: "Profile",
    
    // Filter sidebar
    filters: "Filters",
    filterDescription: "Customize your search to find the perfect project collaborators",
    cardTypes: "Card Types",
    projects: "Projects",
    profiles: "Profiles",
    projectStatus: "Project Status",
    projectTypes: "Project Types",
    distance: "Distance (km)",
    ageRange: "Age Range",
    ongoing: "Ongoing",
    finished: "Finished",
    
    // Project details
    projectOwner: "Project Owner",
    about: "About",
    collaborators: "Collaborators",
    description: "Description",
    purpose: "Purpose",
    lookingFor: "Looking For",
    links: "Links",
    media: "Media",
    projectDetails: "Project Details",
    profileDetails: "Profile Details",
    whatWeAreBuilding: "What We're Building",
    goals: "Goals",
    
    // Common text
    by: "By",
    collaboratorsText: "collaborators",
    kmAway: "km away",
    complete: "complete",
    years: "years",
    
    // Actions
    close: "Close",
    back: "Back",
    next: "Next",
    save: "Save",
    cancel: "Cancel",
    
    // Status
    status: "Status",
    progress: "Progress",
    startTime: "Start Time",
    
    // Card content
    cardBy: "By",
    cardCollaborators: "collaborators",
  },
  
  zh: {
    // App name
    appName: "快索",
    
    // Navigation
    home: "首页",
    search: "搜索",
    messages: "消息",
    profile: "个人资料",
    
    // Filter sidebar
    filters: "筛选",
    filterDescription: "自定义搜索以找到完美的项目合作伙伴",
    cardTypes: "卡片类型",
    projects: "项目",
    profiles: "个人资料",
    projectStatus: "项目状态",
    projectTypes: "项目类型",
    distance: "距离 (公里)",
    ageRange: "年龄范围",
    ongoing: "进行中",
    finished: "已完成",
    
    // Project details
    projectOwner: "项目负责人",
    about: "关于",
    collaborators: "合作者",
    description: "描述",
    purpose: "目的",
    lookingFor: "正在寻找",
    links: "链接",
    media: "媒体",
    projectDetails: "项目详情",
    profileDetails: "个人资料详情",
    whatWeAreBuilding: "我们正在做的",
    goals: "目标",
    
    // Common text
    by: "发起人",
    collaboratorsText: "合作者",
    kmAway: "公里外",
    complete: "完成",
    years: "岁",
    
    // Actions
    close: "关闭",
    back: "返回",
    next: "下一步",
    save: "保存",
    cancel: "取消",
    
    // Status
    status: "状态",
    progress: "进度",
    startTime: "开始时间",
    
    // Card content
    cardBy: "发起人",
    cardCollaborators: "合作者",
  }
};

// Helper function to get translation
export const getTranslation = (key: string, language: 'en' | 'zh' = 'zh') => {
  const keys = key.split('.');
  let value: any = translations[language];
  
  for (const k of keys) {
    value = value?.[k];
    if (value === undefined) {
      console.warn(`Translation key "${key}" not found for language "${language}"`);
      return key; // Return the key as fallback
    }
  }
  
  return value;
};

// Current language (default to Chinese)
export let currentLanguage: 'en' | 'zh' = 'zh';

// Function to set language
export const setLanguage = (language: 'en' | 'zh') => {
  currentLanguage = language;
  // Update HTML lang attribute
  document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
};

// Function to get current translation
export const t = (key: string) => getTranslation(key, currentLanguage); 