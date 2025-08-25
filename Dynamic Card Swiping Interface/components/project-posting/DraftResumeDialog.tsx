import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';

interface DraftResumeDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onResume: () => void;
  onStartNew: () => void;
}

export function DraftResumeDialog({ isOpen, onOpenChange, onResume, onStartNew }: DraftResumeDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Resume Latest Draft?</DialogTitle>
          <DialogDescription>
            You have saved drafts from previous sessions. Would you like to resume editing your latest draft or start a new project?
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex-col gap-2">
          <Button onClick={onResume} className="w-full">
            Resume Latest Draft
          </Button>
          <Button variant="outline" onClick={onStartNew} className="w-full">
            Start New Project
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 