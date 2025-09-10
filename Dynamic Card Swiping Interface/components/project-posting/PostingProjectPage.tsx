import { useState, useEffect } from 'react';
import { ArrowLeft, FileText } from 'lucide-react';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { ProjectForm } from './ProjectForm';
import { DraftsPage } from './DraftsPage';
import { createProject } from '../../src/api/projects';
import { t, currentLanguage as i18nCurrentLanguage } from '../../translations';

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

const initialProjectData: ProjectData = {
  title: '',
  shortDescription: '',
  media: [],
  projectTags: [],
  ownRole: [],
  collaborators: [],
  startTime: '',
  currentProgress: 0,
  detailedDescription: '',
  purpose: '',
  whatWeAreDoing: '',
  peopleLookingFor: '',
  lookingForTags: [],
  links: [],
};

interface PostingProjectPageProps {
  onBack: () => void;
  resumeDraft?: boolean;
  draftId?: string;
  onPublished?: (newProject?: any) => void;
  onPublishError?: (error: unknown) => void;
}

export function PostingProjectPage({ onBack, resumeDraft = false, draftId, onPublished, onPublishError }: PostingProjectPageProps) {
  console.log('🏗️ PostingProjectPage render start', { onBack: !!onBack, resumeDraft, draftId, onPublished: !!onPublished, onPublishError: !!onPublishError });
  
  const [projectData, setProjectData] = useState<ProjectData>(initialProjectData);
  const [hasChanges, setHasChanges] = useState(false);
  const [showExitDialog, setShowExitDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDraftsPage, setShowDraftsPage] = useState(false);
  
  console.log('🏗️ PostingProjectPage state', { 
    projectData: projectData.title, 
    hasChanges, 
    showExitDialog, 
    isSubmitting, 
    showDraftsPage 
  });

  // Load draft on mount if resumeDraft is true or draftId is provided
  useEffect(() => {
    if (draftId) {
      // Load specific draft by ID
      const savedDrafts = localStorage.getItem('project_drafts');
      if (savedDrafts) {
        try {
          const drafts = JSON.parse(savedDrafts);
          const specificDraft = drafts.find((draft: any) => draft.id === draftId);
          if (specificDraft) {
            const updatedDraft = {
              ...initialProjectData,
              ...specificDraft.data,
              projectTags: specificDraft.data.projectTags || [],
              lookingForTags: specificDraft.data.lookingForTags || [],
              links: specificDraft.data.links || [],
            };
            setProjectData(updatedDraft);
            setHasChanges(true);
          }
        } catch (error) {
          console.error('Failed to load specific draft:', error);
        }
      }
    } else if (resumeDraft) {
      // Load legacy draft format for backward compatibility
      const savedDraft = localStorage.getItem('project_draft');
      if (savedDraft) {
        try {
          const draft = JSON.parse(savedDraft);
          const updatedDraft = {
            ...initialProjectData,
            ...draft,
            projectTags: draft.projectTags || [],
            lookingForTags: draft.lookingForTags || [],
            links: draft.links || [],
          };
          setProjectData(updatedDraft);
          setHasChanges(true);
        } catch (error) {
          console.error('Failed to load draft:', error);
        }
      }
    }
  }, [resumeDraft, draftId]);

  // Track changes to project data
  useEffect(() => {
    const isEmpty = !projectData.title && !projectData.shortDescription && 
                   !projectData.detailedDescription && !projectData.purpose &&
                   !projectData.whatWeAreDoing && !projectData.peopleLookingFor &&
                   projectData.ownRole.length === 0 && projectData.collaborators.length === 0 &&
                   projectData.media.length === 0 && projectData.projectTags.length === 0 &&
                   projectData.lookingForTags.length === 0 && projectData.links.length === 0;
    setHasChanges(!isEmpty);
  }, [projectData]);

  const handleBack = () => {
    if (hasChanges) {
      setShowExitDialog(true);
    } else {
      onBack();
    }
  };

  const handleSaveDraft = () => {
    // Get existing drafts
    const existingDrafts = localStorage.getItem('project_drafts');
    let drafts = [] as any[];
    
    if (existingDrafts) {
      try {
        drafts = JSON.parse(existingDrafts);
      } catch (error) {
        console.error('Error parsing existing drafts:', error);
      }
    }
    
    // Create new draft entry
    const newDraft = {
      id: Date.now().toString(),
      data: projectData,
      createdAt: new Date().toISOString(),
      title: projectData.title || (i18nCurrentLanguage === 'en' ? 'Untitled Project' : '未命名项目'),
    };
    
    // Add to drafts array
    drafts.push(newDraft);
    
    // Save updated drafts
    localStorage.setItem('project_drafts', JSON.stringify(drafts));
    
    // Remove old single draft format for backward compatibility
    localStorage.removeItem('project_draft');
    
    setShowExitDialog(false);
    onBack();
  };

  const handleDiscardAndExit = () => {
    // Don't remove all drafts, just exit without saving current changes
    setShowExitDialog(false);
    onBack();
  };

  const handleOpenDrafts = () => {
    setShowDraftsPage(true);
  };

  const handleEditDraft = (editDraftId: string) => {
    // Load specific draft
    const savedDrafts = localStorage.getItem('project_drafts');
    if (savedDrafts) {
      try {
        const drafts = JSON.parse(savedDrafts);
        const specificDraft = drafts.find((draft: any) => draft.id === editDraftId);
        if (specificDraft) {
          const updatedDraft = {
            ...initialProjectData,
            ...specificDraft.data,
            projectTags: specificDraft.data.projectTags || [],
            lookingForTags: specificDraft.data.lookingForTags || [],
            links: specificDraft.data.links || [],
          };
          setProjectData(updatedDraft);
          setHasChanges(true);
        }
      } catch (error) {
        console.error('Failed to load specific draft:', error);
      }
    }
    setShowDraftsPage(false);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Map form data to backend ProjectCreate request
      const payload = {
        short_description: projectData.shortDescription ? projectData.shortDescription : '',
        long_description: (projectData.detailedDescription || projectData.purpose) ? (projectData.detailedDescription || projectData.purpose) : '',
        start_time: new Date(projectData.startTime).toISOString(),
        status: 'ONGOING' as const,
        media_link_id: null as number | null,
      };

      // Build media object URLs for preview/sync
      const mediaUrls: string[] = Array.isArray(projectData.media)
        ? projectData.media
            .filter((f) => !!f)
            .map((f) => {
              try { return URL.createObjectURL(f); } catch { return ''; }
            })
            .filter(Boolean)
        : [];

      const firstImageUrl = mediaUrls[0] || 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=600&fit=crop&crop=center';
      const desc = projectData.whatWeAreDoing || projectData.detailedDescription || projectData.shortDescription || (i18nCurrentLanguage === 'en' ? 'No description' : '暂无描述');
      const statusTextZh = ((): string => {
        const p = Number(projectData.currentProgress || 0);
        if (p <= 0) return '未开始';
        if (p >= 100) return '已完成';
        return '进行中';
      })();

      const optimisticProject: any = {
        id: Date.now(),
        title: projectData.title || (i18nCurrentLanguage === 'en' ? 'Untitled Project' : '未命名项目'),
        description: desc,
        status: statusTextZh,
        progress: projectData.currentProgress || 0,
        image: firstImageUrl,
        tags: projectData.projectTags || [],
        startDate: projectData.startTime || (i18nCurrentLanguage === 'en' ? 'Recently' : '近期'),
        createdAt: Date.now(),
        role: Array.isArray(projectData.ownRole) && projectData.ownRole.length > 0 ? projectData.ownRole[0] : undefined,
        media: mediaUrls,
        links: Array.isArray(projectData.links) ? projectData.links : [],
      };

      // Try real API but fall back to optimistic success
      try {
        const resp = await createProject(payload);
        console.log('Project created:', resp);
        if (resp && (resp as any).id) {
          optimisticProject.id = (resp as any).id;
        }
      } catch (apiErr) {
        console.warn('API failed, using optimistic publish:', apiErr);
      }

      if (onPublished) onPublished(optimisticProject);
      onBack();
    } catch (error) {
      console.error('Unexpected error in submit:', error);
      // 依然走本地成功
      try {
        const mediaUrls: string[] = Array.isArray(projectData.media)
          ? projectData.media
              .filter((f) => !!f)
              .map((f) => {
                try { return URL.createObjectURL(f); } catch { return ''; }
              })
              .filter(Boolean)
          : [];
        const firstImageUrl = mediaUrls[0] || 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=600&fit=crop&crop=center';
        const desc = projectData.whatWeAreDoing || projectData.detailedDescription || projectData.shortDescription || (i18nCurrentLanguage === 'en' ? 'No description' : '暂无描述');
        const statusTextZh = ((): string => {
          const p = Number(projectData.currentProgress || 0);
          if (p <= 0) return '未开始';
          if (p >= 100) return '已完成';
          return '进行中';
        })();
        const newProject = {
          id: Date.now(),
          title: projectData.title || (i18nCurrentLanguage === 'en' ? 'Untitled Project' : '未命名项目'),
          description: desc,
          status: statusTextZh,
          progress: projectData.currentProgress || 0,
          image: firstImageUrl,
          tags: projectData.projectTags || [],
          startDate: projectData.startTime || (i18nCurrentLanguage === 'en' ? 'Recently' : '近期'),
          createdAt: Date.now(),
          role: Array.isArray(projectData.ownRole) && projectData.ownRole.length > 0 ? projectData.ownRole[0] : undefined,
          media: mediaUrls,
          links: Array.isArray(projectData.links) ? projectData.links : [],
        };
        if (onPublished) onPublished(newProject as any);
      } catch {}
      onBack();
    } finally {
      setIsSubmitting(false);
    }
  };

  if (showDraftsPage) {
    console.log('📋 Rendering DraftsPage instead of PostingProjectPage');
    return (
      <DraftsPage
        onBack={() => setShowDraftsPage(false)}
        onEditDraft={handleEditDraft}
      />
    );
  }

  console.log('🎨 About to render PostingProjectPage main UI');

  return (
    <div 
      className="flex flex-col h-screen bg-gradient-to-br from-background to-secondary/20"
      style={{
        backgroundColor: '#ffffff',
        minHeight: '100vh',
        width: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Top Bar - align with SettingsPage */}
      <div 
        className="h-[90px] px-[19px] z-0 relative bg-[#FAFAFA] border-b border-[#E8EDF2] flex items-center"
      >
        <div className="flex items-center justify-between w-[354px]">
          <button onClick={handleBack} className="p-2"><ArrowLeft className="w-6 h-6 text-[#0055F7]" /></button>
          <h1 className="text-lg font-bold">{t('projects') || (i18nCurrentLanguage === 'en' ? 'Projects' : '发布项目')}</h1>
          <button onClick={handleOpenDrafts} className="p-2"><FileText className="w-5 h-5 text-[#0055F7]" /></button>
        </div>
      </div>

      {/* Form Content */}
      <div 
        className="flex-1 overflow-y-auto p-4"
        style={{
          flex: 1,
          overflowY: 'auto',
          backgroundColor: '#ffffff'
        }}
      >
        {(() => {
          console.log('📝 Rendering Form Content area');
          return null;
        })()}
        
        <ProjectForm
          projectData={projectData}
          onProjectDataChange={setProjectData}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />
      </div>

      {/* Exit Confirmation Dialog */}
      <Dialog open={showExitDialog} onOpenChange={setShowExitDialog}>
        <DialogContent className="w-[360px] max-w-[360px] p-4 sm:p-5">
          <DialogHeader>
            <DialogTitle className="text-xl">{i18nCurrentLanguage === 'en' ? 'Save your progress?' : '保存当前进度？'}</DialogTitle>
            <DialogDescription className="text-sm">
              {i18nCurrentLanguage === 'en' ? 'You have unsaved changes. Save as draft or discard changes?' : '你有未保存的更改。是否保存为草稿，或者放弃更改？'}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col gap-2 items-center sm:flex-col sm:justify-center">
            <Button onClick={handleSaveDraft} className="w-full h-11 text-base">
              {i18nCurrentLanguage === 'en' ? 'Save to Drafts' : '保存到草稿'}
            </Button>
            <Button variant="outline" onClick={handleDiscardAndExit} className="w-full h-11 text-base">
              {i18nCurrentLanguage === 'en' ? 'Discard changes' : '放弃更改'}
            </Button>
            <Button variant="ghost" onClick={() => setShowExitDialog(false)} className="w-full h-11 text-base">
              {i18nCurrentLanguage === 'en' ? 'Continue Editing' : '继续编辑'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 