import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Slider } from './ui/slider';
import { MediaUpload } from './MediaUpload';
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

      {/* Media Upload */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Media (Optional)</Label>
        <MediaUpload
          files={projectData.media}
          onFilesChange={(files) => updateProjectData('media', files)}
          maxFiles={9}
        />
      </div>

      {/* Project Tags */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Project Tags</Label>
        <TagInput
          tags={projectData.projectTags}
          onTagsChange={(tags) => updateProjectData('projectTags', tags)}
          placeholder="Add project tags (e.g., Web Development, Mobile App)"
          maxTags={3}
        />
      </div>

      {/* Your Role */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Your Role *</Label>
        <TagInput
          tags={projectData.ownRole}
          onTagsChange={(tags) => updateProjectData('ownRole', tags)}
          placeholder="Add your role (e.g., Frontend Developer, Designer)"
          maxTags={3}
        />
      </div>

      {/* Collaborators */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-bold">Collaborators</CardTitle>
        </CardHeader>
        <CardContent>
          <CollaboratorInput
            collaborators={projectData.collaborators}
            onCollaboratorsChange={(collaborators) => updateProjectData('collaborators', collaborators)}
          />
        </CardContent>
      </Card>

      {/* Start Time */}
      <div className="space-y-2">
        <Label htmlFor="startTime" className="text-lg font-bold">Start Time *</Label>
        <Input
          id="startTime"
          type="date"
          placeholder="yyyy/mm/dd"
          value={projectData.startTime}
          onChange={(e) => updateProjectData('startTime', e.target.value)}
        />
      </div>

      {/* Current Progress */}
      <div className="space-y-4">
        <Label className="text-lg font-bold">Current Progress: {projectData.currentProgress}%</Label>
        <Slider
          value={[projectData.currentProgress]}
          onValueChange={(value) => updateProjectData('currentProgress', value[0])}
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
          placeholder="Detailed description of your project, goals, and requirements"
          rows={6}
        />
      </div>

      {/* Purpose */}
      <div className="space-y-2">
        <Label htmlFor="purpose" className="text-lg font-bold">Purpose *</Label>
        <Textarea
          id="purpose"
          value={projectData.purpose}
          onChange={(e) => updateProjectData('purpose', e.target.value)}
          placeholder="What is the purpose and goal of this project?"
          rows={3}
        />
      </div>

      {/* What We're Doing Now */}
      <div className="space-y-2">
        <Label htmlFor="whatWeAreDoing" className="text-lg font-bold">What We're Doing Now *</Label>
        <Textarea
          id="whatWeAreDoing"
          value={projectData.whatWeAreDoing}
          onChange={(e) => updateProjectData('whatWeAreDoing', e.target.value)}
          placeholder="Current activities and progress on the project"
          rows={3}
        />
      </div>

      {/* People Looking For */}
      <div className="space-y-2">
        <Label htmlFor="peopleLookingFor" className="text-lg font-bold">People We're Looking For *</Label>
        
        {/* Tags for Looking For */}
        <div className="space-y-2">
          <Label className="text-base">Skills & Roles Needed</Label>
          <TagInput
            tags={projectData.lookingForTags || []}
            onTagsChange={(tags) => updateProjectData('lookingForTags', tags)}
            placeholder="Add skills/roles (e.g., UI Designer, React Developer)"
            maxTags={5}
          />
        </div>
        
        <Textarea
          id="peopleLookingFor"
          value={projectData.peopleLookingFor}
          onChange={(e) => updateProjectData('peopleLookingFor', e.target.value)}
          placeholder="Additional details about the collaborators you're looking for..."
          rows={3}
        />
      </div>

      {/* Links */}
      <div className="space-y-2">
        <Label className="text-lg font-bold">Project Links (Optional)</Label>
        <LinkInput
          links={projectData.links}
          onLinksChange={(links) => updateProjectData('links', links)}
        />
      </div>

      {/* Submit Button */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-card/95 backdrop-blur-sm border-t border-border shadow-lg">
        <Button
          onClick={onSubmit}
          disabled={!isFormValid() || isSubmitting}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg transition-all duration-200 hover:shadow-xl"
          size="lg"
        >
          {isSubmitting ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-foreground/30 border-t-primary-foreground"></div>
              <span>Posting Project...</span>
            </div>
          ) : (
            'Post Project'
          )}
        </Button>
      </div>
    </div>
  );
}