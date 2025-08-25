import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Plus, Trash2, ExternalLink } from 'lucide-react';

interface LinkInputProps {
  links: string[];
  onLinksChange: (links: string[]) => void;
}

export function LinkInput({ links, onLinksChange }: LinkInputProps) {
  const [newLink, setNewLink] = useState('');

  const addLink = () => {
    const trimmedLink = newLink.trim();
    if (trimmedLink && !links.includes(trimmedLink)) {
      onLinksChange([...links, trimmedLink]);
      setNewLink('');
    }
  };

  const handleAddClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    addLink();
  };

  const removeLink = (index: number) => {
    onLinksChange(links.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addLink();
    }
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const formatUrl = (url: string) => {
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      return `https://${url}`;
    }
    return url;
  };

  return (
    <div className="space-y-4">
      {/* Existing Links */}
      {links.length > 0 && (
        <div className="space-y-2">
          {links.map((link, index) => (
            <Card key={index}>
              <CardContent className="p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <a
                      href={formatUrl(link)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline truncate"
                    >
                      {link}
                    </a>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeLink(index)}
                    className="flex-shrink-0"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add New Link */}
      <div className="flex space-x-2">
        <Input
          value={newLink}
          onChange={(e) => setNewLink(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter project link (e.g., github.com/username/repo)"
          className="flex-1"
        />
        <Button
          onClick={handleAddClick}
          disabled={!newLink.trim()}
          variant="outline"
          type="button"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      <p className="text-sm text-muted-foreground">
        Add links to your project repository, website, or other relevant resources.
      </p>
    </div>
  );
}