"""
Standardized error handling and response formats for IRIS API
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import Optional, Dict, Any, List
import traceback
from datetime import datetime

class ErrorDetail(BaseModel):
    """Standardized error detail structure"""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Standardized error response structure"""
    error: bool = True
    timestamp: str
    status_code: int
    error_type: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None

class IRISException(HTTPException):
    """Base exception class for IRIS-specific errors"""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        error_type: str = "application_error",
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error_type = error_type
        self.details = details or []
        super().__init__(status_code=status_code, detail=message, headers=headers)

class ValidationException(IRISException):
    """Exception for validation errors"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[List[ErrorDetail]] = None):
        super().__init__(
            status_code=400,
            message=message,
            error_type="validation_error",
            details=details
        )

class NotFoundException(IRISException):
    """Exception for resource not found errors"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f" (ID: {identifier})"
        
        super().__init__(
            status_code=404,
            message=message,
            error_type="not_found_error"
        )

class BusinessLogicException(IRISException):
    """Exception for business logic errors"""
    
    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None):
        super().__init__(
            status_code=422,
            message=message,
            error_type="business_logic_error",
            details=details
        )

class ExternalServiceException(IRISException):
    """Exception for external service errors"""
    
    def __init__(self, service: str, message: str = None):
        default_message = f"External service '{service}' is currently unavailable"
        super().__init__(
            status_code=503,
            message=message or default_message,
            error_type="external_service_error"
        )

class FileProcessingException(IRISException):
    """Exception for file processing errors"""
    
    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None):
        super().__init__(
            status_code=422,
            message=message,
            error_type="file_processing_error",
            details=details
        )

