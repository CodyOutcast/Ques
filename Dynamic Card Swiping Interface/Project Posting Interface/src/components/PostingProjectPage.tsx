import { useState, useEffect } from 'react';
import { ArrowLeft, FileText } from 'lucide-react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { ProjectForm } from './ProjectForm';
import { DraftsPage } from './DraftsPage';

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
}

export function PostingProjectPage({ onBack, resumeDraft = false, draftId }: PostingProjectPageProps) {
  const [projectData, setProjectData] = useState<ProjectData>(initialProjectData);
  const [hasChanges, setHasChanges] = useState(false);
  const [showExitDialog, setShowExitDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDraftsPage, setShowDraftsPage] = useState(false);

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
    let drafts = [];
    
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
      title: projectData.title || 'Untitled Project',
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
      // TODO: Implement actual submission logic
      console.log('Submitting project:', projectData);
      
      // Clear current draft after successful submission if it was a resumed draft
      // Don't clear all drafts, just the current one if it exists
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      onBack();
    } catch (error) {
      console.error('Failed to submit project:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (showDraftsPage) {
    return (
      <DraftsPage
        onBack={() => setShowDraftsPage(false)}
        onEditDraft={handleEditDraft}
      />
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background to-secondary/20">
      {/* Top Bar */}
      <div className="flex items-center justify-between p-4 border-b border-border bg-card/80 backdrop-blur-sm">
        <Button variant="ghost" size="icon" onClick={handleBack} className="hover:bg-primary/10 hover:text-primary">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        
        <h1 className="text-lg font-semibold text-primary">Posting Project</h1>
        
        <Button variant="ghost" size="icon" onClick={handleOpenDrafts} className="hover:bg-primary/10 hover:text-primary">
          <FileText className="h-5 w-5" />
        </Button>
      </div>

      {/* Form Content */}
      <div className="flex-1 overflow-y-auto">
        <ProjectForm
          projectData={projectData}
          onProjectDataChange={setProjectData}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />
      </div>

      {/* Exit Confirmation Dialog */}
      <Dialog open={showExitDialog} onOpenChange={setShowExitDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save your progress?</DialogTitle>
            <DialogDescription>
              You have unsaved changes. Would you like to save them as a draft or discard them?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col gap-2">
            <Button onClick={handleSaveDraft} className="w-full">
              Save to Drafts
            </Button>
            <Button variant="outline" onClick={handleDiscardAndExit} className="w-full">
              Discard Changes
            </Button>
            <Button variant="ghost" onClick={() => setShowExitDialog(false)} className="w-full">
              Continue Editing
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}