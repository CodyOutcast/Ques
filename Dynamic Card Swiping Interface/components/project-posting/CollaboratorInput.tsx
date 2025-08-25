import { useState } from 'react';
import { X, Plus, User } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { TagInput } from './TagInput';

interface Collaborator {
  id: string;
  name: string;
  role: string[];
}

interface CollaboratorInputProps {
  collaborators: Collaborator[];
  onCollaboratorsChange: (collaborators: Collaborator[]) => void;
}

export function CollaboratorInput({ collaborators, onCollaboratorsChange }: CollaboratorInputProps) {
  const [newName, setNewName] = useState('');
  const [newRoles, setNewRoles] = useState<string[]>([]);

  const handleAddCollaborator = () => {
    if (newName.trim() && newRoles.length > 0) {
      const newCollaborator: Collaborator = {
        id: Date.now().toString(),
        name: newName.trim(),
        role: newRoles,
      };
      onCollaboratorsChange([...collaborators, newCollaborator]);
      setNewName('');
      setNewRoles([]);
    }
  };

  const handleRemoveCollaborator = (id: string) => {
    onCollaboratorsChange(collaborators.filter(c => c.id !== id));
  };

  const handleUpdateCollaborator = (id: string, field: keyof Collaborator, value: any) => {
    onCollaboratorsChange(
      collaborators.map(c => 
        c.id === id ? { ...c, [field]: value } : c
      )
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddCollaborator();
    }
  };

  return (
    <div className="space-y-4">
      {/* Add New Collaborator */}
      <Card>
        <CardContent className="p-4 space-y-3">
          <h4 className="font-medium text-sm">Add New Collaborator</h4>
          
          <div className="space-y-3">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Collaborator name"
              className="w-full"
            />
            
            <TagInput
              tags={newRoles}
              onTagsChange={setNewRoles}
              placeholder="Add roles..."
              maxTags={5}
            />
            
            <Button
              onClick={handleAddCollaborator}
              disabled={!newName.trim() || newRoles.length === 0}
              size="sm"
              className="w-full"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Collaborator
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Existing Collaborators */}
      {collaborators.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium text-sm">Current Collaborators</h4>
          
          {collaborators.map((collaborator) => (
            <Card key={collaborator.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-muted-foreground" />
                      <Input
                        value={collaborator.name}
                        onChange={(e) => handleUpdateCollaborator(collaborator.id, 'name', e.target.value)}
                        placeholder="Name"
                        className="flex-1"
                      />
                    </div>
                    
                    <TagInput
                      tags={collaborator.role}
                      onTagsChange={(roles) => handleUpdateCollaborator(collaborator.id, 'role', roles)}
                      placeholder="Roles..."
                      maxTags={5}
                    />
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRemoveCollaborator(collaborator.id)}
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 