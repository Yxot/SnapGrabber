from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.utils import tiktok, youtube, instagram

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str

@app.post("/download")
async def download_video(req: DownloadRequest):
    url = req.url
    if 'tiktok.com' in url:
        return await tiktok.download(url)
    elif 'youtube.com' in url or 'youtu.be' in url:
        return await youtube.download(url)
    elif 'instagram.com' in url:
        return await instagram.download(url)
    else:
        return {"error": "Unsupported URL"} 