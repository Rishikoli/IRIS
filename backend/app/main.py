from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError
import time
import os
from collections import defaultdict
from app.database import engine, Base
from app.routers import tips, assessments, pdf_checks, advisors, heatmap, multi_source_data, forecast, fraud_chains, reviews, websockets, data_status, search
from app.exceptions import (
    IRISException,
    validation_error_handler,
    iris_exception_handler,
    general_exception_handler
)
from app.security import (
    SecurityConfig,
    SecurityMiddleware,
    rate_limiter
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IRIS RegTech Platform API",
    description="Intelligent Risk & Investigation System for fraud detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced rate limiting middleware
@app.middleware("http")
async def enhanced_rate_limit_middleware(request: Request, call_next):
    """Enhanced rate limiting with security logging"""
    client_ip = SecurityMiddleware.get_client_ip(request)
    
    # Check rate limit
    if not rate_limiter.is_allowed(
        client_ip, 
        SecurityConfig.RATE_LIMIT_REQUESTS, 
        SecurityConfig.RATE_LIMIT_WINDOW
    ):
        # Log rate limit violation
        SecurityMiddleware.log_security_event(
            "rate_limit_exceeded",
            {"client_ip": client_ip, "limit": SecurityConfig.RATE_LIMIT_REQUESTS},
            request
        )
        
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {SecurityConfig.RATE_LIMIT_REQUESTS} requests per minute.",
            headers={"Retry-After": str(SecurityConfig.RATE_LIMIT_WINDOW)}
        )
    
    response = await call_next(request)
    return response

# Enhanced security headers middleware
@app.middleware("http")
async def enhanced_security_headers(request: Request, call_next):
    """Add comprehensive security headers to all responses"""
    # Generate request ID for tracking
    request_id = SecurityMiddleware.generate_request_id()
    
    # Add request ID to request state for use in handlers
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    # Add standard security headers
    for header, value in SecurityConfig.SECURITY_HEADERS.items():
        response.headers[header] = value
    
    # Add Content Security Policy based on environment
    if ENVIRONMENT == "production":
        response.headers["Content-Security-Policy"] = SecurityConfig.CSP_PRODUCTION
    else:
        response.headers["Content-Security-Policy"] = SecurityConfig.CSP_DEVELOPMENT
    
    # Add request tracking headers
    response.headers["X-Request-ID"] = request_id
    
    # Add rate limit info (if available)
    client_ip = SecurityMiddleware.get_client_ip(request)
    remaining_requests = SecurityConfig.RATE_LIMIT_REQUESTS - len(
        rate_limiter.requests.get(client_ip, [])
    )
    response.headers["X-Rate-Limit-Remaining"] = str(max(0, remaining_requests))
    
    return response

# Configure CORS middleware using security configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Use security config for CORS settings
cors_origins = SecurityConfig.ALLOWED_ORIGINS.copy()

# For demo/development, allow additional localhost variations
if ENVIRONMENT == "development":
    cors_origins.extend([
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3001",  # Alternative React port
        "http://127.0.0.1:3001"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if ENVIRONMENT != "development" else ["*"],  # Allow all only in dev
    allow_credentials=True,
    allow_methods=SecurityConfig.ALLOWED_METHODS,
    allow_headers=SecurityConfig.ALLOWED_HEADERS,
    expose_headers=["X-Request-ID", "X-Rate-Limit-Remaining"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add exception handlers
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(IRISException, iris_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(tips.router, prefix="/api", tags=["tips"])
app.include_router(assessments.router, prefix="/api", tags=["assessments"])
app.include_router(pdf_checks.router, prefix="/api", tags=["pdf_checks"])
app.include_router(advisors.router, prefix="/api", tags=["advisors"])
app.include_router(heatmap.router, prefix="/api", tags=["heatmap"])
app.include_router(multi_source_data.router, prefix="/api", tags=["multi_source_data"])
app.include_router(forecast.router, tags=["forecast"])
app.include_router(fraud_chains.router, prefix="/api", tags=["fraud_chains"])
app.include_router(reviews.router, prefix="/api", tags=["reviews"])
app.include_router(websockets.router, tags=["websockets"])
app.include_router(data_status.router, tags=["data_status"])
app.include_router(search.router, prefix="/api", tags=["search"])

# Import and include analytics router
from app.routers import analytics
app.include_router(analytics.router, tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "IRIS RegTech Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}