import { useState, useEffect } from 'react';
import { PostingProjectPage } from './components/PostingProjectPage';
import { DraftsPage } from './components/DraftsPage';
import { FloatingActionButtons } from './components/FloatingActionButtons';
import { DraftResumeDialog } from './components/DraftResumeDialog';
import { Button } from './components/ui/button';
import { Plus } from 'lucide-react';

export default function App() {
  const [showPostingPage, setShowPostingPage] = useState(false);
  const [showDraftsPage, setShowDraftsPage] = useState(false);
  const [showFloatingButtons, setShowFloatingButtons] = useState(false);
  const [showDraftDialog, setShowDraftDialog] = useState(false);
  const [resumeDraft, setResumeDraft] = useState(false);
  const [selectedDraftId, setSelectedDraftId] = useState<string | undefined>();



  const handlePostNewProjectClick = () => {
    // Check if there are any saved drafts
    const savedDrafts = localStorage.getItem('project_drafts');
    let hasDrafts = false;
    
    if (savedDrafts) {
      try {
        const drafts = JSON.parse(savedDrafts);
        hasDrafts = Array.isArray(drafts) && drafts.length > 0;
      } catch (error) {
        console.error('Error parsing drafts:', error);
        localStorage.removeItem('project_drafts');
      }
    }
    
    if (hasDrafts) {
      // Show draft resume dialog
      setShowDraftDialog(true);
    } else {
      // No drafts, start new project directly
      handleStartNewProject();
    }
  };

  const handleResumeLatestDraft = () => {
    // Get the latest draft (most recently created)
    const savedDrafts = localStorage.getItem('project_drafts');
    if (savedDrafts) {
      try {
        const drafts = JSON.parse(savedDrafts);
        if (drafts.length > 0) {
          // Sort by createdAt and get the latest
          const sortedDrafts = drafts.sort((a: any, b: any) => 
            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
          );
          const latestDraft = sortedDrafts[0];
          setSelectedDraftId(latestDraft.id);
          setResumeDraft(false);
          setShowDraftDialog(false);
          setShowPostingPage(true);
        }
      } catch (error) {
        console.error('Error loading latest draft:', error);
        handleStartNewProject();
      }
    } else {
      handleStartNewProject();
    }
  };

  const handleStartNewProject = () => {
    setResumeDraft(false);
    setSelectedDraftId(undefined);
    setShowDraftDialog(false);
    setShowFloatingButtons(false);
    setShowPostingPage(true);
  };

  const handleCreateNewProject = () => {
    setResumeDraft(false);
    setSelectedDraftId(undefined);
    setShowFloatingButtons(false);
    setShowPostingPage(true);
  };

  const handleOpenDrafts = () => {
    setShowFloatingButtons(false);
    setShowDraftsPage(true);
  };

  const handleEditDraft = (draftId: string) => {
    setSelectedDraftId(draftId);
    setResumeDraft(false);
    setShowDraftsPage(false);
    setShowPostingPage(true);
  };

  const handleBackFromPosting = () => {
    setShowPostingPage(false);
    setResumeDraft(false);
    setSelectedDraftId(undefined);
  };

  const handleBackFromDrafts = () => {
    setShowDraftsPage(false);
  };

  if (showPostingPage) {
    return (
      <PostingProjectPage 
        onBack={handleBackFromPosting} 
        resumeDraft={resumeDraft}
        draftId={selectedDraftId}
      />
    );
  }

  if (showDraftsPage) {
    return (
      <DraftsPage
        onBack={handleBackFromDrafts}
        onEditDraft={handleEditDraft}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-secondary/30 flex flex-col items-center justify-center p-4">
      <div className="text-center space-y-6 max-w-md">
        <div className="space-y-3">
          <h1 className="text-3xl font-semibold text-primary">Ques</h1>
          <p className="text-foreground/80 text-lg">
            Find your perfect project collaborators
          </p>
        </div>
        
        <div className="space-y-4">
          <Button 
            onClick={handlePostNewProjectClick}
            size="lg"
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg transition-all duration-200 hover:shadow-xl"
          >
            <Plus className="h-5 w-5 mr-2" />
            Post New Project
          </Button>
          
          <div className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/50">
            <p className="text-sm text-muted-foreground">
              Create a project posting to find collaborators who share your vision and complement your skills.
            </p>
          </div>
        </div>
      </div>

      {/* Floating Action Buttons */}
      <FloatingActionButtons
        isOpen={showFloatingButtons}
        onCreateNew={handleCreateNewProject}
        onOpenDrafts={handleOpenDrafts}
        onClose={() => setShowFloatingButtons(false)}
      />

      {/* Draft Resume Dialog */}
      <DraftResumeDialog
        isOpen={showDraftDialog}
        onOpenChange={setShowDraftDialog}
        onResume={handleResumeLatestDraft}
        onStartNew={handleStartNewProject}
      />
    </div>
  );
}