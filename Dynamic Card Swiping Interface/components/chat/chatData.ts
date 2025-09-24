// 聊天数据管理模块
interface Message {
  id: number;
  text: string;
  time: string;
  isOwn: boolean;
  isNew?: boolean;
  status?: 'sending' | 'sent' | 'read' | 'failed';
}

interface UserProfile {
  id: number;
  name: string;
  age: number;
  gender: 'Male' | 'Female' | 'Non-binary';
  role: string;
  distance: number;
  avatar: string;
  tags: string[];
  bio: string;
  projectTitle: string;
  projectDescription: string;
  isOnline: boolean;
  lastSeen?: string;
  // 个人主页数据
  profileData: {
    birthday: string;
    location: string;
    fullBio: string;
    objective: string;
    lookingFor: string;
    typeTags: string[];
    skills: string[];
    media: string[];
    initiatedProjects: any[];
    collaboratedProjects: any[];
  };
}

interface ChatData {
  chatId: number;
  user: UserProfile;
  messages: Message[];
  isNewMatch: boolean;
}

// 用户数据
const userProfiles: { [key: number]: UserProfile } = {
  1: {
    id: 1,
    name: "Jessica Parker",
    age: 28,
    gender: "Female",
    role: "UI/UX Designer",
    distance: 2.3,
    avatar: "https://images.unsplash.com/photo-1652471949169-9c587e8898cd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3b21hbiUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNzQ5Mnww&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["UI/UX", "Design Systems", "Prototyping", "Figma"],
    bio: "Passionate about creating user-centered designs that solve real problems. I love working on innovative projects that make a positive impact.",
    projectTitle: "AI-Powered Design Assistant",
    projectDescription: "Building an intelligent design tool that helps designers create better user experiences through AI-driven insights and automated design suggestions.",
    isOnline: true,
    profileData: {
      birthday: "1996-03-15",
      location: "San Francisco, CA",
      fullBio: "👋 Hi, I'm Jessica, a passionate UI/UX designer with 6+ years of experience creating intuitive digital experiences.\n\nI specialize in user research, design systems, and prototyping. I've worked with startups and Fortune 500 companies to design products that millions of people use daily.\n\nI believe great design happens when we deeply understand our users and their needs.",
      objective: "To collaborate with innovative teams building products that make a meaningful impact on people's lives.\n\nI'm particularly interested in AI-powered tools, healthcare technology, and sustainable design solutions.",
      lookingFor: "Exciting projects where I can contribute my design expertise while learning from talented developers and product managers.",
      typeTags: ["Seeking Collaborators", "Design Lead", "UX Researcher"],
      skills: ["UI/UX Design", "Design Systems", "Figma", "User Research", "Prototyping", "Accessibility"],
      media: [
        "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop"
      ],
      initiatedProjects: [
        {
          id: 101,
          title: "AI-Powered Design Assistant",
          description: "Building an intelligent design tool that helps designers create better user experiences through AI-driven insights and automated design suggestions.",
          status: "进行中",
          progress: 65,
          image: "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=400&h=200&fit=crop",
          tags: ["AI", "Design", "UX"],
          startDate: "2024年9月",
          createdAt: Date.now() - 1000 * 60 * 60 * 24 * 45
        },
        {
          id: 102,
          title: "Design System Library",
          description: "Comprehensive design system for consistent user interfaces across multiple platforms",
          status: "已完成",
          progress: 100,
          image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop",
          tags: ["Design Systems", "UI", "Components"],
          startDate: "2024年6月",
          createdAt: Date.now() - 1000 * 60 * 60 * 24 * 90
        }
      ],
      collaboratedProjects: [
        {
          id: 103,
          title: "HealthTech Mobile App",
          description: "Designed user experience for a comprehensive health monitoring application",
          status: "已完成",
          progress: 100,
          image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=200&fit=crop",
          tags: ["Health", "Mobile", "UX"],
          startDate: "2024年1月",
          role: "Lead Designer"
        }
      ]
    }
  },
  2: {
    id: 2,
    name: "Mark Stevens",
    age: 32,
    gender: "Male",
    role: "Full Stack Developer",
    distance: 5.1,
    avatar: "https://images.unsplash.com/photo-1672685667592-0392f458f46f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtYW4lMjBwcm9mZXNzaW9uYWwlMjBwb3J0cmFpdHxlbnwxfHx8fDE3NTYxOTcwMzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["React", "Node.js", "Python", "AWS"],
    bio: "Experienced developer who loves building scalable web applications. Always excited to work on projects that push technological boundaries.",
    projectTitle: "Sustainable Supply Chain Platform",
    projectDescription: "Developing a blockchain-based platform to track and verify sustainable practices across global supply chains.",
    isOnline: false,
    lastSeen: "2 hours ago",
    profileData: {
      birthday: "1992-07-22",
      location: "Seattle, WA",
      fullBio: "👨‍💻 Full-stack developer with 8+ years of experience building scalable web applications and cloud infrastructure.\n\nI'm passionate about clean code, sustainable technology, and creating solutions that make a positive environmental impact. I've led development teams at several startups and have experience with everything from frontend React to backend microservices.",
      objective: "To work on meaningful projects that combine cutting-edge technology with environmental sustainability.\n\nI'm particularly interested in blockchain applications, carbon tracking systems, and green tech innovations.",
      lookingFor: "Collaborative teams focused on sustainability and social impact where I can contribute my technical leadership skills.",
      typeTags: ["Tech Lead", "Sustainability Advocate", "Open Source"],
      skills: ["React", "Node.js", "Python", "AWS", "Blockchain", "Docker", "PostgreSQL", "GraphQL"],
      media: [
        "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=300&fit=crop"
      ],
      initiatedProjects: [
        {
          id: 201,
          title: "Sustainable Supply Chain Platform",
          description: "Developing a blockchain-based platform to track and verify sustainable practices across global supply chains.",
          status: "进行中",
          progress: 78,
          image: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=200&fit=crop",
          tags: ["Blockchain", "Sustainability", "Supply Chain"],
          startDate: "2024年6月",
          createdAt: Date.now() - 1000 * 60 * 60 * 24 * 60
        }
      ],
      collaboratedProjects: [
        {
          id: 202,
          title: "Carbon Footprint Tracker",
          description: "Mobile app for tracking and reducing personal carbon emissions",
          status: "已完成",
          progress: 100,
          image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=200&fit=crop",
          tags: ["Mobile", "Environment", "React Native"],
          startDate: "2024年1月",
          role: "Backend Developer"
        }
      ]
    }
  },
  3: {
    id: 3,
    name: "Anna Miller",
    age: 26,
    gender: "Female",
    role: "Product Manager",
    distance: 1.8,
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEzMDI5M3ww&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["Product Strategy", "Data Analysis", "User Research", "Agile"],
    bio: "Strategic thinker with a passion for bringing innovative products to market. I excel at bridging the gap between technical teams and business goals.",
    projectTitle: "HealthTech Mobile App",
    projectDescription: "Creating a comprehensive health monitoring app that uses AI to provide personalized wellness insights and connect users with healthcare professionals.",
    isOnline: true,
    profileData: {
      birthday: "1998-11-03",
      location: "Austin, TX",
      fullBio: "🚀 Product Manager with 4+ years of experience launching successful digital health products.\n\nI specialize in user research, data-driven decision making, and cross-functional team leadership. I've helped launch 3 healthcare apps that serve over 100K users.",
      objective: "To build health technology products that genuinely improve people's quality of life and make healthcare more accessible.",
      lookingFor: "Innovative healthcare projects where I can apply my product strategy skills to create meaningful user experiences.",
      typeTags: ["Product Lead", "Healthcare Tech", "Data-Driven"],
      skills: ["Product Strategy", "User Research", "Data Analysis", "Agile", "Healthcare", "Mobile Apps"],
      media: ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop"],
      initiatedProjects: [{
        id: 301,
        title: "HealthTech Mobile App",
        description: "Creating a comprehensive health monitoring app that uses AI to provide personalized wellness insights and connect users with healthcare professionals.",
        status: "进行中",
        progress: 85,
        image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=200&fit=crop",
        tags: ["Health", "AI", "Mobile"],
        startDate: "2024年8月",
        createdAt: Date.now() - 1000 * 60 * 60 * 24 * 30
      }],
      collaboratedProjects: []
    }
  },
  4: {
    id: 4,
    name: "Tom Anderson",
    age: 35,
    gender: "Male",
    role: "Data Scientist",
    distance: 3.7,
    avatar: "https://images.unsplash.com/photo-1739298061757-7a3339cee982?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEwNjAzMXww&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["Machine Learning", "Python", "TensorFlow", "Statistics"],
    bio: "Data scientist with expertise in machine learning and AI. I'm passionate about using data to solve complex problems and drive business value.",
    projectTitle: "Predictive Analytics Platform",
    projectDescription: "Building an advanced analytics platform that helps businesses make data-driven decisions through predictive modeling and real-time insights.",
    isOnline: false,
    lastSeen: "1 day ago",
    profileData: {
      birthday: "1989-04-18",
      location: "Boston, MA",
      fullBio: "📊 Senior Data Scientist with 10+ years of experience in machine learning, predictive analytics, and big data systems.\n\nI specialize in transforming complex datasets into business intelligence and building scalable ML pipelines.",
      objective: "To leverage data science and machine learning to solve complex business problems and drive innovation in various industries.",
      lookingFor: "Data-focused projects where I can apply advanced analytics to create meaningful business impact.",
      typeTags: ["Data Expert", "ML Engineer", "Analytics Lead"],
      skills: ["Machine Learning", "Python", "TensorFlow", "Statistics", "SQL", "Apache Spark"],
      media: ["https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop"],
      initiatedProjects: [{
        id: 401,
        title: "Predictive Analytics Platform",
        description: "Building an advanced analytics platform that helps businesses make data-driven decisions through predictive modeling and real-time insights.",
        status: "进行中",
        progress: 72,
        image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop",
        tags: ["Machine Learning", "Analytics", "Business Intelligence"],
        startDate: "2024年7月",
        createdAt: Date.now() - 1000 * 60 * 60 * 24 * 50
      }],
      collaboratedProjects: []
    }
  },
  5: {
    id: 5,
    name: "Sarah Johnson",
    age: 29,
    gender: "Female",
    role: "Creative Director",
    distance: 2.5,
    avatar: "https://images.unsplash.com/photo-1652471949169-9c587e8898cd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3b21hbiUyMHByb2Zlc3Npb25hbCUyMGhlYWRzaG90fGVufDF8fHx8MTc1NjEwNzQ5Mnww&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["Creative Strategy", "Brand Design", "Art Direction", "Adobe Creative Suite"],
    bio: "Creative director with a passion for innovative design and storytelling. I love creating compelling brand experiences that resonate with audiences.",
    projectTitle: "AI Creative Platform",
    projectDescription: "Developing a revolutionary creative platform that combines AI technology with human creativity to help artists and designers create stunning visual content.",
    isOnline: true,
    profileData: {
      birthday: "1995-08-22",
      location: "Los Angeles, CA",
      fullBio: "🎨 Creative Director with 7+ years of experience in brand design, art direction, and visual storytelling.\n\nI specialize in creating compelling brand experiences that connect with audiences on an emotional level. My work has been featured in major design publications.",
      objective: "To push the boundaries of creative technology and help artists worldwide unlock their full creative potential.",
      lookingFor: "Innovative creative projects that combine technology with artistic expression.",
      typeTags: ["Creative Lead", "Art Director", "Brand Strategist"],
      skills: ["Creative Strategy", "Brand Design", "Art Direction", "Adobe Creative Suite", "UI/UX", "Photography"],
      media: ["https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=400&h=300&fit=crop"],
      initiatedProjects: [{
        id: 501,
        title: "AI Creative Platform",
        description: "Developing a revolutionary creative platform that combines AI technology with human creativity to help artists and designers create stunning visual content.",
        status: "进行中",
        progress: 68,
        image: "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=400&h=200&fit=crop",
        tags: ["AI", "Creative", "Design"],
        startDate: "2024年5月",
        createdAt: Date.now() - 1000 * 60 * 60 * 24 * 80
      }],
      collaboratedProjects: []
    }
  },
  6: {
    id: 6,
    name: "Michael Chen",
    age: 31,
    gender: "Male",
    role: "VR Developer",
    distance: 4.2,
    avatar: "https://images.unsplash.com/photo-1672685667592-0392f458f46f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtYW4lMjBwcm9mZXNzaW9uYWwlMjBwb3J0cmFpdHxlbnwxfHx8fDE3NTYxOTcwMzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["Unity", "Unreal Engine", "3D Modeling", "AR/VR"],
    bio: "VR developer passionate about creating immersive experiences. I specialize in educational and training applications that leverage the power of virtual reality.",
    projectTitle: "VR Education App",
    projectDescription: "Creating immersive virtual reality educational experiences that make learning more engaging and effective for students of all ages.",
    isOnline: true,
    profileData: {
      birthday: "1993-12-05",
      location: "Vancouver, Canada",
      fullBio: "🥽 VR Developer specializing in immersive educational experiences and 3D interactive environments.\n\nI've created VR applications for major educational institutions and tech companies, focusing on making learning more engaging through virtual reality.",
      objective: "To revolutionize education through immersive virtual reality technologies that make complex concepts accessible and engaging.",
      lookingFor: "Educational VR projects that can make a real impact on learning outcomes and student engagement.",
      typeTags: ["VR Developer", "Education Tech", "3D Specialist"],
      skills: ["Unity", "Unreal Engine", "3D Modeling", "AR/VR", "C#", "Educational Design"],
      media: ["https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=400&h=300&fit=crop"],
      initiatedProjects: [{
        id: 601,
        title: "VR Education App",
        description: "Creating immersive virtual reality educational experiences that make learning more engaging and effective for students of all ages.",
        status: "进行中",
        progress: 55,
        image: "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=400&h=200&fit=crop",
        tags: ["VR", "Education", "3D"],
        startDate: "2024年4月",
        createdAt: Date.now() - 1000 * 60 * 60 * 24 * 100
      }],
      collaboratedProjects: []
    }
  },
  7: {
    id: 7,
    name: "Emily Davis",
    age: 27,
    gender: "Female",
    role: "Blockchain Developer",
    distance: 3.1,
    avatar: "https://images.unsplash.com/photo-1563132337-f159f484226c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHByb2Zlc3Npb25hbCUyMHdvbWFufGVufDF8fHx8MTc1NjEwMDY1MXww&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["Blockchain", "Smart Contracts", "Solidity", "DeFi"],
    bio: "Blockchain developer focused on building decentralized solutions that empower users and create new economic opportunities. Passionate about the future of Web3.",
    projectTitle: "Blockchain Solution",
    projectDescription: "Building innovative blockchain solutions that solve real-world problems while ensuring security, scalability, and user-friendly experiences.",
    isOnline: false,
    lastSeen: "3 hours ago",
    profileData: {
      birthday: "1997-06-14",
      location: "Berlin, Germany",
      fullBio: "⛓️ Blockchain Developer passionate about building decentralized solutions that empower users and create new economic opportunities.\n\nI specialize in smart contract development, DeFi protocols, and Web3 applications. My work focuses on making blockchain technology more accessible and user-friendly.",
      objective: "To build the future of decentralized finance and help create a more equitable and transparent financial system through blockchain technology.",
      lookingFor: "Innovative blockchain projects that can solve real-world problems and make a positive impact on society.",
      typeTags: ["Blockchain Developer", "DeFi Expert", "Smart Contract Specialist"],
      skills: ["Blockchain", "Smart Contracts", "Solidity", "DeFi", "Web3", "Ethereum"],
      media: ["https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=300&fit=crop"],
      initiatedProjects: [{
        id: 701,
        title: "Blockchain Solution",
        description: "Building innovative blockchain solutions that solve real-world problems while ensuring security, scalability, and user-friendly experiences.",
        status: "进行中",
        progress: 62,
        image: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=200&fit=crop",
        tags: ["Blockchain", "DeFi", "Smart Contracts"],
        startDate: "2024年3月",
        createdAt: Date.now() - 1000 * 60 * 60 * 24 * 120
      }],
      collaboratedProjects: []
    }
  },
  8: {
    id: 8,
    name: "David Wilson",
    age: 33,
    gender: "Male",
    role: "IoT Engineer",
    distance: 6.8,
    avatar: "https://images.unsplash.com/photo-1601489865452-407a1b801dde?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBtYW4lMjBzdWl0fGVufDF8fHx8MTc1NjE5Nzc1Mnww&ixlib=rb-4.1.0&q=80&w=1080",
    tags: ["IoT", "Arduino", "Raspberry Pi", "Embedded Systems"],
    bio: "IoT engineer with expertise in creating smart connected devices. I enjoy working on projects that merge hardware and software to create innovative solutions.",
    projectTitle: "Smart IoT Hub",
    projectDescription: "Developing an intelligent IoT hub that seamlessly connects and manages smart home devices while ensuring privacy and security.",
    isOnline: true,
    profileData: {
      birthday: "1991-09-28",
      location: "Singapore",
      fullBio: "🔧 IoT Engineer with expertise in creating smart connected devices and systems that bridge the physical and digital worlds.\n\nI enjoy working on projects that merge hardware and software to create innovative solutions that improve people's daily lives through intelligent automation.",
      objective: "To create intelligent IoT ecosystems that enhance quality of life while prioritizing user privacy and security.",
      lookingFor: "Smart technology projects that combine hardware innovation with software intelligence to solve real-world problems.",
      typeTags: ["IoT Engineer", "Hardware Specialist", "Smart Home Expert"],
      skills: ["IoT", "Arduino", "Raspberry Pi", "Embedded Systems", "C++", "Python", "Edge Computing"],
      media: ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"],
      initiatedProjects: [{
        id: 801,
        title: "Smart IoT Hub",
        description: "Developing an intelligent IoT hub that seamlessly connects and manages smart home devices while ensuring privacy and security.",
        status: "进行中",
        progress: 88,
        image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=200&fit=crop",
        tags: ["IoT", "Smart Home", "Security"],
        startDate: "2024年2月",
        createdAt: Date.now() - 1000 * 60 * 60 * 24 * 150
      }],
      collaboratedProjects: []
    }
  }
};

