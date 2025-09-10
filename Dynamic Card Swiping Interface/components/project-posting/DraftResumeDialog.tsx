import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { currentLanguage as i18nCurrentLanguage } from '../../translations';

interface DraftResumeDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onResume: () => void;
  onStartNew: () => void;
}

export function DraftResumeDialog({ isOpen, onOpenChange, onResume, onStartNew }: DraftResumeDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="w-[360px] max-w-[360px] p-4 sm:p-5">
        <DialogHeader>
          <DialogTitle className="text-xl">{i18nCurrentLanguage === 'en' ? 'Resume last draft?' : '继续上次草稿？'}</DialogTitle>
          <DialogDescription className="text-sm">
            {i18nCurrentLanguage === 'en' ? 'A saved draft was found from your previous session. Continue editing the latest draft or start a new project?' : '检测到你在之前的会话中保存了草稿。现在要继续编辑最近的草稿，还是开始一个新项目？'}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex-col gap-2 items-center sm:flex-col sm:justify-center">
          <Button variant="default" onClick={onResume} className="w-full h-11 text-base">
            {i18nCurrentLanguage === 'en' ? 'Resume latest draft' : '继续最近草稿'}
          </Button>
          <Button variant="outline" onClick={onStartNew} className="w-full h-11 text-base">
            {i18nCurrentLanguage === 'en' ? 'Start new project' : '开始新项目'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 