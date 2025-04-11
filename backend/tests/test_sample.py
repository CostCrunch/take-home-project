import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
import os

# Import the FastAPI app
from ..routes import app

# Test client
client = TestClient(app)

# Test data
TEST_USER_ID = "test_user"
TEST_HEADERS = {"user-id": TEST_USER_ID}
TEST_UPLOAD_DIR = Path("uploads") / TEST_USER_ID

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup test environment and cleanup after each test"""
    # Setup: Create test upload directory
    TEST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup: Remove test upload directory
    if TEST_UPLOAD_DIR.exists():
        shutil.rmtree(TEST_UPLOAD_DIR)

def test_list_files_empty():
    """Test listing files when no files exist"""
    response = client.get("/files/", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["files"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10

def test_list_files_unauthorized():
    """Test listing files without user ID"""
    response = client.get("/files/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_upload_file_success():
    """Test successful file upload"""
    # Create a test file
    test_content = b"Hello, World!"
    files = [("files", ("test.txt", test_content, "text/plain"))]
    
    response = client.post("/upload/", headers=TEST_HEADERS, files=files)
    assert response.status_code == 200
    
    # Test if file was saved
    saved_file = TEST_UPLOAD_DIR / "test.txt"
    assert saved_file.exists()
    assert saved_file.read_bytes() == test_content

def test_upload_large_file():
    """Test uploading a file that exceeds size limit"""
    # Create a large test file (6MB)
    large_content = b"0" * (6 * 1024 * 1024)
    files = [("files", ("large.txt", large_content, "text/plain"))]
    
    response = client.post("/upload/", headers=TEST_HEADERS, files=files)
    assert response.status_code == 400
    assert "exceeds maximum size" in response.json()["detail"]

# TODO: Add more tests for:
# 1. Multiple file uploads
# 2. File listing pagination
# 3. Invalid file types
# 4. Error handling scenarios
# 5. Progress updates during upload
# 6. Concurrent uploads
# 7. File metadata accuracy
# 8. Directory structure
# 9. Edge cases (empty files, special characters in filenames)
# 10. Performance under load 

def test_list_vendors_success():
    """
    Sample test showing how to test the /vendors/ endpoint
    
    This test demonstrates:
    1. How to make requests with authentication headers
    2. How to check response status codes
    3. How to verify response data structure
    4. How to test query parameters
    5. How to verify data content
    """
    # Test basic listing
    response = client.get("/vendors/", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "vendors" in data
    assert isinstance(data["vendors"], list)
    
    # Check data content
    vendors = data["vendors"]
    assert len(vendors) > 0
    assert all(isinstance(v, dict) for v in vendors)
    assert all("id" in v for v in vendors)
    assert all("name" in v for v in vendors)
    assert all("email" in v for v in vendors)
    assert all("phone" in v for v in vendors)

    # Test search functionality
    search_term = "depot"
    response = client.get(f"/vendors/?search={search_term}", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    # Verify search results
    assert all(search_term.lower() in v["name"].lower() for v in data["vendors"])

def test_list_vendors_unauthorized():
    """Test the endpoint without authentication"""
    response = client.get("/vendors/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

# TODO: Write tests for the following endpoints:
# 1. GET /vendors/{vendor_id} - Test getting a specific vendor
# 2. GET /vendors/{vendor_id}/addresses - Test getting vendor addresses
# 3. GET /materials/ - Test material listing with pagination and filtering
# 4. GET /invoices/ - Test invoice listing with date and status filters
# 5. GET /invoices/{invoice_id} - Test getting specific invoice
# 6. GET /invoices/{invoice_id}/line-items - Test getting invoice line items
# 7. GET /projects/ - Test project listing
# 8. GET /projects/{project_id}/invoices - Test getting project invoices
# 9. GET /analytics/spend-by-vendor - Test vendor spending analytics
# 10. GET /analytics/spend-by-category - Test category spending analytics
# 11. GET /analytics/monthly-spend - Test monthly spending trends
# 12. GET /materials/price-history/{material_id} - Test material price history
# 13. GET /vendors/{vendor_id}/payment-terms - Test vendor payment terms
# 14. GET /materials/low-stock - Test low stock materials endpoint

# For each endpoint, remember to test:
# - Successful responses
# - Authentication requirements
# - Error cases (404, invalid params, etc.)
# - Query parameter variations
# - Response data structure and content 