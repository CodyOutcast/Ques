"""
Advanced error handling and standardized response system
"""
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """Standardized error codes for the application"""
    
    # Authentication errors (1000-1099)
    INVALID_CREDENTIALS = ("AUTH_001", "Invalid email or password")
    TOKEN_EXPIRED = ("AUTH_002", "Authentication token has expired")
    TOKEN_INVALID = ("AUTH_003", "Invalid authentication token")
    INSUFFICIENT_PERMISSIONS = ("AUTH_004", "Insufficient permissions for this action")
    EMAIL_NOT_VERIFIED = ("AUTH_005", "Email address not verified")
    
    # User errors (1100-1199)
    USER_NOT_FOUND = ("USER_001", "User not found")
    USER_ALREADY_EXISTS = ("USER_002", "User with this email already exists")
    INVALID_USER_DATA = ("USER_003", "Invalid user data provided")
    USER_INACTIVE = ("USER_004", "User account is inactive")
    
    # Profile errors (1200-1299)
    PROFILE_NOT_FOUND = ("PROFILE_001", "Profile not found")
    INVALID_PROFILE_DATA = ("PROFILE_002", "Invalid profile data")
    PROFILE_INCOMPLETE = ("PROFILE_003", "Profile is incomplete")
    
    # Matching errors (1300-1399)
    ALREADY_LIKED = ("MATCH_001", "You have already liked this user")
    CANNOT_LIKE_SELF = ("MATCH_002", "Cannot like your own profile")
    MATCH_NOT_FOUND = ("MATCH_003", "Match not found")
    
    # Email errors (1400-1499)
    EMAIL_SEND_FAILED = ("EMAIL_001", "Failed to send email")
    VERIFICATION_CODE_EXPIRED = ("EMAIL_002", "Verification code has expired")
    INVALID_VERIFICATION_CODE = ("EMAIL_003", "Invalid verification code")
    
    # Database errors (1500-1599)
    DATABASE_ERROR = ("DB_001", "Database operation failed")
    RECORD_NOT_FOUND = ("DB_002", "Record not found")
    DUPLICATE_RECORD = ("DB_003", "Record already exists")
    
    # File/Upload errors (1600-1699)
    FILE_TOO_LARGE = ("FILE_001", "File size exceeds maximum limit")
    INVALID_FILE_TYPE = ("FILE_002", "Invalid file type")
    UPLOAD_FAILED = ("FILE_003", "File upload failed")
    
    # Rate limiting errors (1700-1799)
    RATE_LIMIT_EXCEEDED = ("RATE_001", "Rate limit exceeded")
    TOO_MANY_REQUESTS = ("RATE_002", "Too many requests")
    
    # External service errors (1800-1899)
    EXTERNAL_SERVICE_ERROR = ("EXT_001", "External service unavailable")
    WECHAT_API_ERROR = ("EXT_002", "WeChat API error")
    EMAIL_SERVICE_ERROR = ("EXT_003", "Email service error")
    
    # General errors (1900-1999)
    INTERNAL_SERVER_ERROR = ("SYS_001", "Internal server error")
    VALIDATION_ERROR = ("SYS_002", "Validation error")
    INVALID_REQUEST = ("SYS_003", "Invalid request")

class APIResponse:
    """Standardized API response format"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a successful response"""
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            response["meta"] = meta
            
        return response
    
    @staticmethod
    def error(
        error_code: ErrorCode,
        details: Optional[str] = None,
        field_errors: Optional[Dict[str, List[str]]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> JSONResponse:
        """Create an error response"""
        code, message = error_code.value
        
        error_data = {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        }
        
        if field_errors:
            error_data["error"]["field_errors"] = field_errors
        
        # Log the error
        logger.error(f"API Error: {code} - {message}", extra={
            "error_code": code,
            "details": details,
            "field_errors": field_errors
        })
        
        return JSONResponse(
            status_code=status_code,
            content=error_data
        )

class APIException(HTTPException):
    """Custom exception class for API errors"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        details: Optional[str] = None,
        field_errors: Optional[Dict[str, List[str]]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        self.error_code = error_code
        self.details = details
        self.field_errors = field_errors
        
        code, message = error_code.value
        super().__init__(status_code=status_code, detail=message)

def create_validation_error(field_errors: Dict[str, List[str]]) -> APIException:
    """Create a validation error with field-specific errors"""
    return APIException(
        error_code=ErrorCode.VALIDATION_ERROR,
        field_errors=field_errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

def create_auth_error(error_code: ErrorCode) -> APIException:
    """Create an authentication error"""
    return APIException(
        error_code=error_code,
        status_code=status.HTTP_401_UNAUTHORIZED
    )

def create_not_found_error(error_code: ErrorCode) -> APIException:
    """Create a not found error"""
    return APIException(
        error_code=error_code,
        status_code=status.HTTP_404_NOT_FOUND
    )

def create_server_error(error_code: ErrorCode, details: Optional[str] = None) -> APIException:
    """Create a server error"""
    return APIException(
        error_code=error_code,
        details=details,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
