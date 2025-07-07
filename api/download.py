from http.server import BaseHTTPRequestHandler
import json
import requests
import re
import os
from urllib.parse import urlparse, parse_qs

def detect_platform(url):
    """Detect the platform from the URL"""
    url_lower = url.lower()
    
    if 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    else:
        return 'unknown'

def download_tiktok(url):
    """Download TikTok video using RapidAPI"""
    try:
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {'url': url}
        
        response = requests.get(f'https://{rapidapi_host}/v1/index', headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'nwm_video_url' in data['data']:
                return {
                    "download_url": data['data']['nwm_video_url'],
                    "title": data['data'].get('title', 'TikTok Video'),
                    "platform": "tiktok",
                    "success": True
                }
        
        return {"error": "Failed to extract TikTok video", "success": False}
        
    except Exception as e:
        return {"error": f"TikTok download error: {str(e)}", "success": False}

def download_instagram(url):
    """Download Instagram video using RapidAPI"""
    try:
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {'Userinfo': url}
        
        response = requests.get(f'https://{rapidapi_host}/', headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Try different response formats
            video_url = None
            if isinstance(data, dict):
                if 'video_url' in data:
                    video_url = data['video_url']
                elif 'url' in data:
                    video_url = data['url']
                elif 'media' in data and isinstance(data['media'], list) and len(data['media']) > 0:
                    video_url = data['media'][0].get('url') or data['media'][0].get('video_url')
            
            if video_url:
                return {
                    "download_url": video_url,
                    "title": data.get('title', data.get('caption', 'Instagram Video')),
                    "platform": "instagram",
                    "success": True
                }
        
        return {"error": "Failed to extract Instagram video", "success": False}
        
    except Exception as e:
        return {"error": f"Instagram download error: {str(e)}", "success": False}

def download_youtube(url):
    """Download YouTube video using RapidAPI"""
    try:
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'youtube-video-download-info.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {'url': url}
        
        response = requests.get(f'https://{rapidapi_host}/dl', headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'link' in data and len(data['link']) > 0:
                # Get the highest quality video
                video_url = data['link'][0]['url']
                return {
                    "download_url": video_url,
                    "title": data.get('title', 'YouTube Video'),
                    "platform": "youtube",
                    "success": True
                }
        
        return {"error": "Failed to extract YouTube video", "success": False}
        
    except Exception as e:
        return {"error": f"YouTube download error: {str(e)}", "success": False}

def download_video(url):
    """Main download function that routes to platform-specific handlers"""
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return {"error": "Invalid URL format. Please provide a valid URL starting with http:// or https://", "success": False}
        
        # Detect platform
        platform = detect_platform(url)
        if platform == 'unknown':
            return {"error": "Unsupported platform. Please use Instagram, TikTok, or YouTube URLs only.", "success": False}
        
        # Route to platform-specific downloader
        if platform == 'tiktok':
            return download_tiktok(url)
        elif platform == 'instagram':
            return download_instagram(url)
        elif platform == 'youtube':
            return download_youtube(url)
        else:
            return {"error": "Platform not supported", "success": False}
            
    except Exception as e:
        return {"error": f"Download failed: {str(e)}", "success": False}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Test endpoint to check if API is working"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "API is working", 
            "message": "SnapGrabber API is online",
            "supported_platforms": ["tiktok", "instagram", "youtube"],
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response("No data provided")
                return
                
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error_response("Invalid JSON data")
                return
                
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
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Server error: {str(e)}")  # Add logging
            self.send_error_response(f"Server error: {str(e)}")
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {"error": message, "success": False}
        self.wfile.write(json.dumps(error_response).encode()) 