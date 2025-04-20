import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
import os
import sys

# Import the FastAPI app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.routes import app

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

def test_vendor_by_id_success():
    """Test getting a specific vendor by ID"""
    response = client.get("/vendors/v1", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "v1"
    assert data["name"] == "Home Depot"
    assert data["email"] == "orders@homedepot.com"
    assert data["phone"] == "1-800-466-3337"

def test_vendor_by_id_not_found():
    """Test getting a specific vendor by ID that does not exist"""
    response = client.get("/vendors/v4", headers=TEST_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found"

def test_vendor_by_id_unauthorized():
    """Test getting a specific vendor by ID without authentication"""
    response = client.get("/vendors/v1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_vendor_addresses_success():
    """Test getting vendor addresses"""
    response = client.get("/vendors/v1/addresses", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "addresses" in data
    assert isinstance(data["addresses"], list)
    
    addresses = data["addresses"]
    assert len(addresses) > 0
    assert all(isinstance(a, dict) for a in addresses)
    assert all("id" in a for a in addresses)
    assert all("vendor_id" in a for a in addresses)
    assert all("street" in a for a in addresses)
    assert all("city" in a for a in addresses)
    assert all("state" in a for a in addresses)
    assert all("zip" in a for a in addresses)

def test_vendor_addresses_unauthorized():
    """Test getting vendor addresses without authentication"""
    response = client.get("/vendors/v1/addresses")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_invoice_by_id_success():
    """Test getting a specific invoice by ID"""
    response = client.get("/invoices/i1", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "i1"
    assert data["vendor_id"] == "v1"
    assert data["number"] == "INV-001"
    assert data["date"] == "2024-01-15"
    assert data["total"] == 1234.56
    assert data["status"] == "processed"

def test_invoice_by_id_not_found():
    """Test getting a specific invoice by ID that does not exist"""
    response = client.get("/invoices/i3", headers=TEST_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"

def test_invoice_by_id_unauthorized():
    """Test getting a specific invoice by ID without authentication"""
    response = client.get("/invoices/i1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_invoice_line_items_success():
    """Test getting invoice line items"""
    response = client.get("/invoices/i1/line-items", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "line_items" in data
    assert isinstance(data["line_items"], list)
    
    line_items = data["line_items"]
    assert len(line_items) > 0
    assert all(isinstance(li, dict) for li in line_items)
    assert all("id" in li for li in line_items)
    assert all("invoice_id" in li for li in line_items)
    assert all("material_id" in li for li in line_items)
    assert all("quantity" in li for li in line_items)
    assert all("unit_price" in li for li in line_items)

def test_invoice_line_items_unauthorized():
    """Test getting invoice line items without authentication"""
    response = client.get("/invoices/i1/line-items")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_project_listing_success():
    """Test project listing"""
    response = client.get("/projects/", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "projects" in data
    assert isinstance(data["projects"], list)
    
    projects = data["projects"]
    assert len(projects) > 0
    assert all(isinstance(p, dict) for p in projects)
    assert all("id" in p for p in projects)
    assert all("name" in p for p in projects)
    assert all("address" in p for p in projects)

def test_project_listing_unauthorized():
    """Test project listing without authentication"""
    response = client.get("/projects/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_project_invoices_success():
    """Test getting project invoices"""
    response = client.get("/projects/p1/invoices", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "invoices" in data
    assert isinstance(data["invoices"], list)
    invoices = data["invoices"]
    assert len(invoices) > 0
    assert all(isinstance(i, dict) for i in invoices)
    assert all("id" in i for i in invoices)
    assert all("vendor_id" in i for i in invoices)
    assert all("number" in i for i in invoices)
    assert all("date" in i for i in invoices)
    assert all("total" in i for i in invoices)
    assert all("status" in i for i in invoices)
    
    # To cover the else case of the api endpoint
    response2 = client.get("/projects/p2/invoices", headers=TEST_HEADERS)
    assert response2.status_code == 200
    data2 = response2.json()
    assert "invoices" in data2
    assert isinstance(data2["invoices"], list)
    invoices2 = data2["invoices"]
    assert len(invoices2) > 0
    assert all(isinstance(i, dict) for i in invoices2)
    assert all("id" in i for i in invoices2)
    assert all("vendor_id" in i for i in invoices2)
    assert all("number" in i for i in invoices2)
    assert all("date" in i for i in invoices2)
    assert all("total" in i for i in invoices2)
    assert all("status" in i for i in invoices2)

def test_project_invoices_unauthorized():
    """Test getting project invoices without authentication"""
    response = client.get("/projects/p1/invoices")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_analytics_spend_by_category_success():
    """Test category spending analytics"""
    response = client.get("/analytics/spend-by-category", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "spend_by_category" in data
    assert isinstance(data["spend_by_category"], list)
    
    spend_by_category = data["spend_by_category"]
    assert len(spend_by_category) > 0
    assert all(isinstance(sc, dict) for sc in spend_by_category)
    assert all("category" in sc for sc in spend_by_category)
    assert all("total_spend" in sc for sc in spend_by_category)

def test_analytics_spend_by_category_unauthorized():
    """Test category spending analytics without authentication"""
    response = client.get("/analytics/spend-by-category")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_analytics_monthly_spend_success():
    """Test monthly spending analytics"""
    response = client.get("/analytics/monthly-spend", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "monthly_spend" in data
    assert isinstance(data["monthly_spend"], list)
    
    monthly_spend = data["monthly_spend"]
    assert len(monthly_spend) > 0
    assert all(isinstance(ms, dict) for ms in monthly_spend)
    assert all("month" in ms for ms in monthly_spend)
    assert all("total_spend" in ms for ms in monthly_spend)

def test_analytics_monthly_spend_unauthorized():
    """Test monthly spending analytics without authentication"""
    response = client.get("/analytics/monthly-spend")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_materials_price_history_by_id_success():
    """Test material price history"""
    response = client.get("/materials/price-history/m1", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "material_id" in data
    assert "price_history" in data
    assert data["material_id"] == "m1"
    assert isinstance(data["price_history"], list)
    
    price_history = data["price_history"]
    assert len(price_history) > 0
    assert all(isinstance(ph, dict) for ph in price_history)
    assert all("date" in ph for ph in price_history)
    assert all("price" in ph for ph in price_history)

def test_materials_price_history_by_id_unauthorized():
    """Test material price history without authentication"""
    response = client.get("/materials/price-history/m1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_vendor_payment_terms_by_id_success():
    """Test vendor payment terms"""
    response = client.get("/vendors/v1/payment-terms", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "vendor_id" in data
    assert "payment_terms" in data
    assert data["vendor_id"] == "v1"
    assert isinstance(data["payment_terms"], dict)
    
    payment_terms = data["payment_terms"]
    assert payment_terms["net_days"] == 30
    assert payment_terms["discount_percent"] == 2.0
    assert payment_terms["discount_days"] == 10
    assert payment_terms["credit_limit"] == 50000.00

def test_vendor_payment_terms_by_id_unauthorized():
    """Test vendor payment terms without authentication"""
    response = client.get("/vendors/v1/payment-terms")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_low_stock_materials_success():
    """Test low stock materials"""
    response = client.get("/materials/low-stock", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "low_stock_materials" in data
    assert isinstance(data["low_stock_materials"], list)
    
    low_stock_materials = data["low_stock_materials"]
    assert len(low_stock_materials) > 0
    assert all(isinstance(lsm, dict) for lsm in low_stock_materials)
    assert all("material_id" in lsm for lsm in low_stock_materials)
    assert all("name" in lsm for lsm in low_stock_materials)
    assert all("current_stock" in lsm for lsm in low_stock_materials)
    assert all("reorder_point" in lsm for lsm in low_stock_materials)

def test_low_stock_materials_unauthorized():
    """Test low stock materials without authentication"""
    response = client.get("/materials/low-stock")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_get_spend_by_vendor():
    """Test vendor spending analytics"""
    response = client.get("/analytics/spend-by-vendor", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "spend_by_vendor" in data
    assert isinstance(data["spend_by_vendor"], list)
    
    spend_by_vendor = data["spend_by_vendor"]
    assert len(spend_by_vendor) > 0
    assert all(isinstance(sbv, dict) for sbv in spend_by_vendor)
    assert all("vendor_id" in sbv for sbv in spend_by_vendor)
    assert all("vendor_name" in sbv for sbv in spend_by_vendor)
    assert all("total_spend" in sbv for sbv in spend_by_vendor)

    response2 = client.get("/analytics/spend-by-vendor?start_date=2024-06-01&end_date=2025-03-31", headers=TEST_HEADERS)
    assert response2.status_code == 200
    data2 = response2.json()
    
    assert "spend_by_vendor" in data2
    assert isinstance(data2["spend_by_vendor"], list)
    
    spend_by_vendor2 = data2["spend_by_vendor"]
    assert len(spend_by_vendor2) > 0
    assert all(isinstance(sbv, dict) for sbv in spend_by_vendor2)
    assert all("vendor_id" in sbv for sbv in spend_by_vendor2)
    assert all("vendor_name" in sbv for sbv in spend_by_vendor2)
    assert all("total_spend" in sbv for sbv in spend_by_vendor2)

    response3 = client.get("/analytics/spend-by-vendor?start_date=2024-06-01", headers=TEST_HEADERS)
    assert response3.status_code == 200
    data3 = response3.json()
    
    assert "spend_by_vendor" in data3
    assert isinstance(data3["spend_by_vendor"], list)
    
    spend_by_vendor3 = data3["spend_by_vendor"]
    assert len(spend_by_vendor3) > 0
    assert all(isinstance(sbv, dict) for sbv in spend_by_vendor3)
    assert all("vendor_id" in sbv for sbv in spend_by_vendor3)
    assert all("vendor_name" in sbv for sbv in spend_by_vendor3)
    assert all("total_spend" in sbv for sbv in spend_by_vendor3)

def test_get_spend_by_vendor_unauthorized():
    """Test vendor spending analytics without authentication"""
    response = client.get("/analytics/spend-by-vendor")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

    response2 = client.get("/analytics/spend-by-vendor?start_date=2024-06-01&end_date=2025-03-31")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_materials_listing_success():
    """Test materials listing"""
    response = client.get("/materials/", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "materials" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["materials"], list)
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 10
    materials = data["materials"]
    assert len(materials) > 0
    assert all(isinstance(m, dict) for m in materials)
    assert all("id" in m for m in materials)
    assert all("name" in m for m in materials)
    assert all("category" in m for m in materials)
    assert all("unit" in m for m in materials)

    response2 = client.get("/materials/?category=Wood&page=1&page_size=2", headers=TEST_HEADERS)
    assert response2.status_code == 200
    data2 = response2.json()
    assert "materials" in data2
    assert "total" in data2
    assert "page" in data2
    assert "page_size" in data2
    assert isinstance(data2["materials"], list)
    assert data2["total"] == 1
    assert data2["page"] == 1
    assert data2["page_size"] == 2
    materials2 = data2["materials"]
    assert len(materials2) > 0
    assert all(isinstance(m, dict) for m in materials2)
    assert all("id" in m for m in materials2)
    assert all("name" in m for m in materials2)
    assert all("unit" in m for m in materials2)
    assert all(m["category"] == "Wood" for m in materials2)

def test_materials_listing_unauthorized():
    """Test materials listing without authentication"""
    response = client.get("/materials/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

    response2 = client.get("/materials/?category=Wood&page=1&page_size=2")
    assert response2.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

def test_invoice_listing_success():
    """Test invoice listing"""
    response = client.get("/invoices/", headers=TEST_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "invoices" in data
    assert isinstance(data["invoices"], list)
    invoices = data["invoices"]
    assert len(invoices) > 0
    assert all(isinstance(i, dict) for i in invoices)
    assert all("id" in i for i in invoices)
    assert all("vendor_id" in i for i in invoices)
    assert all("number" in i for i in invoices)
    assert all("date" in i for i in invoices)
    assert all("total" in i for i in invoices)
    assert all("status" in i for i in invoices)

    response2 = client.get("/invoices/?status=processed&start_date=2024-01-01&end_date=2024-12-31", headers=TEST_HEADERS)
    assert response2.status_code == 200
    data2 = response2.json()
    assert "invoices" in data2
    assert isinstance(data2["invoices"], list)
    invoices2 = data2["invoices"]
    assert len(invoices2) > 0
    assert all(isinstance(i, dict) for i in invoices2)

    assert all(i["id"] == "i1" for i in invoices2)
    assert all(i["vendor_id"] == "v1" for i in invoices2)
    assert all(i["number"] == "INV-001" for i in invoices2)
    assert all(i["date"] == "2024-01-15" for i in invoices2)
    assert all(i["total"] == 1234.56 for i in invoices2)
    assert all(i["status"] == "processed" for i in invoices2)

def test_invoice_listing_unauthorized():
    """Test invoice listing without authentication"""
    response = client.get("/invoices/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"

    response2 = client.get("/invoices/?status=processed&start_date=2024-01-01&end_date=2024-12-31")
    assert response2.status_code == 401
    assert response.json()["detail"] == "Missing user-id header"


# TODO: Write tests for the following endpoints:
# 1. GET /vendors/{vendor_id} - Test getting a specific vendor                          - DONE
# 2. GET /vendors/{vendor_id}/addresses - Test getting vendor addresses                 - DONE
# 3. GET /materials/ - Test material listing with pagination and filtering              - DONE
# 4. GET /invoices/ - Test invoice listing with date and status filters                 - DONE
# 5. GET /invoices/{invoice_id} - Test getting specific invoice                         - DONE
# 6. GET /invoices/{invoice_id}/line-items - Test getting invoice line items            - DONE
# 7. GET /projects/ - Test project listing                                              - DONE
# 8. GET /projects/{project_id}/invoices - Test getting project invoices                - DONE
# 9. GET /analytics/spend-by-vendor - Test vendor spending analytics                    - DONE
# 10. GET /analytics/spend-by-category - Test category spending analytics               - DONE
# 11. GET /analytics/monthly-spend - Test monthly spending trends                       - DONE
# 12. GET /materials/price-history/{material_id} - Test material price history          - DONE
# 13. GET /vendors/{vendor_id}/payment-terms - Test vendor payment terms                - DONE
# 14. GET /materials/low-stock - Test low stock materials endpoint                      - DONE

# For each endpoint, remember to test:
# - Successful responses
# - Authentication requirements
# - Error cases (404, invalid params, etc.)
# - Query parameter variations
# - Response data structure and content 