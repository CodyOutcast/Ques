import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { ArrowLeft, FileText, Trash2, Edit, Calendar, User } from 'lucide-react';

interface Draft {
  id: string;
  title: string;
  shortDescription: string;
  lastModified: string;
  projectTags: string[];
  collaboratorsCount: number;
  progress: number;
}

interface DraftsPageProps {
  onBack: () => void;
  onEditDraft: (draftId: string) => void;
}

export function DraftsPage({ onBack, onEditDraft }: DraftsPageProps) {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [selectedDraft, setSelectedDraft] = useState<Draft | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  useEffect(() => {
    loadDrafts();
  }, []);

  const loadDrafts = () => {
    // Load drafts from localStorage
    const savedDrafts = localStorage.getItem('project_drafts');
    if (savedDrafts) {
      try {
        const parsedDrafts = JSON.parse(savedDrafts);
        // Convert saved drafts to display format
        const formattedDrafts = parsedDrafts.map((savedDraft: any) => ({
          id: savedDraft.id,
          title: savedDraft.data.title || 'Untitled Project',
          shortDescription: savedDraft.data.shortDescription || 'No description',
          lastModified: savedDraft.createdAt,
          projectTags: savedDraft.data.projectTags || [],
          collaboratorsCount: savedDraft.data.collaborators?.length || 0,
          progress: savedDraft.data.currentProgress || 0,
        }));
        setDrafts(formattedDrafts);
      } catch (error) {
        console.error('Error loading drafts:', error);
        setDrafts([]);
      }
    }
  };

  const handleEditDraft = (draft: Draft) => {
    onEditDraft(draft.id);
  };

  const handleDeleteDraft = (draft: Draft) => {
    setSelectedDraft(draft);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedDraft) {
      // Get saved drafts
      const savedDrafts = localStorage.getItem('project_drafts');
      if (savedDrafts) {
        try {
          const parsedDrafts = JSON.parse(savedDrafts);
          const updatedDrafts = parsedDrafts.filter((draft: any) => draft.id !== selectedDraft.id);
          localStorage.setItem('project_drafts', JSON.stringify(updatedDrafts));
        } catch (error) {
          console.error('Error deleting draft:', error);
        }
      }
    }
    setShowDeleteDialog(false);
    setSelectedDraft(null);
    loadDrafts(); // Reload to sync state
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) {
      return `${diffMins} minutes ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hours ago`;
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Top Bar */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        
        <h1 className="text-lg font-medium">Drafts</h1>
        
        <div className="w-10" /> {/* Spacer for centering */}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {drafts.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No Drafts Yet</h3>
            <p className="text-muted-foreground">
              Your draft projects will appear here when you save them.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {drafts.map((draft) => (
              <Card key={draft.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-base truncate">{draft.title}</CardTitle>
                      <CardDescription className="mt-1 line-clamp-2">
                        {draft.shortDescription}
                      </CardDescription>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditDraft(draft);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteDraft(draft);
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {/* Tags */}
                    {draft.projectTags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {draft.projectTags.slice(0, 3).map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {draft.projectTags.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{draft.projectTags.length - 3} more
                          </Badge>
                        )}
                      </div>
                    )}
                    
                    {/* Metadata */}
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(draft.lastModified)}</span>
                        </div>
                        
                        {draft.collaboratorsCount > 0 && (
                          <div className="flex items-center space-x-1">
                            <User className="h-3 w-3" />
                            <span>{draft.collaboratorsCount} collaborators</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="text-right">
                        <span>{draft.progress}% complete</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Draft?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{selectedDraft?.title}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Delete Draft
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}