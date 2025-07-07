from http.server import BaseHTTPRequestHandler
import json
import requests
import re
import os
import asyncio
from urllib.parse import urlparse

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
    else:
        return 'unknown'

def download_video(url):
    """Download video using RapidAPI"""
    try:
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
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code != 200:
            return {"error": f"API request failed with status {response.status_code}"}
        
        data = response.json()
        
        # Check if the API response is successful
        if not data or 'error' in data:
            return {"error": f"API error: {data.get('error', 'Unknown error')}"}
        
        # Extract platform from URL
        platform = detect_platform(url)
        
        # Extract video URL from response
        video_url = None
        if isinstance(data, dict):
            if 'video_url' in data:
                video_url = data['video_url']
            elif 'url' in data:
                video_url = data['url']
            elif 'download_url' in data:
                video_url = data['download_url']
        
        if not video_url:
            return {"error": "No video URL found in API response"}
        
        return {
            "download_url": video_url,
            "title": data.get('title', f'{platform.title()} Video'),
            "platform": platform
        }
        
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Parse JSON data
        data = json.loads(post_data.decode('utf-8'))
        url = data.get('url', '').strip()
        
        # Validate URL
        if not url:
            self.send_error_response("URL is required")
            return
        
        # Download the video
        result = download_video(url)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {"error": message}
        self.wfile.write(json.dumps(error_response).encode()) 