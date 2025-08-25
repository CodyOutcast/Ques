import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent } from './ui/card';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { TagInput } from './TagInput';
import { Plus, Edit, Trash2, User } from 'lucide-react';

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
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [editingCollaborator, setEditingCollaborator] = useState<Collaborator | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    role: [] as string[],
  });

  const resetForm = () => {
    setFormData({
      name: '',
      role: [],
    });
  };

  const handleAddCollaborator = () => {
    setIsAddDialogOpen(true);
  };

  const handleAdd = () => {
    if (formData.name.trim()) {
      const newCollaborator: Collaborator = {
        id: Date.now().toString(),
        name: formData.name.trim(),
        role: formData.role,
      };
      
      onCollaboratorsChange([...collaborators, newCollaborator]);
      resetForm();
      setIsAddDialogOpen(false);
    }
  };

  const handleEdit = (collaborator: Collaborator) => {
    setEditingCollaborator(collaborator);
    setFormData({
      name: collaborator.name,
      role: collaborator.role,
    });
  };

  const handleSaveEdit = () => {
    if (editingCollaborator && formData.name.trim()) {
      const updatedCollaborators = collaborators.map(c =>
        c.id === editingCollaborator.id
          ? {
              ...c,
              name: formData.name.trim(),
              role: formData.role,
            }
          : c
      );
      
      onCollaboratorsChange(updatedCollaborators);
      resetForm();
      setEditingCollaborator(null);
    }
  };

  const handleDelete = (id: string) => {
    onCollaboratorsChange(collaborators.filter(c => c.id !== id));
  };

  const handleCancel = () => {
    resetForm();
    setIsAddDialogOpen(false);
    setEditingCollaborator(null);
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="space-y-4">
      {/* Existing Collaborators */}
      {collaborators.length > 0 && (
        <div className="space-y-3">
          {collaborators.map((collaborator) => (
            <Card key={collaborator.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <span className="text-primary font-medium text-sm">
                        {getInitials(collaborator.name)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{collaborator.name}</p>
                      {collaborator.role.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {collaborator.role.map((role, index) => (
                            <span
                              key={index}
                              className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-md"
                            >
                              {role}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleEdit(collaborator)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(collaborator.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Collaborator Button */}
      <Button variant="outline" className="w-full" onClick={handleAddCollaborator}>
        <Plus className="h-4 w-4 mr-2" />
        Add Collaborator
      </Button>

      {/* Add Collaborator Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Collaborator</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="collaborator-name">Name *</Label>
              <Input
                id="collaborator-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter collaborator's name"
              />
            </div>
            
            <div className="space-y-2">
              <Label>Role</Label>
              <TagInput
                tags={formData.role}
                onTagsChange={(role) => setFormData({ ...formData, role })}
                placeholder="Add roles (e.g., Designer, Developer)"
                maxTags={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
            <Button onClick={handleAdd} disabled={!formData.name.trim()}>
              Add Collaborator
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Collaborator Dialog */}
      <Dialog open={!!editingCollaborator} onOpenChange={() => setEditingCollaborator(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Collaborator</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-collaborator-name">Name *</Label>
              <Input
                id="edit-collaborator-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter collaborator's name"
              />
            </div>
            
            <div className="space-y-2">
              <Label>Role</Label>
              <TagInput
                tags={formData.role}
                onTagsChange={(role) => setFormData({ ...formData, role })}
                placeholder="Add roles (e.g., Designer, Developer)"
                maxTags={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
            <Button onClick={handleSaveEdit} disabled={!formData.name.trim()}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}