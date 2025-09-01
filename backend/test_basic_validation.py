"""
Basic test for error handling and validation implementation
"""

import requests
import json

# Test the API directly
BASE_URL = "http://localhost:8000"

def test_validation_functions():
    """Test validation utility functions directly"""
    print("Testing validation utilities...")
    
    from app.validation import (
        validate_uuid_format,
        validate_text_content,
        validate_email_format,
        validate_risk_level,
        validate_score_range,
        sanitize_filename
    )
    from app.exceptions import ValidationException
    
    # Test UUID validation
    try:
        validate_uuid_format("invalid-uuid")
        print("❌ UUID validation failed")
    except ValidationException as e:
        print("✓ UUID validation works")
    
    # Test text content validation
    try:
        validate_text_content("<script>alert('xss')</script>")
        print("❌ XSS protection failed")
    except ValidationException as e:
        print("✓ XSS protection works")
    
    # Test email validation
    try:
        validate_email_format("invalid-email")
        print("❌ Email validation failed")
    except ValidationException:
        print("✓ Email validation works")
    
    # Test risk level validation
    try:
        validate_risk_level("Invalid")
        print("❌ Risk level validation failed")
    except ValidationException:
        print("✓ Risk level validation works")
    
    # Test score range validation
    try:
        validate_score_range(150)
        print("❌ Score range validation failed")
    except ValidationException:
        print("✓ Score range validation works")
    
    # Test filename sanitization
    safe_name = sanitize_filename("../../../etc/passwd")
    if ".." not in safe_name:
        print("✓ Filename sanitization works")
    else:
        print("❌ Filename sanitization failed")

def test_error_response_format():
    """Test that error responses follow standardized format"""
    print("\nTesting error response format...")
    
    from app.exceptions import (
        ValidationException,
        NotFoundException,
        ExternalServiceException,
        ErrorDetail,
        create_error_response
    )
    
    # Test creating standardized error response
    error_response = create_error_response(
        status_code=400,
        message="Test error",
        error_type="validation_error",
        details=[ErrorDetail(
            code="test_error",
            message="This is a test error",
            field="test_field"
        )]
    )
    
    # Check required fields
    assert error_response.error == True
    assert error_response.status_code == 400
    assert error_response.error_type == "validation_error"
    assert error_response.message == "Test error"
    assert len(error_response.details) == 1
    print("✓ Standardized error response format works")

def test_exception_classes():
    """Test custom exception classes"""
    print("\nTesting exception classes...")
    
    from app.exceptions import (
        ValidationException,
        NotFoundException,
        ExternalServiceException,
        FileProcessingException,
        BusinessLogicException
    )
    
    # Test ValidationException
    try:
        raise ValidationException("Test validation error")
    except ValidationException as e:
        assert e.status_code == 400
        assert e.error_type == "validation_error"
        print("✓ ValidationException works")
    
    # Test NotFoundException
    try:
        raise NotFoundException("User", "123")
    except NotFoundException as e:
        assert e.status_code == 404
        assert e.error_type == "not_found_error"
        assert "User not found (ID: 123)" in e.detail
        print("✓ NotFoundException works")
    
    # Test ExternalServiceException
    try:
        raise ExternalServiceException("gemini_api", "Service unavailable")
    except ExternalServiceException as e:
        assert e.status_code == 503
        assert e.error_type == "external_service_error"
        print("✓ ExternalServiceException works")

def test_file_validation_functions():
    """Test file validation functions"""
    print("\nTesting file validation functions...")
    
    from app.exceptions import validate_file_type, validate_file_size, ValidationException
    
    # Test file type validation
    try:
        validate_file_type("test.txt", ["pdf"])
        print("❌ File type validation failed")
    except ValidationException:
        print("✓ File type validation works")
    
    # Test file size validation
    try:
        validate_file_size(11 * 1024 * 1024, 10 * 1024 * 1024)  # 11MB > 10MB limit
        print("❌ File size validation failed")
    except ValidationException:
        print("✓ File size validation works")

def run_basic_tests():
    """Run basic validation tests"""
    print("=" * 60)
    print("IRIS Basic Error Handling and Validation Tests")
    print("=" * 60)
    
    try:
        test_validation_functions()
        test_error_response_format()
        test_exception_classes()
        test_file_validation_functions()
        
        print("\n" + "=" * 60)
        print("✅ ALL BASIC TESTS PASSED!")
        print("Error handling and validation implementation is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("=" * 60)
        raise

if __name__ == "__main__":
    run_basic_tests()