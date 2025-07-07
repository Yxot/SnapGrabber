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
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    else:
        return 'unknown'

def download_video(url):
    """Download video using RapidAPI"""
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return {"error": "Invalid URL format. Please provide a valid URL starting with http:// or https://"}
        
        # Detect platform
        platform = detect_platform(url)
        if platform == 'unknown':
            return {"error": "Unsupported platform. Please use Instagram, TikTok, or YouTube URLs only."}
        
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
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            return {"error": f"API request failed with status {response.status_code}. Please try again."}
        
        data = response.json()
        
        # Check if the API response is successful
        if not data or 'error' in data:
            return {"error": f"API error: {data.get('error', 'Unknown error')}"}
        
        # Extract video URL from response
        video_url = None
        if isinstance(data, dict):
            if 'video_url' in data:
                video_url = data['video_url']
            elif 'url' in data:
                video_url = data['url']
            elif 'download_url' in data:
                video_url = data['download_url']
            elif 'media' in data and isinstance(data['media'], list) and len(data['media']) > 0:
                video_url = data['media'][0].get('url') or data['media'][0].get('video_url')
        
        if not video_url:
            return {"error": "No video URL found in API response. This content might not be available for download."}
        
        # Extract title
        title = data.get('title') or data.get('caption') or data.get('description') or f'{platform.title()} Video'
        
        return {
            "download_url": video_url,
            "title": title,
            "platform": platform,
            "success": True
        }
        
    except requests.exceptions.Timeout:
        return {"error": "Request timeout. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
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
            
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON data")
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}")
    
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
        
        error_response = {"error": message, "success": False}
        self.wfile.write(json.dumps(error_response).encode()) 