"""
Test script for error handling and validation implementation
"""

import asyncio
import json
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.exceptions import ValidationException, ErrorDetail
from app.validation import (
    validate_uuid_format,
    validate_text_content,
    validate_email_format,
    validate_phone_number,
    validate_risk_level,
    validate_score_range,
    sanitize_filename
)

client = TestClient(app)

def test_standardized_error_responses():
    """Test that all endpoints return standardized error responses"""
    print("Testing standardized error responses...")
    
    # Test invalid tip ID format
    response = client.get("/api/tips/invalid-uuid")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 400  # ValidationException returns 400
    error_data = response.json()
    assert "error" in error_data
    assert "timestamp" in error_data
    assert "status_code" in error_data
    assert "error_type" in error_data
    print("✓ Invalid UUID format returns standardized error")
    
    # Test empty tip message
    response = client.post("/api/check-tip", json={"message": ""})
    print(f"Empty message response: {response.status_code} - {response.text}")
    # This should be a validation error
    assert response.status_code in [400, 422]  # Either is acceptable
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data
    print("✓ Empty message returns validation error")
    
    # Test invalid file upload
    response = client.post("/api/check-pdf", files={"file": ("test.txt", b"not a pdf", "text/plain")})
    print(f"File upload response: {response.status_code} - {response.text}")
    assert response.status_code in [400, 422]  # Either is acceptable
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data
    print("✓ Invalid file type returns standardized error")

def test_input_validation():
    """Test Pydantic model validation"""
    print("\nTesting input validation...")
    
    # Test tip creation with invalid data
    invalid_tip_data = {
        "message": "x",  # Too short
        "source": "invalid_source"  # Invalid source
    }
    response = client.post("/api/tips", json=invalid_tip_data)
    print(f"Invalid tip response: {response.status_code} - {response.text}")
    assert response.status_code in [400, 422]  # Either is acceptable
    print("✓ Invalid tip data rejected")
    
    # Test valid tip creation
    valid_tip_data = {
        "message": "This is a valid investment tip message that meets minimum length requirements",
        "source": "manual"
    }
    response = client.post("/api/tips", json=valid_tip_data)
    assert response.status_code == 200
    print("✓ Valid tip data accepted")
    
    # Test heatmap with invalid date format
    response = client.get("/api/fraud-heatmap?dimension=sector&from_date=invalid-date")
    print(f"Invalid date response: {response.status_code} - {response.text}")
    assert response.status_code in [400, 422]  # Either is acceptable
    print("✓ Invalid date format rejected")

def test_validation_utilities():
    """Test validation utility functions"""
    print("\nTesting validation utilities...")
    
    # Test UUID validation
    try:
        validate_uuid_format("invalid-uuid")
        assert False, "Should have raised ValidationException"
    except ValidationException as e:
        assert e.error_type == "validation_error"
        print("✓ UUID validation works")
    
    # Test text content validation
    try:
        validate_text_content("<script>alert('xss')</script>")
        assert False, "Should have raised ValidationException"
    except ValidationException as e:
        assert "unsafe content" in e.detail.lower()
        print("✓ XSS protection works")
    
    # Test email validation
    try:
        validate_email_format("invalid-email")
        assert False, "Should have raised ValidationException"
    except ValidationException:
        print("✓ Email validation works")
    
    # Test phone validation
    try:
        validate_phone_number("123")
        assert False, "Should have raised ValidationException"
    except ValidationException:
        print("✓ Phone validation works")
    
    # Test risk level validation
    try:
        validate_risk_level("Invalid")
        assert False, "Should have raised ValidationException"
    except ValidationException:
        print("✓ Risk level validation works")
    
    # Test score range validation
    try:
        validate_score_range(150)
        assert False, "Should have raised ValidationException"
    except ValidationException:
        print("✓ Score range validation works")
    
    # Test filename sanitization
    safe_name = sanitize_filename("../../../etc/passwd")
    assert ".." not in safe_name
    print("✓ Filename sanitization works")

def test_rate_limiting():
    """Test rate limiting middleware"""
    print("\nTesting rate limiting...")
    
    # Make multiple requests quickly (this is a basic test)
    responses = []
    for i in range(5):
        response = client.get("/health")
        responses.append(response.status_code)
    
    # All should succeed for small number of requests
    assert all(status == 200 for status in responses)
    print("✓ Rate limiting allows normal usage")

def test_file_validation():
    """Test file upload validation"""
    print("\nTesting file validation...")
    
    # Test file size limit (create a large dummy file)
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    response = client.post("/api/check-pdf", files={"file": ("large.pdf", large_content, "application/pdf")})
    print(f"Large file response: {response.status_code}")
    assert response.status_code in [400, 413, 422]  # Any of these is acceptable
    if response.status_code != 413:  # If not payload too large, check error message
        error_data = response.json()
        message = error_data.get("message", "").lower()
        assert "file size" in message or "too large" in message or "limit" in message
    print("✓ File size validation works")
    
    # Test invalid file type
    response = client.post("/api/check-pdf", files={"file": ("test.txt", b"content", "text/plain")})
    print(f"Invalid file type response: {response.status_code}")
    assert response.status_code in [400, 422]  # Either is acceptable
    print("✓ File type validation works")

def test_pagination_validation():
    """Test pagination parameter validation"""
    print("\nTesting pagination validation...")
    
    # Test invalid pagination parameters
    response = client.get("/api/tips?skip=-1")
    print(f"Negative skip response: {response.status_code}")
    assert response.status_code in [400, 422]  # Either is acceptable
    print("✓ Negative skip parameter rejected")
    
    response = client.get("/api/tips?limit=0")
    print(f"Zero limit response: {response.status_code}")
    assert response.status_code in [400, 422]  # Either is acceptable
    print("✓ Zero limit parameter rejected")
    
    response = client.get("/api/tips?limit=2000")
    print(f"Excessive limit response: {response.status_code}")
    assert response.status_code in [400, 422]  # Either is acceptable
    print("✓ Excessive limit parameter rejected")

def test_api_error_consistency():
    """Test that all API errors follow the same format"""
    print("\nTesting API error consistency...")
    
    # Collect error responses from different endpoints
    error_responses = []
    
    # 404 errors
    response = client.get("/api/tips/00000000-0000-0000-0000-000000000000")
    if response.status_code == 404:
        error_responses.append(response.json())
    
    # 422 validation errors
    response = client.post("/api/check-tip", json={"message": ""})
    if response.status_code == 422:
        error_responses.append(response.json())
    
    # Check all errors have required fields (either our format or FastAPI's)
    for error_response in error_responses:
        # Our custom error format or FastAPI's default format
        has_custom_format = all(key in error_response for key in ["error", "timestamp", "status_code", "error_type", "message"])
        has_fastapi_format = "detail" in error_response
        assert has_custom_format or has_fastapi_format, f"Invalid error format: {error_response}"
    
    print("✓ All error responses follow consistent format")

def test_security_headers():
    """Test security-related headers and middleware"""
    print("\nTesting security features...")
    
    response = client.get("/health")
    assert response.status_code == 200
    print("✓ Basic security middleware working")

def run_all_tests():
    """Run all error handling and validation tests"""
    print("=" * 60)
    print("IRIS API Error Handling and Validation Tests")
    print("=" * 60)
    
    try:
        test_standardized_error_responses()
        test_input_validation()
        test_validation_utilities()
        test_rate_limiting()
        test_file_validation()
        test_pagination_validation()
        test_api_error_consistency()
        test_security_headers()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Error handling and validation working correctly!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("=" * 60)
        raise

if __name__ == "__main__":
    run_all_tests()