def create_error_response(
    status_code: int,
    message: str,
    error_type: str = "application_error",
    details: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create a standardized error response"""
    return ErrorResponse(
        timestamp=datetime.utcnow().isoformat(),
        status_code=status_code,
        error_type=error_type,
        message=message,
        details=details,
        request_id=request_id
    )

def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    details = []
    
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        details.append(ErrorDetail(
            code="validation_error",
            message=error["msg"],
            field=field_path,
            details={"input": error.get("input"), "type": error["type"]}
        ))
    
    error_response = create_error_response(
        status_code=422,
        message="Request validation failed",
        error_type="validation_error",
        details=details
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )

def iris_exception_handler(request: Request, exc: IRISException) -> JSONResponse:
    """Handle IRIS-specific exceptions"""
    error_response = create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_type=exc.error_type,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers=exc.headers
    )

def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    # Log the full traceback for debugging
    print(f"Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    # Don't expose internal error details in production
    error_response = create_error_response(
        status_code=500,
        message="An internal server error occurred",
        error_type="internal_server_error"
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )

# Common validation functions
def validate_file_type(filename: str, allowed_types: List[str]) -> None:
    """Enhanced file type validation with security checks"""
    if not filename:
        raise ValidationException("Filename is required")
    
    # Sanitize filename to prevent path traversal
    safe_filename = sanitize_filename(filename)
    
    # Check for double extensions (e.g., file.pdf.exe)
    parts = safe_filename.lower().split('.')
    if len(parts) > 2:
        raise ValidationException(
            "Multiple file extensions not allowed",
            details=[ErrorDetail(
                code="multiple_extensions",
                message="Files with multiple extensions are not permitted for security reasons",
                field="filename",
                details={"filename": safe_filename}
            )]
        )
    
    file_ext = parts[-1] if len(parts) > 1 else ''
    
    # Check against allowed types
    if file_ext not in allowed_types:
        raise ValidationException(
            f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
            details=[ErrorDetail(
                code="invalid_file_type",
                message=f"File extension '.{file_ext}' is not allowed",
                field="filename",
                details={"allowed_types": allowed_types, "received_type": file_ext}
            )]
        )
    
    # Additional security checks for PDF files
    if file_ext == 'pdf':
        validate_pdf_filename_security(safe_filename)

def validate_pdf_filename_security(filename: str) -> None:
    """Additional security validation for PDF filenames"""
    # Check for suspicious patterns in PDF filenames
    suspicious_patterns = [
        'javascript', 'vbscript', 'activex', 'embed', 'object',
        'script', 'onload', 'onerror', 'onclick'
    ]
    
    filename_lower = filename.lower()
    for pattern in suspicious_patterns:
        if pattern in filename_lower:
            raise ValidationException(
                "Suspicious filename pattern detected",
                details=[ErrorDetail(
                    code="suspicious_filename",
                    message=f"Filename contains potentially malicious pattern: {pattern}",
                    field="filename",
                    details={"pattern": pattern}
                )]
            )

def validate_file_size(file_size: int, max_size: int) -> None:
    """Enhanced file size validation with detailed reporting"""
    if file_size <= 0:
        raise ValidationException(
            "Invalid file size",
            details=[ErrorDetail(
                code="invalid_file_size",
                message="File appears to be empty or corrupted",
                field="file_size",
                details={"file_size": file_size}
            )]
        )
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        current_size_mb = file_size / (1024 * 1024)
        
        raise ValidationException(
            f"File size exceeds maximum limit of {max_size_mb:.1f}MB",
            details=[ErrorDetail(
                code="file_too_large",
                message=f"File size {current_size_mb:.1f}MB exceeds limit of {max_size_mb:.1f}MB",
                field="file_size",
                details={"max_size_mb": max_size_mb, "current_size_mb": current_size_mb}
            )]
        )

def sanitize_filename(filename: str) -> str:
    """Enhanced filename sanitization to prevent security issues"""
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
    import re
    import os
    
    # Get just the filename, no path
    safe_filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    safe_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', safe_filename)
    
    # Remove path traversal attempts
    safe_filename = safe_filename.replace('..', '_')
    safe_filename = safe_filename.replace('~', '_')
    
    # Remove leading/trailing dots and spaces
    safe_filename = safe_filename.strip('. ')
    
    # Ensure filename is not empty after sanitization
    if not safe_filename:
        safe_filename = "sanitized_file"
    
    # Ensure filename is not too long
    if len(safe_filename) > 255:
        name, ext = safe_filename.rsplit('.', 1) if '.' in safe_filename else (safe_filename, '')
        safe_filename = name[:250] + ('.' + ext if ext else '')
    
    # Prevent reserved Windows filenames
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_part = safe_filename.split('.')[0].upper()
    if name_part in reserved_names:
        safe_filename = f"file_{safe_filename}"
    
    return safe_filename

def validate_text_input(text: str, min_length: int = 1, max_length: int = 10000, field_name: str = "text") -> str:
    """Enhanced text input validation with security sanitization"""
    if not text or not text.strip():
        raise ValidationException(
            f"{field_name.capitalize()} input cannot be empty",
            details=[ErrorDetail(
                code="empty_text",
                message=f"{field_name.capitalize()} input is required and cannot be empty",
                field=field_name
            )]
        )
    
    # Sanitize the text input
    sanitized_text = sanitize_text_input(text)
    text_length = len(sanitized_text)
    
    if text_length < min_length:
        raise ValidationException(
            f"{field_name.capitalize()} input too short (minimum {min_length} characters)",
            details=[ErrorDetail(
                code="text_too_short",
                message=f"{field_name.capitalize()} must be at least {min_length} characters long",
                field=field_name,
                details={"min_length": min_length, "current_length": text_length}
            )]
        )
    
    if text_length > max_length:
        raise ValidationException(
            f"{field_name.capitalize()} input too long (maximum {max_length} characters)",
            details=[ErrorDetail(
                code="text_too_long",
                message=f"{field_name.capitalize()} must be no more than {max_length} characters long",
                field=field_name,
                details={"max_length": max_length, "current_length": text_length}
            )]
        )
    
    return sanitized_text

def sanitize_text_input(text: str) -> str:
    """Comprehensive text input sanitization for security"""
    import re
    import html
    
    if not text:
        return ""
    
    # HTML entity decode first to catch encoded attacks
    text = html.unescape(text)
    
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Check for and remove potentially dangerous patterns
    dangerous_patterns = [
        # Script injection patterns
        r'<script[^>]*>.*?</script>',
        r'javascript\s*:',
        r'data\s*:\s*text/html',
        r'vbscript\s*:',
        
        # Event handler patterns
        r'on\w+\s*=',
        r'@import',
        r'expression\s*\(',
        
        # SQL injection patterns (basic)
        r';\s*(drop|delete|insert|update|create|alter)\s+',
        r'union\s+select',
        r'or\s+1\s*=\s*1',
        r'and\s+1\s*=\s*1',
        
        # Command injection patterns
        r'[;&|`$]',
        r'\.\./+',
        r'%2e%2e%2f',
    ]
    
    original_text = text
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    # If significant content was removed, it might be malicious
    if len(text) < len(original_text) * 0.8:
        raise ValidationException(
            "Text contains potentially malicious content",
            details=[ErrorDetail(
                code="malicious_content_detected",
                message="Input text contains patterns that may be malicious and has been rejected",
                field="text",
                details={
                    "original_length": len(original_text),
                    "sanitized_length": len(text)
                }
            )]
        )
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text

def validate_content_type(content_type: str, allowed_types: List[str]) -> None:
    """Validate HTTP content type"""
    if not content_type:
        raise ValidationException(
            "Content-Type header is required",
            details=[ErrorDetail(
                code="missing_content_type",
                message="Content-Type header must be specified",
                field="content_type"
            )]
        )
    
    # Extract main content type (ignore charset and other parameters)
    main_type = content_type.split(';')[0].strip().lower()
    
    if main_type not in allowed_types:
        raise ValidationException(
            f"Invalid content type. Allowed types: {', '.join(allowed_types)}",
            details=[ErrorDetail(
                code="invalid_content_type",
                message=f"Content type '{main_type}' is not allowed",
                field="content_type",
                details={"allowed_types": allowed_types, "received_type": main_type}
            )]
        )