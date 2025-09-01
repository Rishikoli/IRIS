"""
Test security validation and file handling implementations
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app
from app.exceptions import ValidationException, sanitize_text_input, validate_file_type, validate_file_size
from app.security import SecurityValidator, SecurityConfig

client = TestClient(app)

class TestFileValidation:
    """Test file upload security validation"""
    
    def test_validate_pdf_file_type_success(self):
        """Test valid PDF file type validation"""
        # Should not raise exception
        validate_file_type("document.pdf", ["pdf"])
    
    def test_validate_pdf_file_type_invalid_extension(self):
        """Test invalid file extension rejection"""
        with pytest.raises(ValidationException) as exc_info:
            validate_file_type("document.exe", ["pdf"])
        
        assert "invalid_file_type" in str(exc_info.value.details[0].code)
    
    def test_validate_pdf_file_type_double_extension(self):
        """Test double extension rejection"""
        with pytest.raises(ValidationException) as exc_info:
            validate_file_type("document.pdf.exe", ["pdf"])
        
        assert "multiple_extensions" in str(exc_info.value.details[0].code)
    
    def test_validate_file_size_success(self):
        """Test valid file size"""
        # Should not raise exception
        validate_file_size(1024 * 1024, 10 * 1024 * 1024)  # 1MB file, 10MB limit
    
    def test_validate_file_size_too_large(self):
        """Test file size too large rejection"""
        with pytest.raises(ValidationException) as exc_info:
            validate_file_size(15 * 1024 * 1024, 10 * 1024 * 1024)  # 15MB file, 10MB limit
        
        assert "file_too_large" in str(exc_info.value.details[0].code)
    
    def test_validate_file_size_empty(self):
        """Test empty file rejection"""
        with pytest.raises(ValidationException) as exc_info:
            validate_file_size(0, 10 * 1024 * 1024)
        
        assert "invalid_file_size" in str(exc_info.value.details[0].code)
    
    def test_pdf_magic_bytes_validation(self):
        """Test PDF magic bytes validation"""
        # Valid PDF signature
        assert SecurityValidator.validate_pdf_magic_bytes(b'%PDF-1.4')
        assert SecurityValidator.validate_pdf_magic_bytes(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3')
        
        # Invalid signatures
        assert not SecurityValidator.validate_pdf_magic_bytes(b'<html>')
        assert not SecurityValidator.validate_pdf_magic_bytes(b'PK\x03\x04')  # ZIP signature
        assert not SecurityValidator.validate_pdf_magic_bytes(b'\x89PNG')  # PNG signature

class TestTextSanitization:
    """Test text input sanitization and validation"""
    
    def test_sanitize_clean_text(self):
        """Test sanitization of clean text"""
        clean_text = "This is a normal investment tip about AAPL stock."
        result = sanitize_text_input(clean_text)
        assert result == clean_text
    
    def test_sanitize_script_injection(self):
        """Test script injection removal"""
        malicious_text = "Buy AAPL now! <script>alert('xss')</script> Great returns!"
        result = sanitize_text_input(malicious_text)
        assert "<script>" not in result
        assert "alert" not in result
        assert "Buy AAPL now!" in result
    
    def test_sanitize_javascript_protocol(self):
        """Test javascript protocol removal"""
        malicious_text = "Click here: javascript:alert('xss') for tips"
        result = sanitize_text_input(malicious_text)
        assert "javascript:" not in result
    
    def test_sanitize_event_handlers(self):
        """Test event handler removal"""
        malicious_text = "Investment tip onclick=alert('xss') here"
        result = sanitize_text_input(malicious_text)
        assert "onclick=" not in result
    
    def test_sanitize_html_entities(self):
        """Test HTML entity decoding and sanitization"""
        encoded_text = "Buy &lt;script&gt;alert('xss')&lt;/script&gt; AAPL"
        result = sanitize_text_input(encoded_text)
        assert "<script>" not in result
        assert "alert" not in result
    
    def test_sanitize_control_characters(self):
        """Test control character removal"""
        text_with_control = "Normal text\x00\x01\x02 with control chars"
        result = sanitize_text_input(text_with_control)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "Normal text with control chars" == result
    
    def test_detect_malicious_patterns(self):
        """Test malicious pattern detection"""
        test_cases = [
            ("Normal text", []),
            ("<script>alert('xss')</script>", ["script_injection"]),
            ("javascript:alert('xss')", ["javascript_protocol"]),
            ("onclick=alert('xss')", ["event_handlers"]),
            ("'; DROP TABLE users; --", ["sql_injection"]),
            ("1=1 OR 1=1", ["sql_tautology"]),
            ("../../../etc/passwd", ["path_traversal"]),
        ]
        
        for text, expected_patterns in test_cases:
            detected = SecurityValidator.detect_malicious_patterns(text)
            for pattern in expected_patterns:
                assert pattern in detected, f"Pattern {pattern} not detected in: {text}"

class TestPDFUploadSecurity:
    """Test PDF upload endpoint security"""
    
    def create_test_pdf(self, content: bytes = None) -> bytes:
        """Create a test PDF file"""
        if content is None:
            # Minimal valid PDF content
            content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000074 00000 n 
0000000120 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
179
%%EOF"""
        return content
    
    def test_pdf_upload_valid_file(self):
        """Test valid PDF upload"""
        pdf_content = self.create_test_pdf()
        
        response = client.post(
            "/api/check-pdf",
            files={"file": ("test.pdf", pdf_content, "application/pdf")}
        )
        
        # Should succeed (might fail due to missing dependencies, but not due to security)
        assert response.status_code in [200, 422, 503]  # 422 for missing OCR, 503 for missing Gemini
    
    def test_pdf_upload_invalid_extension(self):
        """Test rejection of non-PDF file"""
        pdf_content = self.create_test_pdf()
        
        response = client.post(
            "/api/check-pdf",
            files={"file": ("test.exe", pdf_content, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "invalid_file_type" in response.text
    
    def test_pdf_upload_invalid_content_type(self):
        """Test rejection of invalid content type"""
        pdf_content = self.create_test_pdf()
        
        response = client.post(
            "/api/check-pdf",
            files={"file": ("test.pdf", pdf_content, "text/plain")}
        )
        
        assert response.status_code == 400
        assert "invalid_content_type" in response.text
    
    def test_pdf_upload_invalid_magic_bytes(self):
        """Test rejection of file with invalid PDF signature"""
        fake_pdf = b"<html><body>Fake PDF</body></html>"
        
        response = client.post(
            "/api/check-pdf",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "invalid_pdf_signature" in response.text
    
    def test_pdf_upload_too_large(self):
        """Test rejection of oversized file"""
        # Create a file larger than 10MB
        large_content = b"%PDF-1.4\n" + b"x" * (11 * 1024 * 1024)
        
        response = client.post(
            "/api/check-pdf",
            files={"file": ("large.pdf", large_content, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "file_too_large" in response.text
    
    def test_pdf_upload_too_small(self):
        """Test rejection of too small file"""
        tiny_content = b"%PDF"  # Too small to be valid
        
        response = client.post(
            "/api/check-pdf",
            files={"file": ("tiny.pdf", tiny_content, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "file_too_small" in response.text

class TestTipValidationSecurity:
    """Test tip submission security"""
    
    def test_tip_submission_clean_text(self):
        """Test clean tip submission"""
        clean_tip = {
            "message": "I heard AAPL might go up 20% next month based on earnings forecast.",
            "source": "manual"
        }
        
        response = client.post("/api/check-tip", json=clean_tip)
        
        # Should succeed (might fail due to missing Gemini API, but not due to security)
        assert response.status_code in [200, 503]
    
    def test_tip_submission_malicious_script(self):
        """Test rejection of malicious script in tip"""
        malicious_tip = {
            "message": "Buy AAPL <script>alert('xss')</script> for great returns!",
            "source": "manual"
        }
        
        response = client.post("/api/check-tip", json=malicious_tip)
        
        # Should either sanitize or reject
        if response.status_code == 200:
            # If accepted, should be sanitized
            assert "<script>" not in response.text
        else:
            # If rejected, should be validation error
            assert response.status_code == 422
    
    def test_tip_submission_too_short(self):
        """Test rejection of too short tip"""
        short_tip = {
            "message": "Buy AAPL",  # Less than 10 characters
            "source": "manual"
        }
        
        response = client.post("/api/check-tip", json=short_tip)
        assert response.status_code == 422
    
    def test_tip_submission_too_long(self):
        """Test rejection of too long tip"""
        long_tip = {
            "message": "A" * 6000,  # More than 5000 characters
            "source": "manual"
        }
        
        response = client.post("/api/check-tip", json=long_tip)
        assert response.status_code == 422

class TestSecurityHeaders:
    """Test security headers in responses"""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert "X-Request-ID" in response.headers
        
        assert "Content-Security-Policy" in response.headers
    
    def test_cors_headers(self):
        """Test CORS headers configuration"""
        # Test preflight request
        response = client.options(
            "/api/check-tip",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_normal_usage(self):
        """Test normal usage within rate limits"""
        # Make a few requests (should succeed)
        for i in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            assert "X-Rate-Limit-Remaining" in response.headers
    
    def test_rate_limit_headers(self):
        """Test rate limiting headers are present"""
        response = client.get("/health")
        assert "X-Rate-Limit-Remaining" in response.headers
        
        remaining = int(response.headers["X-Rate-Limit-Remaining"])
        assert remaining >= 0

if __name__ == "__main__":
    # Run basic tests
    print("Running security validation tests...")
    
    # Test text sanitization
    validator = SecurityValidator()
    
    test_text = "Normal investment tip about AAPL stock"
    sanitized = validator.sanitize_user_input(test_text)
    print(f"✓ Clean text sanitization: '{test_text}' -> '{sanitized}'")
    
    malicious_text = "Buy AAPL <script>alert('xss')</script> now!"
    sanitized = validator.sanitize_user_input(malicious_text)
    print(f"✓ Malicious text sanitization: '{malicious_text}' -> '{sanitized}'")
    
    # Test PDF validation
    valid_pdf = b"%PDF-1.4\nSome content"
    invalid_pdf = b"<html>Fake PDF</html>"
    
    print(f"✓ Valid PDF signature: {validator.validate_pdf_magic_bytes(valid_pdf)}")
    print(f"✓ Invalid PDF signature: {validator.validate_pdf_magic_bytes(invalid_pdf)}")
    
    print("Security validation tests completed!")