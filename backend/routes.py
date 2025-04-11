from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import os
import json
from pathlib import Path
import random

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
app = FastAPI()

# Constants
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif"}

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)

# Mock Data
MOCK_VENDORS = [
    {"id": "v1", "name": "Home Depot", "email": "orders@homedepot.com", "phone": "1-800-466-3337"},
    {"id": "v2", "name": "Lowes", "email": "orders@lowes.com", "phone": "1-800-445-6937"},
    {"id": "v3", "name": "Ferguson", "email": "orders@ferguson.com", "phone": "1-800-634-0348"},
]

MOCK_ADDRESSES = [
    {"id": "a1", "vendor_id": "v1", "street": "123 Main St", "city": "Atlanta", "state": "GA", "zip": "30301"},
    {"id": "a2", "vendor_id": "v1", "street": "456 Oak Ave", "city": "Miami", "state": "FL", "zip": "33101"},
    {"id": "a3", "vendor_id": "v2", "street": "789 Pine Rd", "city": "Dallas", "state": "TX", "zip": "75201"},
]

MOCK_MATERIALS = [
    {"id": "m1", "name": "2x4 Lumber", "category": "Wood", "unit": "piece"},
    {"id": "m2", "name": "Concrete Mix", "category": "Concrete", "unit": "bag"},
    {"id": "m3", "name": "PVC Pipe 2\"", "category": "Plumbing", "unit": "foot"},
]

MOCK_INVOICES = [
    {
        "id": "i1",
        "vendor_id": "v1",
        "number": "INV-001",
        "date": "2024-01-15",
        "total": 1234.56,
        "status": "processed"
    },
    {
        "id": "i2",
        "vendor_id": "v2",
        "number": "INV-002",
        "date": "2024-01-16",
        "total": 2345.67,
        "status": "processing"
    },
]

MOCK_LINE_ITEMS = [
    {"id": "l1", "invoice_id": "i1", "material_id": "m1", "quantity": 100, "unit_price": 5.99},
    {"id": "l2", "invoice_id": "i1", "material_id": "m2", "quantity": 50, "unit_price": 12.99},
    {"id": "l3", "invoice_id": "i2", "material_id": "m3", "quantity": 200, "unit_price": 3.99},
]

MOCK_PROJECTS = [
    {"id": "p1", "name": "Downtown High-rise", "address": "100 Peachtree St, Atlanta, GA"},
    {"id": "p2", "name": "Suburban Mall", "address": "200 Mall Road, Miami, FL"},
]

def get_user_id(headers: Dict[str, str]) -> str:
    """Get user ID from request headers"""
    user_id = headers.get("user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user-id header")
    return user_id

def save_file(file_content: bytes, filename: str, user_id: str) -> str:
    """Save file to user's directory"""
    user_dir = UPLOAD_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    file_path = user_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    return str(file_path)

def get_file_info(file_path: str) -> dict:
    """Get file metadata"""
    return {
        "path": file_path,
        "size": os.path.getsize(file_path),
        "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
    }

async def process_files_generator(files: List[tuple], user_id: str):
    """Process uploaded files and yield progress updates"""
    processed_files = []
    
    for filename, file_content in files:
        try:
            file_path = save_file(file_content, filename, user_id)
            processed_files.append({
                "filename": filename,
                "status": "completed",
                "message": "File processed successfully"
            })
            
            progress_data = {
                "type": "progress",
                "current_file": filename,
                "total_files": len(files),
                "processed_files": processed_files
            }
            yield json.dumps(progress_data) + "\n"
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            processed_files.append({
                "filename": filename,
                "status": "failed",
                "message": str(e)
            })
    
    complete_data = {
        "type": "complete",
        "status": "success",
        "files": processed_files
    }
    yield json.dumps(complete_data) + "\n"

