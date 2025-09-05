"""
Security configuration and utilities for IRIS RegTech Platform
"""

import os
import re
from typing import List, Dict, Any
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

class SecurityConfig:
    """Centralized security configuration"""
    
    # File upload security
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_FILE_SIZE = 1024  # 1KB
    ALLOWED_FILE_TYPES = ['pdf']
    ALLOWED_CONTENT_TYPES = ['application/pdf']
    
    # Text input security
    MAX_TEXT_LENGTH = 10000
    MIN_TEXT_LENGTH = 1
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100  # requests per minute
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # CORS settings
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS = [
        "Accept", "Accept-Language", "Content-Language", "Content-Type",
        "Authorization", "X-Requested-With", "X-Request-ID"
    ]
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY", 
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # Content Security Policy
    CSP_DEVELOPMENT = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
        "script-src-elem 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src-elem 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "connect-src 'self' https: http: ws: wss:; "
        "img-src 'self' data: https: http:; "
        "font-src 'self' data: https://cdn.jsdelivr.net https://unpkg.com; "
        "object-src 'none'"
    )
    
    CSP_PRODUCTION = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://generativelanguage.googleapis.com; "
        "font-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_pdf_magic_bytes(content: bytes) -> bool:
        """Validate PDF file signature"""
        return content.startswith(b'%PDF-')
    
    @staticmethod
    def detect_malicious_patterns(text: str) -> List[str]:
        """Detect potentially malicious patterns in text"""
        patterns = {
            'script_injection': r'<script[^>]*>.*?</script>',
            'javascript_protocol': r'javascript\s*:',
            'data_uri_html': r'data\s*:\s*text/html',
            'vbscript_protocol': r'vbscript\s*:',
            'event_handlers': r'on\w+\s*=',
            'css_import': r'@import',
            'css_expression': r'expression\s*\(',
            'sql_injection': r';\s*(drop|delete|insert|update|create|alter)\s+',
            'union_select': r'union\s+select',
            'sql_tautology': r'(or|and)\s+\d+\s*=\s*\d+',
            'command_injection': r'[;&|`$]',
            'path_traversal': r'\.\./+',
            'encoded_traversal': r'%2e%2e%2f',
        }
        
        detected = []
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                detected.append(pattern_name)
        
        return detected
    
    @staticmethod
    def sanitize_user_input(text: str, max_length: int = None) -> str:
        """Comprehensive user input sanitization"""
        if not text:
            return ""
        
        import html
        
        # HTML entity decode to catch encoded attacks
        text = html.unescape(text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript\s*:',
            r'data\s*:\s*text/html',
            r'vbscript\s*:',
            r'on\w+\s*=',
            r'@import',
            r'expression\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Truncate if too long
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_request_origin(request: Request, allowed_origins: List[str]) -> bool:
        """Validate request origin against allowed list"""
        origin = request.headers.get("origin")
        if not origin:
            return True  # Allow requests without origin (direct API calls)
        
        # Check exact matches
        if origin in allowed_origins:
            return True
        
        # Check wildcard patterns
        for allowed in allowed_origins:
            if "*" in allowed:
                pattern = allowed.replace("*", ".*")
                if re.match(f"^{pattern}$", origin):
                    return True
        
        return False

class RateLimiter:
    """Simple in-memory rate limiter for demo purposes"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, client_id: str, limit: int = 100, window: int = 60) -> bool:
        """Check if request is within rate limit"""
        import time
        
        current_time = time.time()
        
        # Clean old entries
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < window
            ]
        else:
            self.requests[client_id] = []
        
        # Check limit
        if len(self.requests[client_id]) >= limit:
            return False
        
        # Add current request
        self.requests[client_id].append(current_time)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

class SecurityMiddleware:
    """Security middleware utilities"""
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (for proxy/load balancer setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID for tracking"""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any], request: Request = None):
        """Log security events for monitoring"""
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        if request:
            log_entry.update({
                "client_ip": SecurityMiddleware.get_client_ip(request),
                "user_agent": request.headers.get("User-Agent", ""),
                "path": str(request.url.path),
                "method": request.method
            })
        
        # In production, this would go to a proper logging system
        print(f"SECURITY_EVENT: {json.dumps(log_entry)}")

# Authentication utilities (placeholder for future implementation)
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = None):
    """Get current authenticated user (placeholder)"""
    # For demo purposes, return a mock user
    # In production, this would validate JWT tokens
    return {
        "id": "demo_user",
        "role": "investor",
        "permissions": ["read", "write"]
    }

def require_permission(permission: str):
    """Decorator to require specific permission (placeholder)"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # In production, this would check user permissions
            return await func(*args, **kwargs)
        return wrapper
    return decorator