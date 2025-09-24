import { useState } from 'react';
import { ArrowLeft, MapPin, Calendar, Users, Target, ExternalLink, Star, Heart } from 'lucide-react';
import { ImageWithFallback } from '../figma/ImageWithFallback';
import { Badge } from '../ui/badge';
import svgPaths from "../../imports/svg-fko3i96u3r";

interface UserProfilePageProps {
  onBack: () => void;
  user: {
    id: number;
    name: string;
    age: number;
    gender: string;
    role: string;
    distance: number;
    avatar: string;
    tags: string[];
    bio?: string;
    projects?: Array<{
      id: number;
      title: string;
      description: string;
      status: 'ongoing' | 'finished' | 'not_started';
      tags: string[];
      collaborators: number;
    }>;
  };
}

export function UserProfilePage({ onBack, user }: UserProfilePageProps) {
  const [activeTab, setActiveTab] = useState<'about' | 'projects'>('about');

  // 项目状态tag颜色映射
  const statusColorMap = {
    'not_started': 'bg-gray-300 text-gray-800',
    'ongoing': 'bg-[#0055F7] text-white',
    'finished': 'bg-green-500 text-white',
  };

  return (
    <div className="h-[632px] flex flex-col relative bg-white">
      {/* Header */}
      <div className="h-[90px] flex items-center justify-between px-4 border-b border-[#E8EDF2] bg-[#FAFAFA]">
        <button onClick={onBack} className="p-2">
          <ArrowLeft size={24} className="text-blue-600" />
        </button>
        <h1 className="font-semibold text-lg">个人资料</h1>
        <div className="w-10" />
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="space-y-6 p-6">
          {/* User Info Card */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-start gap-4">
              <div className="relative">
                <ImageWithFallback
                  src={user.avatar}
                  alt={user.name}
                  className="w-20 h-20 rounded-full object-cover"
                />
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-white"></div>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h2 className="text-2xl font-bold">{user.name}</h2>
                  {user.gender !== 'Non-binary' && (
                    <span className="ml-1">
                      <svg className="inline w-5 h-5" fill="none" viewBox="0 0 24 24">
                        <path 
                          d={user.gender === 'Male' ? svgPaths.male : svgPaths.female} 
                          stroke="black" 
                          strokeWidth="2" 
                          strokeLinecap="round" 
                          strokeLinejoin="round"
                        />
                      </svg>
                    </span>
                  )}
                  <span className="text-gray-600">, {user.age}</span>
                </div>
                <p className="text-gray-600 mb-2">{user.role}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                  <div className="flex items-center gap-1">
                    <MapPin size={14} />
                    <span>{user.distance} km 距离</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {user.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('about')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'about'
                  ? 'border-[#0055F7] text-[#0055F7]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              关于
            </button>
            <button
              onClick={() => setActiveTab('projects')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'projects'
                  ? 'border-[#0055F7] text-[#0055F7]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              项目 ({user.projects?.length || 0})
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'about' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">个人简介</h3>
                <p className="text-gray-700 leading-relaxed">
                  {user.bio || '这个人很懒，什么都没有留下...'}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="space-y-4">
              {user.projects && user.projects.length > 0 ? (
                user.projects.map((project) => (
                  <div key={project.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-lg">{project.title}</h4>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${statusColorMap[project.status]}`}>
                        {project.status === 'not_started' ? '未开始' : 
                         project.status === 'ongoing' ? '进行中' : '已完成'}
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{project.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex flex-wrap gap-1">
                        {project.tags.slice(0, 3).map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {project.tags.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{project.tags.length - 3}
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-1 text-sm text-gray-500">
                        <Users size={14} />
                        <span>{project.collaborators}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4">
                    <svg className="block size-full" fill="none" viewBox="0 0 24 24">
                      <path d={svgPaths.like} fill="#9ca3af" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-700 mb-2">暂无项目</h3>
                  <p className="text-gray-500">该用户还没有发布任何项目</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