@app.post("/upload/")
async def upload_files(
    files: List[UploadFile] = File(...),
    request: Request = None
):
    """Handle file uploads with real-time progress updates"""
    try:
        user_id = get_user_id(request.headers)
        
        file_contents = []
        for file in files:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds maximum size of {MAX_FILE_SIZE/1024/1024}MB"
                )
            file_contents.append((file.filename, content))
        
        generator = process_files_generator(file_contents, user_id)
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/")
async def list_files(
    request: Request,
    page: int = 1,
    page_size: int = 10
):
    """List all files for a user with pagination"""
    try:
        user_id = get_user_id(request.headers)
        user_dir = UPLOAD_DIR / user_id
        
        if not user_dir.exists():
            return {
                "files": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        all_files = []
        for file_path in user_dir.glob("*"):
            if file_path.is_file():
                all_files.append(get_file_info(str(file_path)))
        
        # Apply pagination
        total = len(all_files)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_files = all_files[start_idx:end_idx]
        
        return {
            "files": paginated_files,
            "total": total,
            "page": page,
            "page_size": page_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vendors/")
async def list_vendors(request: Request, search: Optional[str] = None):
    """List all vendors with optional search"""
    get_user_id(request.headers)  # Verify auth
    vendors = MOCK_VENDORS
    if search:
        vendors = [v for v in vendors if search.lower() in v["name"].lower()]
    return {"vendors": vendors}

@app.get("/vendors/{vendor_id}")
async def get_vendor(vendor_id: str, request: Request):
    """Get vendor details"""
    get_user_id(request.headers)
    vendor = next((v for v in MOCK_VENDORS if v["id"] == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@app.get("/vendors/{vendor_id}/addresses")
async def get_vendor_addresses(vendor_id: str, request: Request):
    """Get addresses for a vendor"""
    get_user_id(request.headers)
    addresses = [a for a in MOCK_ADDRESSES if a["vendor_id"] == vendor_id]
    return {"addresses": addresses}

@app.get("/materials/")
async def list_materials(
    request: Request,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """List materials with filtering and pagination"""
    get_user_id(request.headers)
    materials = MOCK_MATERIALS
    if category:
        materials = [m for m in materials if m["category"] == category]
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "materials": materials[start:end],
        "total": len(materials),
        "page": page,
        "page_size": page_size
    }

@app.get("/invoices/")
async def list_invoices(
    request: Request,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """List invoices with filtering"""
    get_user_id(request.headers)
    invoices = MOCK_INVOICES
    if status:
        invoices = [i for i in invoices if i["status"] == status]
    if start_date:
        invoices = [i for i in invoices if i["date"] >= start_date]
    if end_date:
        invoices = [i for i in invoices if i["date"] <= end_date]
    return {"invoices": invoices}

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, request: Request):
    """Get invoice details"""
    get_user_id(request.headers)
    invoice = next((i for i in MOCK_INVOICES if i["id"] == invoice_id), None)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/invoices/{invoice_id}/line-items")
async def get_invoice_line_items(invoice_id: str, request: Request):
    """Get line items for an invoice"""
    get_user_id(request.headers)
    items = [i for i in MOCK_LINE_ITEMS if i["invoice_id"] == invoice_id]
    return {"line_items": items}

@app.get("/projects/")
async def list_projects(request: Request):
    """List all projects"""
    get_user_id(request.headers)
    return {"projects": MOCK_PROJECTS}

@app.get("/projects/{project_id}/invoices")
async def get_project_invoices(project_id: str, request: Request):
    """Get invoices for a project"""
    get_user_id(request.headers)
    # Mock relationship between projects and invoices
    project_invoices = MOCK_INVOICES[:1] if project_id == "p1" else MOCK_INVOICES[1:]
    return {"invoices": project_invoices}

@app.get("/analytics/spend-by-vendor")
async def get_spend_by_vendor(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get spending analytics by vendor"""
    get_user_id(request.headers)
    return {
        "spend_by_vendor": [
            {"vendor_id": "v1", "vendor_name": "Home Depot", "total_spend": 50000.00},
            {"vendor_id": "v2", "vendor_name": "Lowes", "total_spend": 35000.00},
        ]
    }

@app.get("/analytics/spend-by-category")
async def get_spend_by_category(request: Request):
    """Get spending analytics by category"""
    get_user_id(request.headers)
    return {
        "spend_by_category": [
            {"category": "Wood", "total_spend": 25000.00},
            {"category": "Concrete", "total_spend": 30000.00},
            {"category": "Plumbing", "total_spend": 15000.00},
        ]
    }

@app.get("/analytics/monthly-spend")
async def get_monthly_spend(request: Request):
    """Get monthly spending trends"""
    get_user_id(request.headers)
    return {
        "monthly_spend": [
            {"month": "2024-01", "total_spend": 45000.00},
            {"month": "2024-02", "total_spend": 52000.00},
            {"month": "2024-03", "total_spend": 38000.00},
        ]
    }

@app.get("/materials/price-history/{material_id}")
async def get_material_price_history(material_id: str, request: Request):
    """Get price history for a material"""
    get_user_id(request.headers)
    return {
        "material_id": material_id,
        "price_history": [
            {"date": "2024-01-15", "price": 5.99},
            {"date": "2024-02-15", "price": 6.49},
            {"date": "2024-03-15", "price": 6.29},
        ]
    }

@app.get("/vendors/{vendor_id}/payment-terms")
async def get_vendor_payment_terms(vendor_id: str, request: Request):
    """Get payment terms for a vendor"""
    get_user_id(request.headers)
    return {
        "vendor_id": vendor_id,
        "payment_terms": {
            "net_days": 30,
            "discount_percent": 2.0,
            "discount_days": 10,
            "credit_limit": 50000.00
        }
    }

@app.get("/materials/low-stock")
async def get_low_stock_materials(request: Request):
    """Get materials with low stock"""
    get_user_id(request.headers)
    return {
        "low_stock_materials": [
            {"material_id": "m1", "name": "2x4 Lumber", "current_stock": 50, "reorder_point": 100},
            {"material_id": "m2", "name": "Concrete Mix", "current_stock": 25, "reorder_point": 40},
        ]
    } 