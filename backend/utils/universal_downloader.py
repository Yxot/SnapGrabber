import requests
import re
import asyncio
import os
import json
from urllib.parse import urlparse, quote

async def download(url):
    """
    Universal social media downloader using RapidAPI
    Supports: TikTok, Instagram, Facebook, Twitter, YouTube, Reddit, Pinterest, and more
    """
    try:
        # Create downloads directory
        downloads_dir = "downloads"
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        
        # RapidAPI configuration
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com'
        
        # API endpoint
        api_url = f"https://{rapidapi_host}/"
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {
            'Userinfo': url
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
        if not data or 'error' in data:
            return {"error": f"API error: {data.get('error', 'Unknown error')}"}
        
        # Extract platform from URL
        platform = detect_platform(url)
        
        # Generate filename
        video_id = extract_video_id(url, platform)
        video_filename = f"{platform}_{video_id}.mp4"
        video_path = os.path.join(downloads_dir, video_filename)
        
        # Extract video URL from response
        video_url = extract_video_url(data, platform)
        
        if not video_url:
            return {"error": "No video URL found in API response"}
        
        # Download the video
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
                "title": extract_title(data, platform),
                "platform": platform,
                "video_id": video_id
            }
        else:
            return {"error": f"Failed to download video file: {video_response.status_code}"}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

def detect_platform(url):
    """Detect the platform from the URL"""
    url_lower = url.lower()
    
    if 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'facebook.com' in url_lower:
        return 'facebook'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'reddit.com' in url_lower:
        return 'reddit'
    elif 'pinterest.com' in url_lower:
        return 'pinterest'
    elif 'pinterest.com' in url_lower:
        return 'pinterest'
    elif 'snapchat.com' in url_lower:
        return 'snapchat'
    elif 'vimeo.com' in url_lower:
        return 'vimeo'
    elif 'bilibili.com' in url_lower:
        return 'bilibili'
    elif 'dailymotion.com' in url_lower:
        return 'dailymotion'
    elif 'imgur.com' in url_lower:
        return 'imgur'
    elif 'ifunny.co' in url_lower:
        return 'ifunny'
    elif 'izlesene.com' in url_lower:
        return 'izlesene'
    elif 'kuaishou.com' in url_lower:
        return 'kuaishou'
    elif 'douyin.com' in url_lower:
        return 'douyin'
    elif 'capcut.com' in url_lower:
        return 'capcut'
    elif 'threads.net' in url_lower:
        return 'threads'
    elif 'espn.com' in url_lower:
        return 'espn'
    elif 'imdb.com' in url_lower:
        return 'imdb'
    else:
        return 'unknown'

def extract_video_id(url, platform):
    """Extract video ID from URL based on platform"""
    try:
        if platform == 'tiktok':
            match = re.search(r'/video/(\d+)', url)
            return match.group(1) if match else 'unknown'
        elif platform == 'instagram':
            match = re.search(r'/p/([^/]+)', url)
            return match.group(1) if match else 'unknown'
        elif platform == 'youtube':
            match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?]+)', url)
            return match.group(1) if match else 'unknown'
        elif platform == 'twitter':
            match = re.search(r'/status/(\d+)', url)
            return match.group(1) if match else 'unknown'
        elif platform == 'reddit':
            match = re.search(r'/comments/[^/]+/([^/]+)', url)
            return match.group(1) if match else 'unknown'
        else:
            # For other platforms, use a hash of the URL
            import hashlib
            return hashlib.md5(url.encode()).hexdigest()[:8]
    except:
        return 'unknown'

def extract_video_url(data, platform):
    """Extract video URL from API response"""
    try:
        # The API response structure may vary, so we'll try different paths
        if isinstance(data, dict):
            # Try common response patterns
            if 'video_url' in data:
                return data['video_url']
            elif 'url' in data:
                return data['url']
            elif 'download_url' in data:
                return data['download_url']
            elif 'media' in data and isinstance(data['media'], list) and len(data['media']) > 0:
                return data['media'][0].get('url') or data['media'][0].get('video_url')
            elif 'data' in data:
                return extract_video_url(data['data'], platform)
        
        # If it's a list, try the first item
        elif isinstance(data, list) and len(data) > 0:
            return extract_video_url(data[0], platform)
        
        return None
    except:
        return None

def extract_title(data, platform):
    """Extract title from API response"""
    try:
        if isinstance(data, dict):
            if 'title' in data:
                return data['title']
            elif 'caption' in data:
                return data['caption']
            elif 'description' in data:
                return data['description']
            elif 'data' in data:
                return extract_title(data['data'], platform)
        
        return f"{platform.title()} Video"
    except:
        return f"{platform.title()} Video" 