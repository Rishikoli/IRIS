"""
Enhanced input validation utilities for IRIS API
"""

import re
import uuid
import time
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from app.exceptions import ValidationException, ErrorDetail

class PaginationParams(BaseModel):
    """Standard pagination parameters with validation"""
    skip: int = Field(default=0, ge=0, le=10000, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")

class DateRangeParams(BaseModel):
    """Date range parameters with validation"""
    from_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Start date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="End date (YYYY-MM-DD)")
    
    @validator('to_date')
    def validate_date_range(cls, v, values):
        if v and values.get('from_date'):
            from datetime import datetime
            try:
                from_date = datetime.strptime(values['from_date'], "%Y-%m-%d").date()
                to_date = datetime.strptime(v, "%Y-%m-%d").date()
                if from_date > to_date:
                    raise ValueError("from_date must be before to_date")
            except ValueError as e:
                raise ValueError(f"Invalid date range: {str(e)}")
        return v

class SortParams(BaseModel):
    """Standard sorting parameters"""
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")

def validate_uuid_format(value: str, field_name: str = "id") -> str:
    """Validate UUID format and return the value"""
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValidationException(
            f"Invalid {field_name} format",
            details=[ErrorDetail(
                code="invalid_uuid",
                message=f"{field_name} must be a valid UUID",
                field=field_name
            )]
        )

def validate_text_content(text: str, min_length: int = 1, max_length: int = 10000, field_name: str = "text") -> str:
    """Validate text content for length and safety"""
    if not text or not text.strip():
        raise ValidationException(
            f"{field_name} cannot be empty",
            details=[ErrorDetail(
                code="empty_text",
                message=f"{field_name} is required and cannot be empty",
                field=field_name
            )]
        )
    
    text = text.strip()
    
    if len(text) < min_length:
        raise ValidationException(
            f"{field_name} too short",
            details=[ErrorDetail(
                code="text_too_short",
                message=f"{field_name} must be at least {min_length} characters long",
                field=field_name,
                details={"min_length": min_length, "current_length": len(text)}
            )]
        )
    
    if len(text) > max_length:
        raise ValidationException(
            f"{field_name} too long",
            details=[ErrorDetail(
                code="text_too_long",
                message=f"{field_name} must be no more than {max_length} characters long",
                field=field_name,
                details={"max_length": max_length, "current_length": len(text)}
            )]
        )
    
    # Check for potentially dangerous content
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValidationException(
                f"{field_name} contains potentially unsafe content",
                details=[ErrorDetail(
                    code="unsafe_content",
                    message=f"{field_name} contains potentially malicious content",
                    field=field_name
                )]
            )
    
    return text

def validate_email_format(email: str) -> str:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationException(
            "Invalid email format",
            details=[ErrorDetail(
                code="invalid_email",
                message="Email must be in valid format",
                field="email"
            )]
        )
    return email.lower()

def validate_phone_number(phone: str) -> str:
    """Validate phone number format (Indian format)"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check for valid Indian phone number patterns
    if len(digits_only) == 10 and digits_only[0] in '6789':
        return f"+91{digits_only}"
    elif len(digits_only) == 12 and digits_only.startswith('91') and digits_only[2] in '6789':
        return f"+{digits_only}"
    elif len(digits_only) == 13 and digits_only.startswith('91') and digits_only[3] in '6789':
        return digits_only
    else:
        raise ValidationException(
            "Invalid phone number format",
            details=[ErrorDetail(
                code="invalid_phone",
                message="Phone number must be a valid Indian mobile number",
                field="phone"
            )]
        )

def validate_risk_level(level: str) -> str:
    """Validate risk level values"""
    valid_levels = ['Low', 'Medium', 'High']
    if level not in valid_levels:
        raise ValidationException(
            "Invalid risk level",
            details=[ErrorDetail(
                code="invalid_risk_level",
                message=f"Risk level must be one of: {', '.join(valid_levels)}",
                field="level",
                details={"valid_levels": valid_levels}
            )]
        )
    return level

def validate_score_range(score: int, min_score: int = 0, max_score: int = 100, field_name: str = "score") -> int:
    """Validate score is within valid range"""
    if not isinstance(score, int) or score < min_score or score > max_score:
        raise ValidationException(
            f"Invalid {field_name}",
            details=[ErrorDetail(
                code="invalid_score_range",
                message=f"{field_name} must be between {min_score} and {max_score}",
                field=field_name,
                details={"min_score": min_score, "max_score": max_score, "received": score}
            )]
        )
    return score

def validate_json_structure(data: Dict[str, Any], required_fields: List[str], field_name: str = "data") -> Dict[str, Any]:
    """Validate JSON structure has required fields"""
    if not isinstance(data, dict):
        raise ValidationException(
            f"Invalid {field_name} format",
            details=[ErrorDetail(
                code="invalid_json_format",
                message=f"{field_name} must be a valid JSON object",
                field=field_name
            )]
        )
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationException(
            f"Missing required fields in {field_name}",
            details=[ErrorDetail(
                code="missing_required_fields",
                message=f"Required fields missing: {', '.join(missing_fields)}",
                field=field_name,
                details={"missing_fields": missing_fields, "required_fields": required_fields}
            )]
        )
    
    return data

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    if not filename:
        raise ValidationException(
            "Filename is required",
            details=[ErrorDetail(
                code="missing_filename",
                message="Filename cannot be empty",
                field="filename"
            )]
        )
    
    # Remove path components and dangerous characters
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_filename = safe_filename.replace('..', '_')
    
    # Ensure filename is not too long
    if len(safe_filename) > 255:
        name, ext = safe_filename.rsplit('.', 1) if '.' in safe_filename else (safe_filename, '')
        safe_filename = name[:250] + ('.' + ext if ext else '')
    
    return safe_filename

class APIResponseValidator:
    """Validator for API responses to ensure consistency"""
    
    @staticmethod
    def validate_success_response(data: Any, message: str = None) -> Dict[str, Any]:
        """Create standardized success response"""
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": time.time()
        }
    
    @staticmethod
    def validate_list_response(items: List[Any], total_count: int = None, pagination: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized list response"""
        response = {
            "success": True,
            "items": items,
            "count": len(items),
            "timestamp": time.time()
        }
        
        if total_count is not None:
            response["total_count"] = total_count
        
        if pagination:
            response["pagination"] = pagination
        
        return response

# Common validation decorators
def validate_request_size(max_size_mb: int = 10):
    """Decorator to validate request size"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented with actual request size checking
            # For now, it's a placeholder for the pattern
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_content_type(allowed_types: List[str]):
    """Decorator to validate content type"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented with actual content type checking
            # For now, it's a placeholder for the pattern
            return await func(*args, **kwargs)
        return wrapper
    return decorator