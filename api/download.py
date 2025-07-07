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
    """Download YouTube video using a more reliable API"""
    try:
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'youtube-dl-api.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {'url': url}
        
        print(f"Trying YouTube API with host: {rapidapi_host}")
        response = requests.get(f'https://{rapidapi_host}/dl', headers=headers, params=params, timeout=30)
        
        print(f"YouTube API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"YouTube API Data: {data}")
            
            # Try to extract video URL from response
            video_url = None
            if isinstance(data, dict):
                if 'url' in data:
                    video_url = data['url']
                elif 'link' in data:
                    video_url = data['link']
                elif 'download_url' in data:
                    video_url = data['download_url']
                elif 'video_url' in data:
                    video_url = data['video_url']
                elif 'formats' in data and isinstance(data['formats'], list) and len(data['formats']) > 0:
                    # Get the best quality format
                    video_url = data['formats'][0].get('url')
            
            if video_url:
                return {
                    "download_url": video_url,
                    "title": data.get('title', 'YouTube Video'),
                    "platform": "youtube",
                    "success": True
                }
        
        # If the above fails, try a different approach
        return download_youtube_simple(url)
        
    except Exception as e:
        print(f"YouTube download error: {str(e)}")
        return download_youtube_simple(url)

def download_youtube_simple(url):
    """Simple YouTube download using a different API"""
    try:
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'youtube-mp36.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {'url': url}
        
        print(f"Trying simple YouTube API with host: {rapidapi_host}")
        response = requests.get(f'https://{rapidapi_host}/dl', headers=headers, params=params, timeout=30)
        
        print(f"Simple YouTube API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Simple YouTube API Data: {data}")
            
            if 'link' in data:
                return {
                    "download_url": data['link'],
                    "title": data.get('title', 'YouTube Video'),
                    "platform": "youtube",
                    "success": True
                }
        
        # If all APIs fail, return a helpful error
        return {"error": "YouTube video download is temporarily unavailable. Please try again later.", "success": False}
        
    except Exception as e:
        print(f"Simple YouTube download error: {str(e)}")
        return {"error": "YouTube download service is currently unavailable", "success": False}

def download_video(url):
    """Main download function that routes to platform-specific handlers"""
    try:
        print(f"Starting download for URL: {url}")
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return {"error": "Invalid URL format. Please provide a valid URL starting with http:// or https://", "success": False}
        
        # Detect platform
        platform = detect_platform(url)
        print(f"Detected platform: {platform}")
        
        if platform == 'unknown':
            return {"error": "Unsupported platform. Please use Instagram, TikTok, or YouTube URLs only.", "success": False}
        
        # Route to platform-specific downloader
        if platform == 'tiktok':
            print("Routing to TikTok downloader")
            return download_tiktok(url)
        elif platform == 'instagram':
            print("Routing to Instagram downloader")
            return download_instagram(url)
        elif platform == 'youtube':
            print("Routing to YouTube downloader")
            return download_youtube(url)
        else:
            return {"error": "Platform not supported", "success": False}
            
    except Exception as e:
        print(f"Main download error: {str(e)}")
        return {"error": f"Download failed: {str(e)}", "success": False}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Test endpoint to check if API is working"""
        # Check if this is a test request
        if self.path.startswith('/api/download/test'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Test the YouTube API directly
            test_url = "https://youtu.be/ooMsDvZUrAg?si=qf2SHRR9RXdCjIUV"
            try:
                result = download_youtube(test_url)
                response = {
                    "status": "Test completed",
                    "test_url": test_url,
                    "result": result,
                    "message": "YouTube API test completed"
                }
            except Exception as e:
                response = {
                    "status": "Test failed",
                    "test_url": test_url,
                    "error": str(e),
                    "message": "YouTube API test failed"
                }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Regular status endpoint
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "API is working", 
            "message": "SnapGrabber API is online",
            "supported_platforms": ["tiktok", "instagram", "youtube"],
            "version": "1.0.0",
            "test_endpoint": "/api/download/test"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        try:
            print("Received POST request")
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                print("No content length provided")
                self.send_error_response("No data provided")
                return
                
            post_data = self.rfile.read(content_length)
            print(f"Received data: {post_data.decode('utf-8')}")
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                self.send_error_response("Invalid JSON data")
                return
                
            url = data.get('url', '').strip()
            print(f"Extracted URL: {url}")
            
            # Validate URL
            if not url:
                print("No URL provided")
                self.send_error_response("URL is required")
                return
            
            # Download the video
            print("Starting video download")
            result = download_video(url)
            print(f"Download result: {result}")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_json = json.dumps(result)
            print(f"Sending response: {response_json}")
            self.wfile.write(response_json.encode())
            
        except Exception as e:
            print(f"Server error in POST handler: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_error_response(f"Server error: {str(e)}")
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
        self.end_headers()
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {"error": message, "success": False}
        self.wfile.write(json.dumps(error_response).encode()) 