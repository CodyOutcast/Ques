import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Slider } from '../ui/slider';
import { TagInput } from './TagInput';
import { CollaboratorInput } from './CollaboratorInput';
import { LinkInput } from './LinkInput';

interface ProjectData {
  title: string;
  shortDescription: string;
  media: File[];
  projectTags: string[];
  ownRole: string[];
  collaborators: Array<{
    id: string;
    name: string;
    role: string[];
  }>;
  startTime: string;
  currentProgress: number;
  detailedDescription: string;
  purpose: string;
  whatWeAreDoing: string;
  peopleLookingFor: string;
  lookingForTags: string[];
  links: string[];
}

interface ProjectFormProps {
  projectData: ProjectData;
  onProjectDataChange: (data: ProjectData) => void;
  onSubmit: () => void;
  isSubmitting: boolean;
}

export function ProjectForm({ projectData, onProjectDataChange, onSubmit, isSubmitting }: ProjectFormProps) {
  const [titleWordCount, setTitleWordCount] = useState(0);

  const updateProjectData = (field: keyof ProjectData, value: any) => {
    onProjectDataChange({
      ...projectData,
      [field]: value,
    });
  };

  const handleTitleChange = (value: string) => {
    // Count words/characters for bilingual support
    const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0;
    const charCount = value.length;
    
    // Limit to 10 words or 20 characters
    if (wordCount <= 10 && charCount <= 20) {
      setTitleWordCount(wordCount);
      updateProjectData('title', value);
    }
  };

  const isFormValid = () => {
    return projectData.title.trim() && 
           projectData.shortDescription.trim() && 
           projectData.ownRole.length > 0 &&
           projectData.startTime &&
           projectData.detailedDescription.trim() &&
           projectData.purpose.trim() &&
           projectData.whatWeAreDoing.trim() &&
           projectData.peopleLookingFor.trim();
  };

  return (
    <div className="p-4 space-y-6 pb-24">
      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title" className="text-lg font-bold">Project Title *</Label>
        <Input
          id="title"
          value={projectData.title}
          onChange={(e) => handleTitleChange(e.target.value)}
          placeholder="Enter project title (max 10 words or 20 characters)"
          className="w-full"
        />
        <p className="text-sm text-muted-foreground">
          {titleWordCount}/10 words, {projectData.title.length}/20 characters
        </p>
      </div>

      {/* Short Description */}
      <div className="space-y-2">
        <Label htmlFor="shortDescription" className="text-lg font-bold">Short Description *</Label>
        <Textarea
          id="shortDescription"
          value={projectData.shortDescription}
          onChange={(e) => updateProjectData('shortDescription', e.target.value)}
          placeholder="Brief description of your project"
          rows={3}
        />
      </div>

      {/* Project Tags */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Project Tags</Label>
        <TagInput
          tags={projectData.projectTags}
          onTagsChange={(tags) => updateProjectData('projectTags', tags)}
          placeholder="Add project tags..."
        />
      </div>

      {/* Your Role */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Your Role *</Label>
        <TagInput
          tags={projectData.ownRole}
          onTagsChange={(tags) => updateProjectData('ownRole', tags)}
          placeholder="Add your roles..."
        />
      </div>

      {/* Start Time */}
      <div className="space-y-2">
        <Label htmlFor="startTime" className="text-lg font-bold">Start Time *</Label>
        <Input
          id="startTime"
          type="date"
          value={projectData.startTime}
          onChange={(e) => updateProjectData('startTime', e.target.value)}
          className="w-full"
        />
      </div>

      {/* Current Progress */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Current Progress: {projectData.currentProgress}%</Label>
        <Slider
          value={[projectData.currentProgress]}
          onValueChange={([value]) => updateProjectData('currentProgress', value)}
          max={100}
          step={5}
          className="w-full"
        />
      </div>

      {/* Detailed Description */}
      <div className="space-y-2">
        <Label htmlFor="detailedDescription" className="text-lg font-bold">Detailed Description *</Label>
        <Textarea
          id="detailedDescription"
          value={projectData.detailedDescription}
          onChange={(e) => updateProjectData('detailedDescription', e.target.value)}
          placeholder="Provide a detailed description of your project"
          rows={4}
        />
      </div>

      {/* Purpose */}
      <div className="space-y-2">
        <Label htmlFor="purpose" className="text-lg font-bold">Project Purpose *</Label>
        <Textarea
          id="purpose"
          value={projectData.purpose}
          onChange={(e) => updateProjectData('purpose', e.target.value)}
          placeholder="What is the main purpose of this project?"
          rows={3}
        />
      </div>

      {/* What We Are Doing */}
      <div className="space-y-2">
        <Label htmlFor="whatWeAreDoing" className="text-lg font-bold">What We Are Building *</Label>
        <Textarea
          id="whatWeAreDoing"
          value={projectData.whatWeAreDoing}
          onChange={(e) => updateProjectData('whatWeAreDoing', e.target.value)}
          placeholder="Describe what you are building or working on"
          rows={3}
        />
      </div>

      {/* People Looking For */}
      <div className="space-y-2">
        <Label htmlFor="peopleLookingFor" className="text-lg font-bold">People We're Looking For *</Label>
        <Textarea
          id="peopleLookingFor"
          value={projectData.peopleLookingFor}
          onChange={(e) => updateProjectData('peopleLookingFor', e.target.value)}
          placeholder="Describe the people you're looking for"
          rows={3}
        />
      </div>

      {/* Looking For Tags */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Skills/Roles Needed</Label>
        <TagInput
          tags={projectData.lookingForTags}
          onTagsChange={(tags) => updateProjectData('lookingForTags', tags)}
          placeholder="Add required skills or roles..."
        />
      </div>

      {/* Collaborators */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Current Collaborators</Label>
        <CollaboratorInput
          collaborators={projectData.collaborators}
          onCollaboratorsChange={(collaborators) => updateProjectData('collaborators', collaborators)}
        />
      </div>

      {/* Links */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Project Links</Label>
        <LinkInput
          links={projectData.links}
          onLinksChange={(links) => updateProjectData('links', links)}
        />
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <Button
          onClick={onSubmit}
          disabled={!isFormValid() || isSubmitting}
          className="w-full"
          size="lg"
        >
          {isSubmitting ? 'Publishing...' : 'Publish Project'}
        </Button>
      </div>
    </div>
  );
} 