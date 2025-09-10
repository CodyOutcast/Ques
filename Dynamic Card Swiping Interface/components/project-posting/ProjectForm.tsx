import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Slider } from '../ui/slider';
import { TagInput } from './TagInput';
import { CollaboratorInput } from './CollaboratorInput';
import { LinkInput } from './LinkInput';
import { ImageWithFallback } from '../figma/ImageWithFallback';
import { MediaUpload } from './MediaUpload';
import { currentLanguage as i18nCurrentLanguage, t } from '../../translations';
import { Calendar } from 'lucide-react';
import { useRef } from 'react';

interface ProjectData {
  title: string;
  shortDescription: string;
  media: File[];
  projectTags: string[];
  ownRole: string[];
  collaborators: Array<{
    id: string;
    name: string;
    role: string[];
  }>;
  startTime: string;
  currentProgress: number;
  detailedDescription: string;
  purpose: string;
  whatWeAreDoing: string;
  peopleLookingFor: string;
  lookingForTags: string[];
  links: string[];
}

interface ProjectFormProps {
  projectData: ProjectData;
  onProjectDataChange: (data: ProjectData) => void;
  onSubmit: () => void;
  isSubmitting: boolean;
}

export function ProjectForm({ projectData, onProjectDataChange, onSubmit, isSubmitting }: ProjectFormProps) {
  const [titleWordCount, setTitleWordCount] = useState(0);
  const nativeDateRef = useRef<HTMLInputElement | null>(null);

  const updateProjectData = (field: keyof ProjectData, value: any) => {
    onProjectDataChange({
      ...projectData,
      [field]: value,
    });
  };

  const handleTitleChange = (value: string) => {
    // Count words/characters for bilingual support
    const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0;
    const charCount = value.length;
    
    // Limit to 10 words or 20 characters
    if (wordCount <= 10 && charCount <= 20) {
      setTitleWordCount(wordCount);
      updateProjectData('title', value);
    }
  };

  const isFormValid = () => {
    return !!(projectData.title.trim() &&
           projectData.startTime &&
           projectData.detailedDescription.trim());
  };

  return (
    <div className="p-4 space-y-6 pb-24">
      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title" className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Project Title *' : '项目标题 *'}</Label>
        <Input
          id="title"
          value={projectData.title}
          onChange={(e) => handleTitleChange(e.target.value)}
          placeholder={i18nCurrentLanguage === 'en' ? 'Enter project title (up to 10 words or 20 characters)' : '请输入项目标题（最多10个英文单词或20个字符）'}
          className="w-full"
        />
        <p className="text-sm text-muted-foreground">
          {i18nCurrentLanguage === 'en' ? `${titleWordCount}/10 words, ${projectData.title.length}/20 chars` : `${titleWordCount}/10 单词，${projectData.title.length}/20 字符`}
        </p>
      </div>

      {/* Short Description */}
      <div className="space-y-2">
        <Label htmlFor="shortDescription" className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Short Description' : '项目简介'}</Label>
        <Textarea
          id="shortDescription"
          value={projectData.shortDescription}
          onChange={(e) => updateProjectData('shortDescription', e.target.value)}
          placeholder={i18nCurrentLanguage === 'en' ? 'Briefly describe your project in one or two sentences' : '用一两句话简要描述你的项目'}
          rows={3}
        />
      </div>

      {/* Collaborators */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Collaborators' : '协作者'}</CardTitle>
        </CardHeader>
        <CardContent>
          <CollaboratorInput
            collaborators={projectData.collaborators}
            onCollaboratorsChange={(collaborators) => updateProjectData('collaborators', collaborators)}
          />
        </CardContent>
      </Card>

      {/* Media Upload */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Media' : '媒体'}</Label>
                  <MediaUpload
          files={projectData.media}
          onFilesChange={(files: File[]) => updateProjectData('media', files)}
          maxFiles={9}
        />
      </div>

      {/* Project Tags */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Project Tags' : '项目标签'}</Label>
        <TagInput
          tags={projectData.projectTags}
          onTagsChange={(tags) => updateProjectData('projectTags', tags)}
          placeholder={i18nCurrentLanguage === 'en' ? 'Add project tags...' : '添加项目标签...'}
        />
      </div>

      {/* Your Role */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Your Role' : '你的角色'}</Label>
        <TagInput
          tags={projectData.ownRole}
          onTagsChange={(tags) => updateProjectData('ownRole', tags)}
          placeholder={i18nCurrentLanguage === 'en' ? 'Add your roles...' : '添加你的角色...'}
        />
      </div>

      {/* Start Time */}
      <div className="space-y-2">
        <Label htmlFor="startTime" className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Start Time *' : '开始时间 *'}</Label>
        <div className="relative">
          {/* Visible text input without any UA placeholder */}
          <Input
            id="startTime"
            type="text"
            readOnly
            value={projectData.startTime ? projectData.startTime : ''}
            onClick={() => nativeDateRef.current?.showPicker ? nativeDateRef.current.showPicker() : nativeDateRef.current?.click()}
            className="w-full text-foreground pl-10"
          />
          {/* Left calendar icon (clickable) */}
          <button
            type="button"
            onClick={() => nativeDateRef.current?.showPicker ? nativeDateRef.current.showPicker() : nativeDateRef.current?.click()}
            className="absolute inset-y-0 left-3 flex items-center text-muted-foreground"
            aria-label={i18nCurrentLanguage === 'en' ? 'Open date picker' : '打开日期选择器'}
          >
            <Calendar className="w-4 h-4" />
          </button>
          {/* Hidden native date input to leverage system picker */}
          <input
            ref={nativeDateRef}
            type="date"
            value={projectData.startTime}
            onChange={(e) => updateProjectData('startTime', e.target.value)}
            lang={i18nCurrentLanguage === 'en' ? 'en' : 'zh-CN'}
            style={{ position: 'absolute', opacity: 0, pointerEvents: 'none', width: 0, height: 0 }}
            tabIndex={-1}
          />
        </div>
      </div>

      {/* Current Progress */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? `Current Progress: ${projectData.currentProgress}%` : `当前进度：${projectData.currentProgress}%`}</Label>
        <Slider
          value={[projectData.currentProgress]}
          onValueChange={([value]) => updateProjectData('currentProgress', value)}
          max={100}
          step={5}
          className="w-full"
        />
      </div>

      {/* Detailed Description */}
      <div className="space-y-2">
        <Label htmlFor="detailedDescription" className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Detailed Description *' : '项目详细描述 *'}</Label>
        <Textarea
          id="detailedDescription"
          value={projectData.detailedDescription}
          onChange={(e) => updateProjectData('detailedDescription', e.target.value)}
          placeholder={i18nCurrentLanguage === 'en' ? 'Describe your project in detail' : '详细描述你的项目'}
          rows={4}
        />
      </div>

      {/* Purpose */}
      <div className="space-y-2">
        <Label htmlFor="purpose" className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Project Purpose' : '项目目的'}</Label>
        <Textarea
          id="purpose"
          value={projectData.purpose}
          onChange={(e) => updateProjectData('purpose', e.target.value)}
          placeholder={i18nCurrentLanguage === 'en' ? 'What is the main purpose of this project?' : '这个项目的主要目的是什么？'}
          rows={3}
        />
      </div>

      {/* What We Are Building */}
      <div className="space-y-2">
        <Label htmlFor="whatWeAreDoing" className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? "What We're Building" : '我们在做什么'}</Label>
        <Textarea
          id="whatWeAreDoing"
          value={projectData.whatWeAreDoing}
          onChange={(e) => updateProjectData('whatWeAreDoing', e.target.value)}
          placeholder={i18nCurrentLanguage === 'en' ? 'Describe what you are building or working on' : '描述你正在构建或进行的内容'}
          rows={3}
        />
      </div>

      {/* People Looking For */}
      <div className="space-y-2">
        <Label htmlFor="peopleLookingFor" className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'People We Are Looking For' : '我们在寻找的人'}</Label>
        <div className="space-y-2">
          <Label className="text-base">{i18nCurrentLanguage === 'en' ? 'Required skills/roles' : '所需技能/角色'}</Label>
          <TagInput
            tags={projectData.lookingForTags}
            onTagsChange={(tags) => updateProjectData('lookingForTags', tags)}
            placeholder={i18nCurrentLanguage === 'en' ? 'Add required skills or roles...' : '添加所需技能或角色...'}
          />
        </div>
        <Textarea
          id="peopleLookingFor"
          value={projectData.peopleLookingFor}
          onChange={(e) => updateProjectData('peopleLookingFor', e.target.value)}
          placeholder={i18nCurrentLanguage === 'en' ? 'Describe the type of collaborator you are looking for' : '描述你在寻找的合作者类型'}
          rows={3}
        />
      </div>

      {/* Links */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">{i18nCurrentLanguage === 'en' ? 'Related Links' : '相关链接'}</Label>
        <LinkInput
          links={projectData.links}
          onLinksChange={(links) => updateProjectData('links', links)}
        />
      </div>

      {/* Submit Button */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-card/95 backdrop-blur-sm border-t border-border shadow-lg z-50">
        <Button
          onClick={onSubmit}
          disabled={!isFormValid() || isSubmitting}
          className={!isFormValid() || isSubmitting ? 'w-full bg-muted text-foreground/60' : 'w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg transition-all duration-200 hover:shadow-xl'}
          size="lg"
        >
          {isSubmitting ? (i18nCurrentLanguage === 'en' ? 'Publishing...' : '发布中...') : (i18nCurrentLanguage === 'en' ? 'Publish Project' : '发布项目')}
        </Button>
      </div>
    </div>
  );
} 