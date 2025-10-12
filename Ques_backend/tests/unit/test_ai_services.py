"""
Unit tests for the AI Services router
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from routers.ai_services import analyze_profile_completion, ProfileCompletionSuggestion


class TestAIProfileAnalysis:
    """Test cases for AI profile analysis functionality"""
    
    def test_analyze_complete_profile(self):
        """Test analysis of a complete profile"""
        # Mock complete profile
        complete_profile = Mock()
        complete_profile.profile_photo = "avatar.jpg"
        complete_profile.name = "John Doe"
        complete_profile.age = 25
        complete_profile.gender = "male"
        complete_profile.location = "Shenzhen"
        complete_profile.one_sentence_intro = "Passionate developer building the future"
        complete_profile.hobbies = ["coding", "gaming", "travel"]
        complete_profile.languages = ["English", "Chinese"]
        complete_profile.skills = ["Python", "JavaScript", "React"]
        complete_profile.resources = ["funding", "network", "expertise"]
        complete_profile.goals = "Building innovative mobile apps that solve real problems"
        complete_profile.demands = ["co-founder", "funding"]
        complete_profile.current_university = "SZU"
        complete_profile.university_verified = True
        complete_profile.wechat_id = "john_dev"
        complete_profile.wechat_verified = True
        
        # Run analysis
        results = analyze_profile_completion(complete_profile)
        
        # Assertions
        assert results['completion_percentage'] == 100.0
        assert len(results['critical_missing']) == 0
        assert len(results['suggestions']) == 0
        assert len(results['strengths']) > 0
        assert "Excellent profile" in results['overall_assessment']
    
    def test_analyze_incomplete_profile(self):
        """Test analysis of an incomplete profile"""
        # Mock incomplete profile - missing avatar and resources
        incomplete_profile = Mock()
        incomplete_profile.profile_photo = None  # Missing
        incomplete_profile.name = "Jane Doe"
        incomplete_profile.age = 22
        incomplete_profile.gender = "female"
        incomplete_profile.location = "Beijing"
        incomplete_profile.one_sentence_intro = "Student learning web development"
        incomplete_profile.hobbies = ["reading"]
        incomplete_profile.languages = ["English"]
        incomplete_profile.skills = ["HTML", "CSS"]
        incomplete_profile.resources = []  # Missing
        incomplete_profile.goals = "Learn programming"  # Too short
        incomplete_profile.demands = []
        incomplete_profile.current_university = "PKU"
        incomplete_profile.university_verified = False
        incomplete_profile.wechat_id = None
        incomplete_profile.wechat_verified = False
        
        # Run analysis
        results = analyze_profile_completion(incomplete_profile)
        
        # Assertions
        assert results['completion_percentage'] < 100.0
        assert 'avatar' in results['critical_missing']
        assert 'resources' in results['critical_missing']
        assert len(results['suggestions']) > 0
        
        # Check suggestions contain expected fields
        suggestion_fields = [s.field for s in results['suggestions']]
        assert 'avatar' in suggestion_fields
        assert 'resources' in suggestion_fields
    
    def test_analyze_minimal_profile(self):
        """Test analysis of a minimal profile with only basic info"""
        # Mock minimal profile
        minimal_profile = Mock()
        minimal_profile.profile_photo = None
        minimal_profile.name = "Min User"
        minimal_profile.age = None
        minimal_profile.gender = None
        minimal_profile.location = None
        minimal_profile.one_sentence_intro = None
        minimal_profile.hobbies = None
        minimal_profile.languages = None
        minimal_profile.skills = None
        minimal_profile.resources = None
        minimal_profile.goals = None
        minimal_profile.demands = None
        minimal_profile.current_university = None
        minimal_profile.university_verified = False
        minimal_profile.wechat_id = None
        minimal_profile.wechat_verified = False
        
        # Run analysis
        results = analyze_profile_completion(minimal_profile)
        
        # Assertions
        assert results['completion_percentage'] < 50.0
        assert len(results['critical_missing']) > 3
        assert len(results['suggestions']) > 3
        assert "Incomplete profile" in results['overall_assessment']


class TestAIServicesEndpoints:
    """Test cases for AI Services API endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_profile_analysis_success(self, client, auth_headers):
        """Test successful profile analysis endpoint"""
        with patch('routers.ai_services.analyze_profile_completion') as mock_analyze:
            mock_analyze.return_value = {
                'completion_percentage': 75.5,
                'overall_assessment': 'Good profile',
                'suggestions': [],
                'strengths': ['Clear goals'],
                'critical_missing': ['avatar'],
                'ai_reasoning': 'Test reasoning'
            }
            
            response = client.get("/api/v1/ai/profile-analysis", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data['completion_percentage'] == 75.5
            assert data['overall_assessment'] == 'Good profile'
            assert 'ai_reasoning' in data
    
    def test_get_profile_analysis_unauthorized(self, client):
        """Test profile analysis endpoint without authentication"""
        response = client.get("/api/v1/ai/profile-analysis")
        assert response.status_code == 401
    
    @pytest.mark.asyncio 
    async def test_post_profile_analysis_success(self, client, auth_headers):
        """Test POST profile analysis endpoint"""
        request_data = {"user_id": None}  # Analyze current user
        
        with patch('routers.ai_services.analyze_profile_completion') as mock_analyze:
            mock_analyze.return_value = {
                'completion_percentage': 85.0,
                'overall_assessment': 'Very good profile',
                'suggestions': [],
                'strengths': ['Strong skills'],
                'critical_missing': [],
                'ai_reasoning': 'Complete profile with good content'
            }
            
            response = client.post(
                "/api/v1/ai/profile-analysis", 
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['completion_percentage'] == 85.0
    
    @pytest.mark.asyncio
    async def test_get_profile_suggestions_success(self, client, auth_headers):
        """Test profile suggestions endpoint"""
        with patch('routers.ai_services.analyze_profile_completion') as mock_analyze:
            mock_analyze.return_value = {
                'suggestions': [
                    ProfileCompletionSuggestion(
                        field='avatar',
                        priority='critical',
                        suggestion='Add a professional photo',
                        impact='Increases trust and match rates'
                    )
                ]
            }
            
            response = client.get("/api/v1/ai/profile-suggestions", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert data[0]['field'] == 'avatar'
            assert data[0]['priority'] == 'critical'


class TestProfileCompletionSuggestion:
    """Test cases for ProfileCompletionSuggestion model"""
    
    def test_suggestion_model_creation(self):
        """Test creation of suggestion model"""
        suggestion = ProfileCompletionSuggestion(
            field="avatar",
            priority="critical", 
            suggestion="Add a professional photo",
            impact="Increases match rates by 70%"
        )
        
        assert suggestion.field == "avatar"
        assert suggestion.priority == "critical"
        assert suggestion.suggestion == "Add a professional photo"
        assert suggestion.impact == "Increases match rates by 70%"
    
    def test_suggestion_model_validation(self):
        """Test validation of suggestion model"""
        # Test with missing required field
        with pytest.raises(ValueError):
            ProfileCompletionSuggestion(
                field="",  # Empty field should fail validation
                priority="critical",
                suggestion="Test suggestion",
                impact="Test impact"
            )