from fastapi import FastAPI, UploadFile, File, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Image Upload App")

# Create an uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.post(os.getenv("UPLOAD_PATH", "/upload"))
async def upload_image(file: UploadFile = File(...)):
    """Uploads an image to the server."""
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "message": "Image uploaded successfully", 
        "filename": unique_filename,
        "url": f"/uploads/{unique_filename}"
    }

@app.get("/")
async def list_images(request: Request, sort: Literal["latest", "oldest"] = Query("latest", description="Sort order: 'latest' or 'oldest'")):
    """Renders a HTML UI displaying all uploaded images."""
    images_data = []
    
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            timestamp = os.path.getmtime(file_path)
            images_data.append({
                "filename": filename,
                "url": f"/uploads/{filename}",
                "timestamp": timestamp,
                "upload_endpoint": os.getenv("UPLOAD_PATH", "/upload")
            })
            
    is_reverse = True if sort == "latest" else False
    images_data.sort(key=lambda x: x["timestamp"], reverse=is_reverse)
    
    # Render the Jinja template using explicit keyword arguments
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "images": images_data,
            "sort": sort
        }
    )

@app.get("/latest-image")
async def get_latest_image(request: Request):
    """
    Renders an HTML UI displaying only the single most recently uploaded image.
    """
    latest_file = None
    max_time = -1
    
    # Scan the directory to find the file with the highest modification time
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if os.path.isfile(file_path):
            timestamp = os.path.getmtime(file_path)
            if timestamp > max_time:
                max_time = timestamp
                latest_file = filename
                
    # Prepare the data if a file was found
    image_data = None
    if latest_file:
        image_data = {
            "filename": latest_file,
            "url": f"/uploads/{latest_file}",
            "timestamp": max_time
        }
        
    # Render the Jinja template and pass the single image
    return templates.TemplateResponse(
        request=request,
        name="latest.html", 
        context={
            "image": image_data
        }
    )