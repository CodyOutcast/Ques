import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Search, Settings, Filter, Star } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "./ui/sheet";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { Checkbox } from "./ui/checkbox";
import { Slider } from "./ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import svgPaths from "../imports/svg-99bqa62khj";
// Placeholder card image URL
const imgCard = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=600&fit=crop";
import NevigationBar from "../imports/NevigationBar";

// Mock project data
const mockProjects = [
  {
    id: 1,
    title: "The Greatest Project In the World",
    description: "Revolutionary AI-powered platform for finding collaborator",
    creator: "Alex",
    collaborators: 3,
    image: imgCard,
    tags: ["AI", "Platform", "Collaboration"]
  },
  {
    id: 2,
    title: "EcoTrack: Sustainable Living App",
    description: "Track your carbon footprint and discover eco-friendly alternatives",
    creator: "Sarah",
    collaborators: 5,
    image: imgCard,
    tags: ["Environment", "Mobile", "Sustainability"]
  },
  {
    id: 3,
    title: "CodeMentor Network",
    description: "Connect developers with mentors for skill development",
    creator: "Mike",
    collaborators: 2,
    tags: ["Education", "Development", "Mentoring"]
  },
  {
    id: 4,
    title: "FoodShare Community",
    description: "Platform to share excess food and reduce waste",
    creator: "Emma",
    collaborators: 4,
    tags: ["Community", "Food", "Social Impact"]
  },
  {
    id: 5,
    title: "AR Shopping Experience",
    description: "Augmented reality platform for virtual product trials",
    creator: "David",
    collaborators: 6,
    tags: ["AR", "E-commerce", "Innovation"]
  },
  {
    id: 6,
    title: "MindfulMed: Mental Health Tracker",
    description: "AI-powered mental health monitoring and support system",
    creator: "Lisa",
    collaborators: 3,
    tags: ["Healthcare", "AI", "Mental Health"]
  }
];

const projectTags = ["AI", "Platform", "Collaboration", "Environment", "Mobile", "Sustainability", "Education", "Development", "Mentoring", "Community", "Food", "Social Impact", "AR", "E-commerce", "Innovation", "Healthcare", "Mental Health"];

function PopupButton() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-[3px] items-start justify-center leading-[0] px-0 py-[13px] relative shrink-0 text-left text-nowrap"
      data-name="Popup Button"
    >
      <div
        className="font-['Instrument_Sans:Bold_Italic',_sans-serif] font-bold italic relative shrink-0 text-[#0055f7] text-[40px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[9px] text-nowrap whitespace-pre">Ques</p>
      </div>
      <div
        className="css-r804ei flex flex-col font-['SF_Pro:Regular',_sans-serif] font-normal justify-center relative shrink-0 text-[#0088ff] text-[18px]"
        style={{ fontVariationSettings: "'wdth' 100" }}
      >
        <p className="block leading-[18px] text-nowrap whitespace-pre">􀆏</p>
      </div>
    </div>
  );
}



