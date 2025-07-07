import yt_dlp
import asyncio
import os
import re

async def download(url):
    # Create downloads directory if it doesn't exist
    downloads_dir = "downloads"
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    
    ydl_opts = {
        'format': 'best[height<=720]/best',  # Limit to 720p for faster downloads
        'outtmpl': f'{downloads_dir}/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            
            if not info:
                return {"error": "Could not extract video information"}
            
            # Download the video
            await loop.run_in_executor(None, lambda: ydl.download([url]))
            
            # Get the filename
            filename = ydl.prepare_filename(info)
            
            # Clean filename for URL
            safe_filename = re.sub(r'[^\w\-_\.]', '_', os.path.basename(filename))
            
            # Return the download URL
            return {
                "download_url": f"/downloads/{safe_filename}",
                "title": info.get('title', 'Unknown'),
                "duration": info.get('duration', 0),
                "platform": "YouTube"
            }
            
    except Exception as e:
        error_msg = str(e)
        if "Video unavailable" in error_msg:
            return {"error": "This video is not available for download"}
        elif "Private video" in error_msg:
            return {"error": "This is a private video"}
        elif "Age-restricted" in error_msg:
            return {"error": "This video is age-restricted"}
        else:
            return {"error": f"YouTube download failed: {error_msg}"} 