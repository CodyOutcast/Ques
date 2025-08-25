import { useState, KeyboardEvent } from 'react';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { X } from 'lucide-react';

interface TagInputProps {
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
}

export function TagInput({ tags, onTagsChange, placeholder = "Add tags...", maxTags = 10 }: TagInputProps) {
  const [inputValue, setInputValue] = useState('');

  const addTag = (tag: string) => {
    const trimmedTag = tag.trim();
    if (trimmedTag && !tags.includes(trimmedTag) && tags.length < maxTags) {
      onTagsChange([...tags, trimmedTag]);
      setInputValue('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    onTagsChange(tags.filter(tag => tag !== tagToRemove));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
      removeTag(tags[tags.length - 1]);
    }
  };

  const handleInputBlur = () => {
    if (inputValue.trim()) {
      addTag(inputValue);
    }
  };

  return (
    <div className="space-y-3">
      {/* Tags Display */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag, index) => (
            <Badge key={index} variant="secondary" className="pr-1">
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-1 hover:bg-destructive hover:text-destructive-foreground rounded-full p-0.5 transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}
      
      {/* Input */}
      {tags.length < maxTags && (
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={handleInputBlur}
          placeholder={placeholder}
          className="w-full"
        />
      )}
      
      <p className="text-sm text-muted-foreground">
        Press Enter or comma to add tags. {tags.length}/{maxTags} tags added.
      </p>
    </div>
  );
}