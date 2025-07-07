from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from backend.utils import tiktok, youtube, instagram

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
if os.path.exists("downloads"):
    app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

class DownloadRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "SnapGrabber API is running"}

@app.post("/download")
async def download_video(req: DownloadRequest):
    url = req.url.strip()
    
    # Validate URL
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Detect platform and download
    try:
        if 'tiktok.com' in url:
            result = await tiktok.download(url)
        elif 'youtube.com' in url or 'youtu.be' in url:
            result = await youtube.download(url)
        elif 'instagram.com' in url:
            result = await instagram.download(url)
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform. Please use TikTok, YouTube, or Instagram URLs.")
        
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