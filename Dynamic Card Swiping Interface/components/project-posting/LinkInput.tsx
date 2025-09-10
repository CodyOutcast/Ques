import { useState } from 'react';
import { X, Plus, Link as LinkIcon } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { currentLanguage as i18nCurrentLanguage } from '../../translations';

interface LinkInputProps {
  links: string[];
  onLinksChange: (links: string[]) => void;
  placeholder?: string;
  maxLinks?: number;
}

export function LinkInput({ links, onLinksChange, placeholder = (i18nCurrentLanguage === 'en' ? 'Add project links...' : '添加项目链接...'), maxLinks = 10 }: LinkInputProps) {
  const [inputValue, setInputValue] = useState('');

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleAddLink = () => {
    const trimmedValue = inputValue.trim();
    if (trimmedValue && !links.includes(trimmedValue) && links.length < maxLinks) {
      // Add http:// if no protocol specified
      const url = trimmedValue.startsWith('http://') || trimmedValue.startsWith('https://') 
        ? trimmedValue 
        : `https://${trimmedValue}`;
      
      if (validateUrl(url)) {
        onLinksChange([...links, url]);
        setInputValue('');
      }
    }
  };

  const handleRemoveLink = (linkToRemove: string) => {
    onLinksChange(links.filter(link => link !== linkToRemove));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddLink();
    }
  };

  const formatLink = (link: string): string => {
    try {
      const url = new URL(link);
      return url.hostname + url.pathname;
    } catch {
      return link;
    }
  };

  return (
    <div className="space-y-3">
      {/* Input and Add Button */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <LinkIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={links.length >= maxLinks}
            className="pl-10"
          />
        </div>
        <Button
          type="button"
          onClick={handleAddLink}
          disabled={!inputValue.trim() || links.length >= maxLinks}
          size="sm"
          variant="outline"
        >
          <Plus className="w-4 h-4" />
        </Button>
      </div>

      {/* Links Display */}
      {links.length > 0 && (
        <div className="space-y-2">
          {links.map((link, index) => (
            <div key={index} className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
              <LinkIcon className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              <a
                href={link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 text-sm text-primary hover:underline truncate"
              >
                {formatLink(link)}
              </a>
              <button
                type="button"
                onClick={() => handleRemoveLink(link)}
                className="text-muted-foreground hover:text-destructive transition-colors flex-shrink-0"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Max Links Warning */}
      {links.length >= maxLinks && (
        <p className="text-sm text-muted-foreground">
          {i18nCurrentLanguage === 'en' ? `Maximum of ${maxLinks} links reached` : `已达到最多 ${maxLinks} 个链接`}
        </p>
      )}
    </div>
  );
} 