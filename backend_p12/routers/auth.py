from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from dependencies.auth import (
    authenticate_user_by_email, 
    get_current_user, 
    get_db,
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    verify_refresh_token
)
from models.auth import AuthProviderType
from models.users import User
from schemas.auth import (
    EmailLoginRequest,
    EmailRegisterRequest,
    WeChatLoginRequest,
    SendVerificationCodeRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    AuthResponse,
    UserProfile,
    VerificationCodeResponse,
    TokenRefreshResponse
)
from services.auth_service import AuthService

router = APIRouter()

def create_user_profile(user: User, db: Session) -> UserProfile:
    """Helper to create UserProfile from User"""
    return UserProfile(
        id=getattr(user, 'id'),
        name=getattr(user, 'name'),
        bio=getattr(user, 'bio'),
        auth_methods=AuthService.get_user_auth_methods(db, getattr(user, 'id'))
    )

def get_user_attribute(user: User, attr: str):
    """Helper to safely get user attributes"""
    return getattr(user, attr)

def get_user_id(user: User) -> int:
    """Helper to extract user ID from SQLAlchemy model"""
    return getattr(user, 'id')

# Legacy endpoint for testing compatibility
@router.post("/token")
def legacy_login(user_id: int):
    """Legacy endpoint for testing - creates token for user ID"""
    access_token = create_access_token({"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Email/Password Authentication
@router.post("/register/email", response_model=AuthResponse)
def register_with_email(
    request: EmailRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user with email and password"""
    user, tokens = AuthService.register_user(
        db=db,
        provider_type=AuthProviderType.EMAIL,
        provider_id=request.email,
        name=request.name,
        bio=request.bio,
        password=request.password,
        verification_code=None  # For demo, skip verification
    )
    
    return AuthResponse(
        **tokens,
        user=create_user_profile(user, db)
    )

@router.post("/login/email", response_model=AuthResponse)
def login_with_email(
    request: EmailLoginRequest,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    user = authenticate_user_by_email(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(get_user_id(user))})
    refresh_token_str = create_refresh_token()
    store_refresh_token(db, get_user_id(user), refresh_token_str)
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=30 * 60,
        user=create_user_profile(user, db)
    )

# Verification Code System
@router.post("/send-verification-code", response_model=VerificationCodeResponse)
def send_verification_code(
    request: SendVerificationCodeRequest,
    db: Session = Depends(get_db)
):
    """Send verification code to email"""
    verification_code = AuthService.create_verification_code(
        db=db,
        provider_type=AuthProviderType(request.provider_type),
        provider_id=request.provider_id,
        purpose=request.purpose
    )
    
    # Send the email verification code
    code_value = getattr(verification_code, 'code')
    AuthService.send_email_verification(
        request.provider_id, 
        code_value, 
        request.purpose
    )
    
    return VerificationCodeResponse(
        message=f"Verification code sent to {request.provider_id}",
        expires_in=10 * 60  # 10 minutes
    )

# WeChat Authentication
@router.post("/login/wechat", response_model=AuthResponse)
def login_with_wechat(
    request: WeChatLoginRequest,
    db: Session = Depends(get_db)
):
    """Login or register with WeChat"""
    # Verify WeChat code and get user info
    wechat_data = AuthService.verify_wechat_code(request.wechat_code)
    if not wechat_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid WeChat authorization code"
        )
    
    openid = wechat_data['openid']
    
    # Check if user exists
    from dependencies.auth import get_user_by_auth_method
    user = get_user_by_auth_method(db, AuthProviderType.WECHAT, openid)
    
    if not user:
        # Register new user
        user_name = request.name or wechat_data.get('nickname', 'WeChat User')
        user, tokens = AuthService.register_user(
            db=db,
            provider_type=AuthProviderType.WECHAT,
            provider_id=openid,
            name=user_name,
            bio=request.bio,
            wechat_data=wechat_data
        )
    else:
        # Existing user login
        access_token = create_access_token(data={"sub": str(get_user_id(user))})
        refresh_token_str = create_refresh_token()
        store_refresh_token(db, get_user_id(user), refresh_token_str)
        
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
            "expires_in": 30 * 60
        }
    
    return AuthResponse(
        **tokens,
        user=create_user_profile(user, db)
    )

# Token Management
@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    refresh_token = verify_refresh_token(db, request.refresh_token)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Generate new access token
    access_token = create_access_token(data={"sub": str(refresh_token.user_id)})
    
    return TokenRefreshResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60
    )

@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user by revoking refresh token"""
    from dependencies.auth import revoke_refresh_token
    revoke_refresh_token(db, request.refresh_token)
    return {"message": "Successfully logged out"}

# User Profile
@router.get("/me", response_model=UserProfile)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    return create_user_profile(current_user, db)