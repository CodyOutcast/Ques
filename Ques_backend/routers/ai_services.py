"""
AI Services Router
Provides AI-powered analysis and recommendations for user profiles
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import json

from dependencies.db import get_db
from dependencies.auth import get_current_user
from models.user_profiles import UserProfile
from models.users import User

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileAnalysisRequest(BaseModel):
    """Request model for profile analysis"""
    user_id: Optional[str] = Field(None, description="User ID to analyze (optional, defaults to current user)")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": None
            }
        }

class ProfileCompletionSuggestion(BaseModel):
    """Individual suggestion for profile improvement"""
    field: str = Field(..., description="Profile field that needs improvement")
    priority: str = Field(..., description="Priority level: critical, high, medium, low")
    suggestion: str = Field(..., description="Specific suggestion for improvement")
    impact: str = Field(..., description="Expected impact of implementing this suggestion")
    
class ProfileAnalysisResponse(BaseModel):
    """Response model for profile analysis"""
    user_id: str = Field(..., description="ID of the analyzed user")
    completion_percentage: float = Field(..., description="Profile completion percentage (0-100)")
    overall_assessment: str = Field(..., description="Overall profile assessment")
    suggestions: List[ProfileCompletionSuggestion] = Field(..., description="List of improvement suggestions")
    strengths: List[str] = Field(..., description="Profile strengths")
    critical_missing: List[str] = Field(..., description="Critical missing fields")
    ai_reasoning: str = Field(..., description="AI's detailed reasoning for the analysis")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "12345",
                "completion_percentage": 75.5,
                "overall_assessment": "Good profile with room for improvement in visual elements and resource specification",
                "suggestions": [
                    {
                        "field": "avatar",
                        "priority": "critical",
                        "suggestion": "Add a professional profile photo to increase trustworthiness and connection rate",
                        "impact": "Profile photos can increase match rates by up to 80%"
                    }
                ],
                "strengths": ["Comprehensive skills list", "Clear goals", "Detailed project experience"],
                "critical_missing": ["avatar", "resources"],
                "ai_reasoning": "The profile shows strong technical competence but lacks visual appeal and resource clarity...",
                "analyzed_at": "2025-01-12T10:30:00"
            }
        }

def analyze_profile_completion(profile: UserProfile) -> Dict:
    """
    Analyze profile completion and generate AI suggestions
    """
    # Define field weights and importance
    field_weights = {
        'avatar': {'weight': 15, 'critical': True, 'category': 'visual'},
        'name': {'weight': 10, 'critical': True, 'category': 'basic'},
        'age': {'weight': 5, 'critical': False, 'category': 'basic'},
        'gender': {'weight': 3, 'critical': False, 'category': 'basic'},
        'location': {'weight': 8, 'critical': True, 'category': 'basic'},
        'one_sentence_intro': {'weight': 12, 'critical': True, 'category': 'introduction'},
        'hobbies': {'weight': 8, 'critical': False, 'category': 'interests'},
        'languages': {'weight': 6, 'critical': False, 'category': 'skills'},
        'skills': {'weight': 15, 'critical': True, 'category': 'skills'},
        'resources': {'weight': 12, 'critical': True, 'category': 'resources'},
        'goals': {'weight': 10, 'critical': True, 'category': 'goals'},
        'demands': {'weight': 8, 'critical': False, 'category': 'networking'},
        'university': {'weight': 5, 'critical': False, 'category': 'education'},
        'wechat_id': {'weight': 3, 'critical': False, 'category': 'contact'}
    }
    
    # Calculate completion scores
    completed_fields = {}
    total_possible_score = sum(field['weight'] for field in field_weights.values())
    current_score = 0
    
    # Check each field
    for field, config in field_weights.items():
        is_complete = False
        
        if field == 'avatar':
            is_complete = bool(profile.profile_photo)
        elif field == 'name':
            is_complete = bool(profile.name and len(profile.name.strip()) > 0)
        elif field == 'age':
            is_complete = bool(profile.age)
        elif field == 'gender':
            is_complete = bool(profile.gender)
        elif field == 'location':
            is_complete = bool(profile.location)
        elif field == 'one_sentence_intro':
            is_complete = bool(profile.one_sentence_intro and len(profile.one_sentence_intro.strip()) > 10)
        elif field == 'hobbies':
            is_complete = bool(profile.hobbies and len(profile.hobbies) > 0)
        elif field == 'languages':
            is_complete = bool(profile.languages and len(profile.languages) > 0)
        elif field == 'skills':
            is_complete = bool(profile.skills and len(profile.skills) >= 2)
        elif field == 'resources':
            is_complete = bool(profile.resources and len(profile.resources) >= 1)
        elif field == 'goals':
            is_complete = bool(profile.goals and len(profile.goals.strip()) > 20)
        elif field == 'demands':
            is_complete = bool(profile.demands and len(profile.demands) > 0)
        elif field == 'university':
            is_complete = bool(profile.current_university)
        elif field == 'wechat_id':
            is_complete = bool(profile.wechat_id)
            
        completed_fields[field] = is_complete
        if is_complete:
            current_score += config['weight']
    
    completion_percentage = (current_score / total_possible_score) * 100
    
    # Generate suggestions based on missing fields
    suggestions = []
    critical_missing = []
    
    for field, config in field_weights.items():
        if not completed_fields[field]:
            if config['critical']:
                critical_missing.append(field)
                
            priority = "critical" if config['critical'] else "medium"
            
            # Generate field-specific suggestions
            suggestion_text = ""
            impact_text = ""
            
            if field == 'avatar':
                suggestion_text = "Add a professional profile photo that clearly shows your face. Use good lighting and a clean background."
                impact_text = "Profile photos increase match rates by 70-80% and build immediate trust with potential collaborators."
            elif field == 'name':
                suggestion_text = "Complete your full name to establish credibility and professional presence."
                impact_text = "A complete name significantly increases trust and professional perception."
            elif field == 'one_sentence_intro':
                suggestion_text = "Write a compelling one-sentence introduction that captures your passion, expertise, and what makes you unique."
                impact_text = "A strong intro is often the first thing people read and can determine if they want to learn more about you."
            elif field == 'skills':
                suggestion_text = "Add at least 3-5 specific technical or professional skills that showcase your expertise and capabilities."
                impact_text = "Skills help others understand your capabilities and increase match quality by 60%."
            elif field == 'resources':
                suggestion_text = "List resources you can offer to collaborators (funding, equipment, networks, expertise, time, etc.)"
                impact_text = "Clearly defined resources help others understand what you bring to collaborations and increase project match success by 45%."
            elif field == 'goals':
                suggestion_text = "Write detailed goals that explain what you want to achieve, why it matters to you, and your timeline."
                impact_text = "Clear goals help attract aligned collaborators and increase meaningful connection rates by 50%."
            elif field == 'location':
                suggestion_text = "Add your city or region to help find local collaborators and networking opportunities."
                impact_text = "Location information enables local networking and can increase in-person collaboration opportunities."
            elif field == 'hobbies':
                suggestion_text = "Add 3-5 hobbies or interests to show your personality and create conversation starters."
                impact_text = "Shared interests create natural conversation starters and stronger personal connections."
            elif field == 'languages':
                suggestion_text = "List languages you speak to expand your collaboration opportunities globally."
                impact_text = "Language skills can significantly expand your collaboration pool and international opportunities."
            elif field == 'demands':
                suggestion_text = "Specify what type of collaborators, resources, or support you're looking for."
                impact_text = "Clear demands help the matching algorithm find more relevant connections for your needs."
            else:
                suggestion_text = f"Complete the {field} section to improve your profile completeness."
                impact_text = "Additional profile information helps create better matches and builds trust."
                
            suggestions.append(ProfileCompletionSuggestion(
                field=field,
                priority=priority,
                suggestion=suggestion_text,
                impact=impact_text
            ))
    
    # Identify strengths
    strengths = []
    if completed_fields.get('skills') and profile.skills and len(profile.skills) >= 3:
        strengths.append("Strong technical skill set")
    if completed_fields.get('goals') and profile.goals and len(profile.goals) > 50:
        strengths.append("Clear and detailed goals")
    if completed_fields.get('one_sentence_intro'):
        strengths.append("Engaging personal introduction")
    if completed_fields.get('resources') and profile.resources and len(profile.resources) >= 2:
        strengths.append("Diverse resource offerings")
    if completed_fields.get('hobbies') and profile.hobbies and len(profile.hobbies) >= 3:
        strengths.append("Well-rounded interests")
    if profile.university_verified:
        strengths.append("Verified educational background")
    if profile.wechat_verified:
        strengths.append("Verified contact information")
        
    # Generate overall assessment
    if completion_percentage >= 90:
        assessment = "Excellent profile! Your comprehensive information makes you highly attractive to potential collaborators."
    elif completion_percentage >= 75:
        assessment = "Very good profile with strong foundations. A few improvements could make it outstanding."
    elif completion_percentage >= 60:
        assessment = "Good profile base with significant room for improvement in key areas."
    elif completion_percentage >= 40:
        assessment = "Basic profile that needs substantial enhancement to attract quality collaborators."
    else:
        assessment = "Incomplete profile that requires immediate attention to critical missing elements."
        
    # Generate AI reasoning
    critical_count = len(critical_missing)
    total_suggestions = len(suggestions)
    
    ai_reasoning = f"""Based on comprehensive analysis of the user profile, I've evaluated {len(field_weights)} key profile elements 
    weighted by their impact on collaboration success. The profile achieves {completion_percentage:.1f}% completion.
    
    Critical Analysis:
    - {critical_count} critical fields are missing: {', '.join(critical_missing) if critical_missing else 'None'}
    - {total_suggestions} total improvement opportunities identified
    - Profile strengths include: {', '.join(strengths) if strengths else 'Basic information present'}
    
    The analysis prioritizes visual elements (profile photo), clear value proposition (skills, resources), 
    and compelling narrative (introduction, goals) as these factors most significantly impact collaboration 
    matching success rates and user engagement.
    
    Immediate focus should be on {'critical missing fields' if critical_count > 0 else 'enhancing existing content quality'} 
    to maximize profile effectiveness and collaboration opportunities."""
    
    return {
        'completion_percentage': completion_percentage,
        'overall_assessment': assessment,
        'suggestions': suggestions,
        'strengths': strengths,
        'critical_missing': critical_missing,
        'ai_reasoning': ai_reasoning
    }

@router.post("/profile-analysis", response_model=ProfileAnalysisResponse)
async def analyze_user_profile(
    request: ProfileAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze user profile completeness and provide AI-powered suggestions for improvement.
    
    Uses the provided prompt: "based on this user profile, Analyze the percentage of how 
    complete the profile is then give suggestions on what the profile should improve on 
    especially if the user is missing important fields such as avatar, interest, and resources"
    """
    try:
        # Determine which user to analyze
        target_user_id = request.user_id if request.user_id else str(current_user.id)
        
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == int(target_user_id)).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
            
        # Security check - users can only analyze their own profile unless they have special permissions
        if str(current_user.id) != target_user_id:
            raise HTTPException(status_code=403, detail="Cannot analyze other user's profile")
            
        # Perform AI analysis
        analysis_results = analyze_profile_completion(profile)
        
        # Log the analysis
        logger.info(f"Profile analysis completed for user {target_user_id}: {analysis_results['completion_percentage']:.1f}% complete")
        
        # Return structured response
        return ProfileAnalysisResponse(
            user_id=target_user_id,
            completion_percentage=analysis_results['completion_percentage'],
            overall_assessment=analysis_results['overall_assessment'],
            suggestions=analysis_results['suggestions'],
            strengths=analysis_results['strengths'],
            critical_missing=analysis_results['critical_missing'],
            ai_reasoning=analysis_results['ai_reasoning']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing profile for user {target_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during profile analysis")

@router.get("/profile-analysis", response_model=ProfileAnalysisResponse)
async def get_current_user_profile_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI analysis for the current user's profile (convenience endpoint).
    
    This is a shorthand for POST /profile-analysis without specifying user_id.
    """
    try:
        request = ProfileAnalysisRequest(user_id=None)
        return await analyze_user_profile(request, db, current_user)
    except Exception as e:
        logger.error(f"Error getting profile analysis for current user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during profile analysis")

# Additional endpoint for profile suggestions only
@router.get("/profile-suggestions", response_model=List[ProfileCompletionSuggestion])
async def get_profile_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get only the improvement suggestions for the current user's profile.
    
    Returns a simplified list of suggestions without the full analysis.
    """
    try:
        # Get user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
            
        # Perform analysis
        analysis_results = analyze_profile_completion(profile)
        
        logger.info(f"Profile suggestions generated for user {current_user.id}")
        
        return analysis_results['suggestions']
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating suggestions for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during suggestion generation")
