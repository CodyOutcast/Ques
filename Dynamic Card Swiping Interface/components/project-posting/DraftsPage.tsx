import { useState, useEffect } from 'react';
import { ArrowLeft, FileText, Edit, Trash2, Calendar } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { t, currentLanguage as i18nCurrentLanguage } from '../../translations';

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
    const locale = (i18nCurrentLanguage === 'en') ? 'en-US' : 'zh-CN';
    return date.toLocaleDateString(locale as any, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    } as any);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background to-secondary/20">
      {/* Top Bar */}
      <div className="flex items-center justify-between p-4 border-b border-border bg-card/80 backdrop-blur-sm">
        <Button variant="ghost" size="icon" onClick={onBack} className="hover:bg-primary/10 hover:text-primary">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        
        <h1 className="text-lg font-semibold text-primary">{i18nCurrentLanguage === 'en' ? 'Drafts' : '草稿箱'}</h1>
        
        <div className="w-10" />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {drafts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <FileText className="w-16 h-16 text-muted-foreground mb-4" />
            <h3 className="text-xl font-medium text-foreground mb-2">{i18nCurrentLanguage === 'en' ? 'No drafts yet' : '暂无草稿'}</h3>
            <p className="text-muted-foreground">
              {i18nCurrentLanguage === 'en' ? 'Drafts will be saved automatically once you start creating a project.' : '开始创建项目后，系统会自动保存草稿。'}
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
                        {draft.title || (i18nCurrentLanguage === 'en' ? 'Untitled Project' : '未命名项目')}
                      </CardTitle>
                      <div className="flex items-start gap-2 text-sm text-muted-foreground">
                        <Calendar className="w-4 h-4 mt-0.5" />
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
                        {i18nCurrentLanguage === 'en' ? 'Edit' : '编辑'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteDraft(draft.id)}
                        className="hover:bg-destructive/10 hover:text-destructive"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        {i18nCurrentLanguage === 'en' ? 'Delete' : '删除'}
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
            <DialogTitle>{i18nCurrentLanguage === 'en' ? 'Delete draft?' : '删除草稿？'}</DialogTitle>
            <DialogDescription>
              {i18nCurrentLanguage === 'en' ? 'Are you sure you want to delete this draft? This action cannot be undone.' : '确定要删除该草稿吗？此操作不可恢复。'}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col gap-2">
            <Button 
              variant="destructive" 
              onClick={confirmDelete} 
              className="w-full"
            >
              {i18nCurrentLanguage === 'en' ? 'Delete Draft' : '删除草稿'}
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setShowDeleteDialog(false)} 
              className="w-full"
            >
              {i18nCurrentLanguage === 'en' ? 'Cancel' : '取消'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 