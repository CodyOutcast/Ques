{
    id: 10001, // 确保唯一
    title: "拯救世界",
    author: "Cody",
    collaborators: 3, // 与下方 collaboratorsList 长度保持一致
    // cardStyle 可选: 'image' | 'video' | 'text-only'
    cardStyle: 'image',
    // 如果是 image 卡片，提供背景图（建议竖图）：
    background: "/sample/cody.jpg",
    // 如果是 video 卡片，提供视频链接（放 public 后用绝对路径）：
    // videoUrl: "/sample/intro.mp4",
  
    description: "打造一个革命性的项目合作伙伴匹配平台",
    tags: ["AI", "Start Up", "App"],
  
    type: 'project',
    status: 'ongoing', // 'ongoing' | 'finished' | 'not_started'
    gradientBackground: 'bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700', // text-only 或 video 时作为底色
  
    owner: {
      name: "Cody",
      age: 20,
      gender: "Male", // 'Male' | 'Female' | 'Non-binary'
      role: "CEO",
      distance: 0, // km
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=sample", // 或放 public 里："/sample/avatar.png"
      tags: []
    },
  
    collaboratorsList: [
      { name: "William", role: "Backend", avatar: "" },
      { name: "Jimmy", role: "AI and algorithm", avatar: "" },
      { name: "Rhys", role: "UI and frontendd", avatar: "" }
    ],
  
    detailedDescription: "这里是项目的详细描述，适合放 2-4 段，导出时会展示到详情页。",
    startTime: "August 2025",
    currentProgress: 50, // 百分比
    content: "我们正在构建一个用于演示导出功能的完整样例，用于验证图片/视频/标签/作者信息等在卡片上的呈现效果。",
    purpose: "向团队或用户展示卡片导出的视觉质量与信息完整性。",
    lookingFor: ["you"],
  
    links: [
      "https://github.com/your-repo",
      "https://figma.com/your-design"
    ],
  
    // 媒体轮播，可混合图片/视频。会在详情页顶部轮播显示
    // 如果提供了 background，也可以一并放在 media 里以便轮播
    media: [
      "/sample/hero.jpg",
      // "/sample/intro.mp4"
    ]
  }