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

def download_with_cobalt(url, quality=None, audio_only=False):
    """Universal download using Cobalt API"""
    try:
        cobalt_api = "http://localhost:3000/api/download"
        params = {"url": url}
        if quality is not None:
            params["quality"] = quality
        if audio_only:
            params["audio_only"] = "true"
        response = requests.get(cobalt_api, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("files"):
                # Prefer best file or let frontend choose
                best_file = data["files"][0]
                return {
                    "download_url": best_file["url"],
                    "title": data.get("title", "Video"),
                    "platform": data.get("extractor", "unknown"),
                    "files": data["files"],
                    "success": True
                }
            else:
                return {"error": "No downloadable file found.", "success": False}
        else:
            return {"error": f"Cobalt API error: {response.status_code} {response.text}", "success": False}
    except Exception as e:
        return {"error": f"Cobalt download error: {str(e)}", "success": False}

def download_video(url, quality=None, audio_only=False):
    """Main download function using Cobalt API only"""
    try:
        print(f"Starting Cobalt download for URL: {url}")
        if not url.startswith(('http://', 'https://')):
            return {"error": "Invalid URL format. Please provide a valid URL starting with http:// or https://", "success": False}
        return download_with_cobalt(url, quality, audio_only)
    except Exception as e:
        print(f"Main download error: {str(e)}")
        return {"error": f"Download failed: {str(e)}", "success": False}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for API status and quality options"""
        # Check if this is a test request
        if self.path.startswith('/api/download/test'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Test the YouTube API directly
            test_url = "https://youtu.be/ooMsDvZUrAg?si=qf2SHRR9RXdCjIUV"
            try:
                result = download_video(test_url)
                response = {
                    "status": "Test completed",
                    "test_url": test_url,
                    "result": result,
                    "message": "YouTube API test completed",
                    "api_host": "youtube-api49.p.rapidapi.com"
                }
            except Exception as e:
                response = {
                    "status": "Test failed",
                    "test_url": test_url,
                    "error": str(e),
                    "message": "YouTube API test failed",
                    "api_host": "youtube-api49.p.rapidapi.com"
                }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Check if this is a qualities request
        if self.path.startswith('/api/download/qualities'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Parse URL parameters
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            url = params.get('url', [None])[0]
            
            if not url:
                response = {"error": "URL parameter is required", "success": False}
            else:
                # Get qualities for the URL
                platform = detect_platform(url)
                if platform == 'youtube':
                    response = get_youtube_qualities(url)
                else:
                    response = {"error": "Quality selection only available for YouTube videos", "success": False}
            
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
            "version": "2.0.0",
            "endpoints": {
                "test": "/api/download/test",
                "qualities": "/api/download/qualities?url=YOUR_URL",
                "download": "/api/download (POST)"
            },
            "apis": {
                "youtube": "youtube-api49.p.rapidapi.com",
                "tiktok": "tiktok-max-quality.p.rapidapi.com",
                "instagram": "instagram-api-media-downloader.p.rapidapi.com"
            }
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
            quality = data.get('quality')
            audio_only = data.get('audio_only', False)
            print(f"Extracted URL: {url}")
            print(f"Quality: {quality}")
            print(f"Audio Only: {audio_only}")
            
            # Validate URL
            if not url:
                print("No URL provided")
                self.send_error_response("URL is required")
                return
            
            # Download the video
            print("Starting video download")
            result = download_video(url, quality, audio_only)
            print(f"Download result: {result}")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
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

# For Vercel serverless functions
def lambda_handler(event, context):
    """AWS Lambda handler for Vercel"""
    return handler().do_POST()

# For direct testing
if __name__ == "__main__":
    print("API is ready for testing") 