from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import sys

# Add the current directory to Python path for Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.utils import universal_downloader
except ImportError:
    # Fallback for Vercel deployment
    from utils import universal_downloader

app = FastAPI(title="SnapGrabber API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving downloads
downloads_dir = "downloads"
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

# Mount static files
app.mount("/downloads", StaticFiles(directory=downloads_dir), name="downloads")

class DownloadRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "SnapGrabber API is running", "status": "healthy"}

@app.get("/api/")
async def api_root():
    return {"message": "SnapGrabber API is running", "status": "healthy"}

@app.post("/api/download")
async def download_video_api(req: DownloadRequest):
    return await download_video(req)

@app.post("/download")
async def download_video(req: DownloadRequest):
    url = req.url.strip()
    
    # Validate URL
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Use universal downloader for all platforms
    try:
        result = await universal_downloader.download(url)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SnapGrabber"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "service": "SnapGrabber"}

@app.get("/supported-platforms")
async def get_supported_platforms():
    """Return list of supported platforms"""
    platforms = [
        "TikTok", "Instagram", "Facebook", "Twitter", "YouTube", 
        "Reddit", "Pinterest", "Snapchat", "Vimeo", "Bilibili", 
        "Dailymotion", "Imgur", "iFunny", "Izlesene", "Kuaishou", 
        "Douyin", "CapCut", "Threads", "ESPN", "IMDB"
    ]
    return {"platforms": platforms}

@app.get("/api/supported-platforms")
async def api_get_supported_platforms():
    """Return list of supported platforms"""
    return await get_supported_platforms()

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "message": "Check the API documentation"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Please try again later"}
    ) 