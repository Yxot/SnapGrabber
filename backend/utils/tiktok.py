import requests
import re
import asyncio
import os
import json
from urllib.parse import urlparse

async def download(url):
    """
    TikTok video downloader using RapidAPI
    """
    try:
        # Clean the URL and extract video ID
        if 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
            # Follow redirects to get the actual URL
            response = requests.get(url, allow_redirects=True)
            url = response.url
        
        # Extract video ID from URL
        video_id_match = re.search(r'/video/(\d+)', url)
        if not video_id_match:
            return {"error": "Invalid TikTok URL format"}
        
        video_id = video_id_match.group(1)
        
        # Create downloads directory
        downloads_dir = "downloads"
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        
        # RapidAPI configuration
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'tiktok-video-no-watermark2.p.rapidapi.com'
        
        # API endpoint for video download
        api_url = f"https://{rapidapi_host}/video/info"
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {
            'video_id': video_id
        }
        
        # Make API request
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.get(api_url, headers=headers, params=params)
        )
        
        if response.status_code != 200:
            return {"error": f"API request failed with status {response.status_code}"}
        
        data = response.json()
        
        # Check if the API response is successful
        if data.get('code') != 0:
            return {"error": f"API error: {data.get('msg', 'Unknown error')}"}
        
        # Extract video URL from response
        video_data = data.get('data', {})
        video_url = video_data.get('play')
        
        if not video_url:
            return {"error": "No video URL found in API response"}
        
        # Download the video
        video_filename = f"tiktok_{video_id}.mp4"
        video_path = os.path.join(downloads_dir, video_filename)
        
        # Download video file
        video_response = await loop.run_in_executor(
            None, 
            lambda: requests.get(video_url, stream=True)
        )
        
        if video_response.status_code == 200:
            with open(video_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return {
                "download_url": f"/downloads/{video_filename}",
                "title": video_data.get('title', f'TikTok Video {video_id}'),
                "author": video_data.get('author', {}).get('nickname', 'Unknown'),
                "duration": video_data.get('duration', 0),
                "platform": "TikTok",
                "video_id": video_id
            }
        else:
            return {"error": f"Failed to download video file: {video_response.status_code}"}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"TikTok download failed: {str(e)}"}

# Alternative method using direct video URL extraction
async def download_direct(url):
    """
    Alternative TikTok downloader that extracts video URL directly
    """
    try:
        # This method would parse the TikTok page HTML to extract video URLs
        # Useful as a fallback if the API fails
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: requests.get(url, headers=headers)
        )
        
        if response.status_code != 200:
            return {"error": "Failed to fetch TikTok page"}
        
        # Extract video URL from page source
        # This is a simplified approach - in production you'd need more robust parsing
        video_url_match = re.search(r'"playAddr":"([^"]+)"', response.text)
        
        if video_url_match:
            video_url = video_url_match.group(1).replace('\\u002F', '/')
            # Download logic would go here
            return {"error": "Direct download method needs implementation"}
        else:
            return {"error": "Could not extract video URL from page"}
        
    except Exception as e:
        return {"error": f"Direct download failed: {str(e)}"}

# Alternative implementation using a third-party service (example)
async def download_with_service(url):
    """
    Example implementation using a hypothetical TikTok download service
    """
    try:
        # This would be replaced with actual service API calls
        service_url = "https://api.tiktok-downloader.com/download"
        params = {"url": url}
        
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: requests.get(service_url, params=params)
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return {
                    "download_url": data["download_url"],
                    "title": data.get("title", "TikTok Video"),
                    "platform": "TikTok"
                }
        
        return {"error": "Failed to download TikTok video"}
        
    except Exception as e:
        return {"error": f"TikTok download failed: {str(e)}"} 