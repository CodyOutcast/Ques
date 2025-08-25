import { useState } from 'react';
import { X, Plus } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';

interface TagInputProps {
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
}

export function TagInput({ tags, onTagsChange, placeholder = "Add tags...", maxTags = 10 }: TagInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleAddTag = () => {
    const trimmedValue = inputValue.trim();
    if (trimmedValue && !tags.includes(trimmedValue) && tags.length < maxTags) {
      onTagsChange([...tags, trimmedValue]);
      setInputValue('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    onTagsChange(tags.filter(tag => tag !== tagToRemove));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <div className="space-y-3">
      {/* Input and Add Button */}
      <div className="flex gap-2">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={tags.length >= maxTags}
          className="flex-1"
        />
        <Button
          type="button"
          onClick={handleAddTag}
          disabled={!inputValue.trim() || tags.length >= maxTags}
          size="sm"
          variant="outline"
        >
          <Plus className="w-4 h-4" />
        </Button>
      </div>

      {/* Tags Display */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag, index) => (
            <Badge
              key={index}
              variant="secondary"
              className="px-3 py-1 text-sm flex items-center gap-1"
            >
              {tag}
              <button
                type="button"
                onClick={() => handleRemoveTag(tag)}
                className="ml-1 hover:text-destructive transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}

      {/* Max Tags Warning */}
      {tags.length >= maxTags && (
        <p className="text-sm text-muted-foreground">
          Maximum {maxTags} tags reached
        </p>
      )}
    </div>
  );
} 