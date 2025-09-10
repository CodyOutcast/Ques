import { useState, useRef } from 'react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { X, Plus, Image, Video, Star, GripVertical } from 'lucide-react';
import { currentLanguage as i18nCurrentLanguage } from '../../translations';

interface MediaUploadProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  maxFiles: number;
}

export function MediaUpload({ files, onFilesChange, maxFiles }: MediaUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previews, setPreviews] = useState<string[]>([]);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    const remainingSlots = maxFiles - files.length;
    const newFiles = selectedFiles.slice(0, remainingSlots);
    
    if (newFiles.length > 0) {
      const updatedFiles = [...files, ...newFiles];
      onFilesChange(updatedFiles);
      
      const newPreviews = [...previews];
      newFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          newPreviews[files.length + index] = e.target?.result as string;
          setPreviews([...newPreviews]);
        };
        reader.readAsDataURL(file);
      });
    }
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    const updatedPreviews = previews.filter((_, i) => i !== index);
    onFilesChange(updatedFiles);
    setPreviews(updatedPreviews);
  };

  const moveFile = (fromIndex: number, toIndex: number) => {
    const updatedFiles = [...files];
    const updatedPreviews = [...previews];
    const [movedFile] = updatedFiles.splice(fromIndex, 1);
    updatedFiles.splice(toIndex, 0, movedFile);
    const [movedPreview] = updatedPreviews.splice(fromIndex, 1);
    updatedPreviews.splice(toIndex, 0, movedPreview);
    onFilesChange(updatedFiles);
    setPreviews(updatedPreviews);
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
    e.dataTransfer.setData('text/plain', index.toString());
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    setDragOverIndex(index);
  };

  const handleDragLeave = () => {
    setDragOverIndex(null);
  };

  const handleDrop = (e: React.DragEvent, toIndex: number) => {
    e.preventDefault();
    setDragOverIndex(null);
    const fromIndex = parseInt(e.dataTransfer.getData('text/plain'));
    if (fromIndex !== toIndex) {
      moveFile(fromIndex, toIndex);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const isImage = (file: File) => file.type.startsWith('image/');
  const isVideo = (file: File) => file.type.startsWith('video/');

  return (
    <div className="space-y-4">
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,video/*"
        onChange={handleFileSelect}
        className="hidden"
      />
      
      <div className="space-y-1">
        <p className="text-sm text-muted-foreground">
          {i18nCurrentLanguage === 'en' ? 'The first image/video will be used as the card cover.' : '第一张图片/视频将作为卡片封面。'}
        </p>
        {files.length > 1 && (
          <p className="text-xs text-muted-foreground">
            {i18nCurrentLanguage === 'en' ? 'Drag to reorder media files.' : '拖拽即可调整媒体文件顺序。'}
          </p>
        )}
      </div>
      
      <div className="grid grid-cols-3 gap-2">
        {files.map((file, index) => (
          <Card 
            key={index}
            draggable
            onDragStart={(e) => handleDragStart(e, index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, index)}
            className={`relative aspect-square overflow-hidden cursor-move transition-all duration-200 ${
              index === 0 ? 'ring-2 ring-primary ring-offset-2' : ''
            } ${
              dragOverIndex === index ? 'ring-2 ring-accent ring-offset-2 scale-105' : ''
            }`}
          >
            {index === 0 && (
              <div className="absolute top-2 left-2 z-30">
                <Star className="h-5 w-5 fill-yellow-400 text-yellow-400 drop-shadow-md" />
              </div>
            )}
            
            <div className="absolute top-1 left-1 z-10">
              <GripVertical className="h-4 w-4 text-white drop-shadow-md" />
            </div>
            
            {isImage(file) && previews[index] ? (
              <img
                src={previews[index]}
                alt={`Preview ${index + 1}`}
                className="w-full h-full object-cover"
              />
            ) : isVideo(file) && previews[index] ? (
              <div className="relative w-full h-full">
                <video
                  src={previews[index]}
                  className="w-full h-full object-cover"
                  muted
                />
                <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30">
                  <Video className="h-8 w-8 text-white" />
                </div>
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-muted">
                {isImage(file) ? (
                  <Image className="h-8 w-8 text-muted-foreground" />
                ) : (
                  <Video className="h-8 w-8 text-muted-foreground" />
                )}
              </div>
            )}
            
            <Button
              variant="destructive"
              size="icon"
              className="absolute top-1 right-1 h-6 w-6"
              onClick={() => removeFile(index)}
            >
              <X className="h-3 w-3" />
            </Button>
          </Card>
        ))}
        
        {files.length < maxFiles && (
          <Card
            className="aspect-square flex items-center justify-center border-dashed border-2 cursor-pointer hover:border-primary transition-colors"
            onClick={openFileDialog}
          >
            <div className="text-center">
              <Plus className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-xs text-muted-foreground">{i18nCurrentLanguage === 'en' ? 'Add Media' : '添加媒体'}</p>
            </div>
          </Card>
        )}
      </div>
      
      <p className="text-sm text-muted-foreground">
        {i18nCurrentLanguage === 'en' ? `Uploaded ${files.length}/${maxFiles} files. Images and videos are supported.` : `已上传 ${files.length}/${maxFiles} 个文件。支持图片与视频。`}
      </p>
    </div>
  );
} 