function UpperBar() {
  const [searchMode, setSearchMode] = useState("basic");
  const [distance, setDistance] = useState([50]);
  const [ageRange, setAgeRange] = useState([18, 65]);
  const [projectStatus, setProjectStatus] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [tagSearch, setTagSearch] = useState("");

  const handleStatusChange = (status: string, checked: boolean) => {
    if (checked) {
      setProjectStatus([...projectStatus, status]);
    } else {
      setProjectStatus(projectStatus.filter(s => s !== status));
    }
  };

  const handleTagToggle = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const filteredTags = projectTags.filter(tag => 
    tag.toLowerCase().includes(tagSearch.toLowerCase())
  );

  return (
    <div
      className="box-border content-stretch flex flex-col gap-2.5 h-[90px] items-center justify-center overflow-clip px-[19px] py-2 relative shrink-0"
      data-name="upper bar"
    >
      <div className="box-border content-stretch flex flex-row h-[52px] items-end justify-between p-0 relative shrink-0 w-[355px]">
        <PopupButton />
        <div className="box-border content-stretch flex flex-row items-center justify-start p-0 relative shrink-0 w-[81px]">
          {/* Settings Modal */}
          <Sheet>
            <SheetTrigger asChild>
              <button className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0 cursor-pointer hover:bg-gray-100">
                <Settings className="w-6 h-6 text-gray-600" />
              </button>
            </SheetTrigger>
            <SheetContent side="bottom" className="h-[400px]">
              <SheetHeader>
                <SheetTitle>Search Mode Settings</SheetTitle>
                <SheetDescription>
                  Choose your search mode to customize how Ques finds projects and collaborators.
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6 space-y-6">
                <div 
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                    searchMode === "basic" ? "border-blue-500 bg-blue-50" : "border-gray-200"
                  }`}
                  onClick={() => setSearchMode("basic")}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Basic Mode</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Search through projects and collaborators within the Ques platform
                      </p>
                    </div>
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      searchMode === "basic" ? "border-blue-500 bg-blue-500" : "border-gray-300"
                    }`} />
                  </div>
                </div>

                <div 
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                    searchMode === "multi-resources" ? "border-blue-500 bg-blue-50" : "border-gray-200"
                  }`}
                  onClick={() => setSearchMode("multi-resources")}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold">Multi-Resources Mode</h3>
                        <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                        <Badge variant="secondary" className="text-xs">PRO</Badge>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        Search across top platforms including GitHub, LinkedIn, and other professional networks
                      </p>
                    </div>
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      searchMode === "multi-resources" ? "border-blue-500 bg-blue-500" : "border-gray-300"
                    }`} />
                  </div>
                </div>

                <div className="pt-4">
                  <Button className="w-full" disabled={searchMode === "multi-resources"}>
                    {searchMode === "multi-resources" ? "Upgrade to Pro" : "Apply Settings"}
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>

          {/* Filter Modal */}
          <Sheet>
            <SheetTrigger asChild>
              <button className="box-border content-stretch flex flex-col items-center justify-center overflow-clip p-[8px] relative rounded-[100px] shrink-0 cursor-pointer hover:bg-gray-100">
                <Filter className="w-6 h-6 text-gray-600" />
              </button>
            </SheetTrigger>
            <SheetContent side="bottom" className="h-[600px] overflow-y-auto">
              <SheetHeader>
                <SheetTitle>Filter Options</SheetTitle>
                <SheetDescription>
                  Apply filters to narrow down your search results and find the perfect project matches.
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6 space-y-6">
                {/* Distance */}
                <div>
                  <label className="text-sm font-medium">Distance (km)</label>
                  <div className="mt-2">
                    <Slider
                      value={distance}
                      onValueChange={setDistance}
                      max={100}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>1 km</span>
                      <span>{distance[0]} km</span>
                      <span>100 km</span>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Age */}
                <div>
                  <label className="text-sm font-medium">Age Range</label>
                  <div className="mt-2">
                    <Slider
                      value={ageRange}
                      onValueChange={setAgeRange}
                      max={65}
                      min={18}
                      step={1}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>18</span>
                      <span>{ageRange[0]} - {ageRange[1]}</span>
                      <span>65</span>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Project Status */}
                <div>
                  <label className="text-sm font-medium mb-3 block">Project Status</label>
                  <div className="space-y-3">
                    {["not started", "on-going", "finished"].map((status) => (
                      <div key={status} className="flex items-center space-x-2">
                        <Checkbox
                          id={status}
                          checked={projectStatus.includes(status)}
                          onCheckedChange={(checked: boolean) => handleStatusChange(status, !!checked)}
                        />
                        <label htmlFor={status} className="text-sm capitalize">
                          {status}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator />

                {/* Project Types */}
                <div>
                  <label className="text-sm font-medium mb-3 block">Project Types</label>
                  <div className="space-y-3">
                    <Input
                      placeholder="Search tags..."
                      value={tagSearch}
                      onChange={(e) => setTagSearch(e.target.value)}
                      className="w-full"
                    />
                    <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
                      {filteredTags.map((tag) => (
                        <Badge
                          key={tag}
                          variant={selectedTags.includes(tag) ? "default" : "outline"}
                          className="cursor-pointer"
                          onClick={() => handleTagToggle(tag)}
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-4 sticky bottom-0 bg-white">
                  <Button className="w-full">Apply Filters</Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </div>
  );
}

interface ProjectCardProps {
  project: typeof mockProjects[0];
  index: number;
}

function ProjectCard({ project, index }: ProjectCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        duration: 0.6, 
        delay: index * 0.1,
        type: "spring",
        stiffness: 100,
        damping: 15
      }}
      className="bg-[position:0%_0%,_50%_50%] bg-size-[auto,cover] box-border content-stretch flex flex-col gap-2.5 h-[300px] items-center justify-end overflow-clip p-0 relative rounded-[14px] shadow-[0px_4px_14.4px_0px_rgba(0,0,0,0.25)] shrink-0 w-full"
      style={{ backgroundImage: `url('${project.image}')` }}
    >
      <div className="h-[120px] min-w-72 relative shrink-0 w-full">
        <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col gap-1 h-[120px] items-center justify-end min-w-inherit pb-6 pt-4 px-6 relative w-full">
          <div className="relative shrink-0 w-full">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
              <div className="css-ddnua5 font-['Inter:Bold',_sans-serif] font-bold leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[20px] text-left w-full">
                <p className="block leading-[24px]">{project.title}</p>
              </div>
            </div>
          </div>
          <div className="relative shrink-0 w-full">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
              <div className="css-ddnua5 font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[12px] text-left w-full">
                <p className="block leading-[18px] line-clamp-2">{project.description}</p>
              </div>
            </div>
          </div>
          <div className="relative shrink-0 w-full">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex flex-col items-start justify-start p-0 relative w-full">
              <div className="css-ddnua5 font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[14px] text-left w-full">
                <p className="leading-[20px]">
                  <span>{`By `}</span>
                  <span className="font-['Inter:Semi_Bold',_sans-serif] font-semibold not-italic">{project.creator}</span>
                  <span>{` · `}</span>
                  <span className="font-['Inter:Semi_Bold',_sans-serif] font-semibold not-italic">{project.collaborators}</span>
                  <span className="font-['Inter:Medium',_sans-serif] font-medium not-italic">{` collaborators`}</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function LoadingCard({ index }: { index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className="h-[300px] w-full rounded-[14px] bg-gray-200 animate-pulse"
    >
      <div className="h-full flex flex-col justify-end p-6">
        <div className="space-y-3">
          <div className="h-6 bg-gray-300 rounded w-3/4 animate-pulse"></div>
          <div className="h-4 bg-gray-300 rounded w-full animate-pulse"></div>
          <div className="h-4 bg-gray-300 rounded w-2/3 animate-pulse"></div>
        </div>
      </div>
    </motion.div>
  );
}

export default function AISearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<typeof mockProjects>([]);
  const [userMessage, setUserMessage] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setUserMessage(searchQuery);
    setIsLoading(true);
    setHasSearched(true);
    setSearchResults([]);

    // Simulate API call
    setTimeout(() => {
      // Filter projects based on search query (simple mock)
      const filtered = mockProjects.filter(
        (project) =>
          project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          project.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      
      // If no matches, show all projects as AI suggestions
      const results = filtered.length > 0 ? filtered : mockProjects.slice(0, 6);
      
      setSearchResults(results);
      setIsLoading(false);
      setSearchQuery("");
    }, 2000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="relative size-full bg-white overflow-hidden">
      <UpperBar />
      
      <div className="flex-1 overflow-hidden px-4" style={{ height: 'calc(100vh - 90px - 96px - 96px)' }}>
        <AnimatePresence>
          {hasSearched && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500"
            >
              <p className="text-gray-700">
                <span className="text-blue-600">You searched for:</span> "{userMessage}"
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="h-full overflow-y-auto">
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-8">
              {Array.from({ length: 6 }).map((_, index) => (
                <LoadingCard key={index} index={index} />
              ))}
            </div>
          ) : searchResults.length > 0 ? (
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {searchResults.map((project, index) => (
                <ProjectCard key={project.id} project={project} index={index} />
              ))}
            </motion.div>
          ) : hasSearched ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-full text-gray-500"
            >
              <Search size={48} className="mb-4 text-gray-300" />
              <p>No projects found. Try a different search term.</p>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-full text-gray-500"
            >
              <Search size={48} className="mb-4 text-gray-300" />
              <h3 className="text-xl mb-2">AI Project Search</h3>
              <p className="text-center max-w-md">
                Describe what kind of project or collaborator you're looking for, and our AI will find the perfect matches.
              </p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Search Bar */}
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="absolute bg-white border-t border-gray-200 p-6 shadow-lg"
        style={{ bottom: '96px', left: 0, right: 0, height: '96px' }}
      >
        <div className="flex items-center gap-3 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask AI to find projects or collaborators..."
              className="pr-12 h-12 rounded-full border-2 border-gray-200 bg-gray-50 focus-visible:!border-blue-500 focus-visible:!ring-2 focus-visible:!ring-blue-500/20 focus-visible:!ring-offset-0"
              disabled={isLoading}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <Search size={20} className="text-gray-400" />
            </div>
          </div>
          <Button
            onClick={handleSearch}
            disabled={!searchQuery.trim() || isLoading}
            className="h-12 w-12 rounded-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center"
          >
            {isLoading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
              />
            ) : (
              <Send size={20} />
            )}
          </Button>
        </div>
      </motion.div>

      {/* Navigation Bar */}
      <div className="absolute bottom-0 left-0 right-0" style={{ height: '96px' }}>
        <NevigationBar />
      </div>
    </div>
  );
}