// 聊天消息数据
const chatMessages: { [key: number]: Message[] } = {
  1: [
    {
      id: 1,
      text: "Hi! I saw your project about AI-powered design. That sounds fascinating! 🎨",
      time: "14:28",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Hello! Thank you! I'm really excited about it. We're trying to bridge the gap between AI and human creativity.",
      time: "14:30",
      isOwn: true,
      status: 'read'
    },
    {
      id: 3,
      text: "I'd love to learn more about how the AI suggestions work. Are you looking for collaborators?",
      time: "14:32",
      isOwn: false,
      status: 'read'
    },
    {
      id: 4,
      text: "Absolutely! We're looking for a UX designer to help shape the user experience. Would you be interested in discussing further?",
      time: "14:35",
      isOwn: true,
      status: 'read'
    },
    {
      id: 5,
      text: "Thanks for the update!",
      time: "14:36",
      isOwn: false,
      status: 'read'
    }
  ],
  2: [
    {
      id: 1,
      text: "Hey! Your supply chain project looks impressive. I've been working on similar sustainability initiatives.",
      time: "13:10",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Thanks! It's a complex challenge but very rewarding. What kind of sustainability work have you been doing?",
      time: "13:15",
      isOwn: true,
      status: 'read'
    },
    {
      id: 3,
      text: "I've been focusing on carbon footprint tracking in manufacturing. The blockchain approach is really smart for verification.",
      time: "13:18",
      isOwn: false,
      status: 'read'
    },
    {
      id: 4,
      text: "Let's schedule a meeting",
      time: "13:20",
      isOwn: true,
      status: 'read'
    }
  ],
  3: [
    {
      id: 1,
      text: "I'm really interested in your HealthTech app! Healthcare innovation is so important right now.",
      time: "12:40",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Thank you! We're trying to make healthcare more accessible and personalized. What's your background in this space?",
      time: "12:42",
      isOwn: true,
      status: 'read'
    },
    {
      id: 3,
      text: "I have experience in health data analytics and user research for medical applications. Would love to contribute!",
      time: "12:44",
      isOwn: false,
      status: 'read'
    },
    {
      id: 4,
      text: "Perfect! See you then",
      time: "12:45",
      isOwn: true,
      status: 'read'
    }
  ],
  4: [
    {
      id: 1,
      text: "Your predictive analytics platform sounds amazing! I'm always looking for better ways to leverage data insights.",
      time: "11:25",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Thanks! We're building something that can handle real-time data processing at scale. What kind of analytics work do you do?",
      time: "11:30",
      isOwn: true,
      status: 'read'
    },
    {
      id: 3,
      text: "Great work on the project",
      time: "11:35",
      isOwn: false,
      status: 'read'
    }
  ],
  5: [
    {
      id: 1,
      text: "Hey, I'm interested in your project! 😎",
      time: "10:28",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Hi Sarah! Thanks for reaching out. I'd love to hear your thoughts on combining AI with creative workflows.",
      time: "10:30",
      isOwn: true,
      status: 'read'
    },
    {
      id: 3,
      text: "I think AI can be a powerful creative partner when used thoughtfully. Are you looking for creative direction input?",
      time: "10:32",
      isOwn: false,
      status: 'read'
    }
  ],
  6: [
    {
      id: 1,
      text: "Your VR education project is exactly what the industry needs! I've been working on similar immersive experiences.",
      time: "16:15",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Thank you! Educational VR is such an exciting field. What kind of immersive experiences have you been creating?",
      time: "16:18",
      isOwn: true,
      status: 'read'
    }
  ],
  7: [
    {
      id: 1,
      text: "I'm fascinated by your blockchain solution! The decentralized approach is really innovative.",
      time: "09:45",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Thanks! We're trying to make blockchain technology more accessible while maintaining security. Are you working with blockchain?",
      time: "09:50",
      isOwn: true,
      status: 'read'
    }
  ],
  8: [
    {
      id: 1,
      text: "Your smart IoT hub concept is brilliant! I've been working on connected device security.",
      time: "08:20",
      isOwn: false,
      status: 'read'
    },
    {
      id: 2,
      text: "Security is such a crucial aspect of IoT! We'd love to collaborate on that front. What's your approach?",
      time: "08:25",
      isOwn: true,
      status: 'read'
    }
  ]
};

// 获取聊天数据
export function getChatData(chatId: number | null): ChatData | null {
  if (!chatId || !userProfiles[chatId]) {
    return null;
  }

  return {
    chatId,
    user: userProfiles[chatId],
    messages: chatMessages[chatId] || [],
    isNewMatch: [5, 6].includes(chatId) // Sarah Johnson 和 Michael Chen 是新匹配
  };
}

// 获取用户信息
export function getUserProfile(chatId: number | null): UserProfile | null {
  if (!chatId || !userProfiles[chatId]) {
    return null;
  }
  return userProfiles[chatId];
}

export type { Message, UserProfile, ChatData }; 