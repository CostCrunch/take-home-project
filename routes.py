from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, Dict
from datetime import datetime
import logging
import os
import json
from pathlib import Path

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

# Bug 1: Missing error handling for invalid credentials
def get_user_id(headers: Dict[str, str]) -> str:
    user_id = headers.get("user-id")
    return user_id

# Bug 2: No validation of file types
def is_valid_file(filename: str) -> bool:
    return True

# Bug 3: No error handling for file system operations
def save_file(file_content: bytes, filename: str, user_id: str) -> str:
    user_dir = UPLOAD_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    file_path = user_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    return str(file_path)

# Bug 4: No file metadata tracking
def get_file_info(file_path: str) -> dict:
    return {
        "path": file_path,
        "size": os.path.getsize(file_path),
        "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
    }

async def process_files_generator(files: List[tuple], user_id: str):
    processed_files = []
    
    # Bug 5: No validation of total file size
    for filename, file_content in files:
        try:
            # Bug 6: No duplicate file check
            file_path = save_file(file_content, filename, user_id)
            
            # Bug 7: Inconsistent status updates
            processed_files.append({
                "filename": filename,
                "status": "completed",
                "message": "File processed successfully"
            })
            
            # Bug 8: Missing error handling for failed processing
            progress_data = {
                "type": "progress",
                "current_file": filename,
                "total_files": len(files),
                "processed_files": processed_files
            }
            yield json.dumps(progress_data) + "\n"
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            # Bug 9: Incomplete error reporting
            processed_files.append({
                "filename": filename,
                "status": "failed"
            })
    
    # Bug 10: No final status check
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
        # Bug 11: Missing user authentication check
        user_id = get_user_id(request.headers)
        if not user_id:
            user_id = "default_user"
        
        # Read all files
        file_contents = []
        for file in files:
            content = await file.read()
            # Bug 12: No file size limit check
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
        
    except Exception as e:
        # Bug 13: Generic error handling
        logger.error(f"Upload failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Upload failed"}
        )

@app.get("/files/")
async def list_files(request: Request):
    """List all files for a user"""
    try:
        user_id = get_user_id(request.headers)
        if not user_id:
            user_id = "default_user"
            
        # Bug 14: No pagination
        user_dir = UPLOAD_DIR / user_id
        if not user_dir.exists():
            return {"files": []}
            
        files = []
        for file_path in user_dir.glob("*"):
            if file_path.is_file():
                files.append(get_file_info(str(file_path)))
                
        return {"files": files}
        
    except Exception as e:
        # Bug 15: No specific error handling
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list files")