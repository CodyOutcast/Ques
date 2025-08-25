import { useState, useEffect } from 'react';
import { ArrowLeft, FileText, Edit, Trash2, Calendar } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';

interface Draft {
  id: string;
  title: string;
  createdAt: string;
  data: any;
}

interface DraftsPageProps {
  onBack: () => void;
  onEditDraft: (draftId: string) => void;
}

export function DraftsPage({ onBack, onEditDraft }: DraftsPageProps) {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [draftToDelete, setDraftToDelete] = useState<string | null>(null);

  useEffect(() => {
    loadDrafts();
  }, []);

  const loadDrafts = () => {
    const savedDrafts = localStorage.getItem('project_drafts');
    if (savedDrafts) {
      try {
        const parsedDrafts = JSON.parse(savedDrafts);
        setDrafts(parsedDrafts);
      } catch (error) {
        console.error('Error parsing drafts:', error);
        setDrafts([]);
      }
    } else {
      setDrafts([]);
    }
  };

  const handleDeleteDraft = (draftId: string) => {
    setDraftToDelete(draftId);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (draftToDelete) {
      const updatedDrafts = drafts.filter(draft => draft.id !== draftToDelete);
      localStorage.setItem('project_drafts', JSON.stringify(updatedDrafts));
      setDrafts(updatedDrafts);
      setShowDeleteDialog(false);
      setDraftToDelete(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background to-secondary/20">
      {/* Top Bar */}
      <div className="flex items-center justify-between p-4 border-b border-border bg-card/80 backdrop-blur-sm">
        <Button variant="ghost" size="icon" onClick={onBack} className="hover:bg-primary/10 hover:text-primary">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        
        <h1 className="text-lg font-semibold text-primary">Drafts</h1>
        
        <div className="w-10" />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {drafts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <FileText className="w-16 h-16 text-muted-foreground mb-4" />
            <h3 className="text-xl font-medium text-foreground mb-2">No drafts yet</h3>
            <p className="text-muted-foreground">
              Start creating a project to save drafts automatically.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {drafts.map((draft) => (
              <Card key={draft.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">
                        {draft.title || 'Untitled Project'}
                      </CardTitle>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(draft.createdAt)}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onEditDraft(draft.id)}
                        className="hover:bg-primary/10 hover:text-primary"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteDraft(draft.id)}
                        className="hover:bg-destructive/10 hover:text-destructive"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  {draft.data?.shortDescription && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {draft.data.shortDescription}
                    </p>
                  )}
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
              Are you sure you want to delete this draft? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col gap-2">
            <Button 
              variant="destructive" 
              onClick={confirmDelete} 
              className="w-full"
            >
              Delete Draft
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setShowDeleteDialog(false)} 
              className="w-full"
            >
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 