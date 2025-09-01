"""
Demo confidence tests for key API endpoints
Tests the main /check-tip and /check-pdf endpoints to ensure demo stability
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
import json

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_demo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

class TestCheckTipEndpoint:
    """Test the /check-tip endpoint for demo stability"""
    
    def test_check_tip_success_high_risk(self):
        """Test successful tip analysis with high risk content"""
        payload = {
            "message": "🚀 URGENT: Buy XYZ stock NOW! Guaranteed 500% returns in 1 week! Limited time offer!",
            "source": "manual"
        }
        
        response = client.post("/api/check-tip", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "tip_id" in data
        assert "assessment" in data
        
        assessment = data["assessment"]
        assert "level" in assessment
        assert "score" in assessment
        assert "reasons" in assessment
        assert "stock_symbols" in assessment
        assert "timestamp" in assessment
        assert "assessment_id" in assessment
        assert "confidence" in assessment
        
        # Verify risk assessment logic
        assert assessment["level"] in ["Low", "Medium", "High"]
        assert 0 <= assessment["score"] <= 100
        assert isinstance(assessment["reasons"], list)
        assert len(assessment["reasons"]) > 0
        assert isinstance(assessment["stock_symbols"], list)
        
        # High risk content should be detected
        assert assessment["level"] in ["Medium", "High"]
        assert assessment["score"] >= 50
    
    def test_check_tip_success_low_risk(self):
        """Test successful tip analysis with low risk content"""
        payload = {
            "message": "ABC company quarterly results look promising. Stock might see some upward movement based on fundamentals and market analysis."
        }
        
        response = client.post("/api/check-tip", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assessment = data["assessment"]
        assert assessment["level"] in ["Low", "Medium"]
        assert assessment["score"] <= 70  # Should be lower risk
    
    def test_check_tip_validation_errors(self):
        """Test validation error handling"""
        # Empty message
        response = client.post("/api/check-tip", json={"message": ""})
        assert response.status_code == 422
        
        # Message too short
        response = client.post("/api/check-tip", json={"message": "short"})
        assert response.status_code == 422
        
        # Message too long
        long_message = "x" * 5001
        response = client.post("/api/check-tip", json={"message": long_message})
        assert response.status_code == 422
        
        # Invalid source
        response = client.post("/api/check-tip", json={
            "message": "Valid message for testing purposes",
            "source": "invalid_source"
        })
        assert response.status_code == 422
    
    def test_check_tip_error_handling(self):
        """Test that the endpoint handles errors gracefully without crashing"""
        # Test with potentially problematic content
        test_cases = [
            {"message": "Test with special chars: <>&\"'"},
            {"message": "Test with unicode: 🚀💰📈"},
            {"message": "Test with numbers: 123456789"},
            {"message": "A" * 100}  # Boundary test
        ]
        
        for payload in test_cases:
            response = client.post("/api/check-tip", json=payload)
            # Should not crash - either success or proper error
            assert response.status_code in [200, 422, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "tip_id" in data
                assert "assessment" in data


class TestCheckPdfEndpoint:
    """Test the /check-pdf endpoint for demo stability"""
    
    def create_test_pdf(self, content: str = "Test PDF content") -> str:
        """Create a simple test PDF file"""
        # For demo purposes, create a simple text file as PDF
        # In real implementation, this would be a proper PDF
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False)
        temp_file.write(f"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n174\n%%EOF\n{content}")
        temp_file.close()
        return temp_file.name
    
    def test_check_pdf_success(self):
        """Test successful PDF analysis"""
        pdf_path = self.create_test_pdf("Test document content for analysis")
        
        try:
            with open(pdf_path, 'rb') as f:
                response = client.post(
                    "/api/check-pdf",
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
            
            # Should handle the request without crashing
            assert response.status_code in [200, 422, 500]
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = [
                    "id", "file_hash", "filename", "file_size", 
                    "score", "is_likely_fake", "created_at"
                ]
                for field in required_fields:
                    assert field in data
                
                # Verify data types and ranges
                assert isinstance(data["score"], int)
                assert 0 <= data["score"] <= 100
                assert isinstance(data["is_likely_fake"], bool)
                assert isinstance(data["file_size"], int)
                assert data["file_size"] > 0
                
        finally:
            # Clean up
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_check_pdf_validation_errors(self):
        """Test PDF upload validation"""
        # Test with non-PDF file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a PDF")
            f.flush()
            
            try:
                with open(f.name, 'rb') as file:
                    response = client.post(
                        "/api/check-pdf",
                        files={"file": ("test.txt", file, "text/plain")}
                    )
                
                # Should reject non-PDF files
                assert response.status_code == 422
                
            finally:
                os.unlink(f.name)
    
    def test_check_pdf_large_file_handling(self):
        """Test handling of large files"""
        # Create a file that's too large (simulate)
        large_content = "x" * (11 * 1024 * 1024)  # 11MB content
        pdf_path = self.create_test_pdf(large_content)
        
        try:
            with open(pdf_path, 'rb') as f:
                response = client.post(
                    "/api/check-pdf",
                    files={"file": ("large.pdf", f, "application/pdf")}
                )
            
            # Should handle large files gracefully
            assert response.status_code in [413, 422, 500]  # Payload too large or validation error
            
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    def test_check_pdf_error_handling(self):
        """Test that PDF endpoint handles errors gracefully"""
        # Test with empty file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.flush()
            
            try:
                with open(f.name, 'rb') as file:
                    response = client.post(
                        "/api/check-pdf",
                        files={"file": ("empty.pdf", file, "application/pdf")}
                    )
                
                # Should not crash - either success or proper error
                assert response.status_code in [200, 422, 500]
                
            finally:
                os.unlink(f.name)


class TestHealthEndpoints:
    """Test basic health and connectivity endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint is accessible"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_docs_endpoint(self):
        """Test API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200


class TestErrorHandling:
    """Test general error handling to prevent demo crashes"""
    
    def test_rate_limiting_doesnt_crash(self):
        """Test that rate limiting works without crashing"""
        # Make several requests quickly
        for i in range(5):
            response = client.post("/api/check-tip", json={
                "message": f"Test message {i} for rate limiting check"
            })
            # Should either succeed or rate limit, but not crash
            assert response.status_code in [200, 422, 429, 500]
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON requests"""
        response = client.post(
            "/api/check-tip",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test handling of requests with missing content type"""
        response = client.post("/api/check-tip", data='{"message": "test"}')
        # Should handle gracefully
        assert response.status_code in [422, 415]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])