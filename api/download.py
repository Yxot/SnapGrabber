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
        # Extract video ID from URL
        video_id = None
        if 'video/' in url:
            video_id = url.split('video/')[-1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=')[-1].split('&')[0]
        
        if not video_id:
            return {"error": "Could not extract video ID from TikTok URL", "success": False}
        
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'tiktok-video-no-watermark2.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        # Use the video download endpoint
        params = {'url': url}
        
        response = requests.get(f'https://{rapidapi_host}/video/by-url', headers=headers, params=params, timeout=30)
        
        print(f"TikTok API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"TikTok API Data: {data}")
            
            # Extract video URL from response
            video_url = None
            if isinstance(data, dict):
                if 'data' in data and 'play' in data['data']:
                    video_url = data['data']['play']
                elif 'video_data' in data and 'play' in data['video_data']:
                    video_url = data['video_data']['play']
                elif 'url' in data:
                    video_url = data['url']
                elif 'download_url' in data:
                    video_url = data['download_url']
            
            if video_url:
                return {
                    "download_url": video_url,
                    "title": data.get('data', {}).get('title', 'TikTok Video'),
                    "platform": "tiktok",
                    "success": True
                }
        
        return {"error": "Failed to extract TikTok video", "success": False}
        
    except Exception as e:
        print(f"TikTok download error: {str(e)}")
        return {"error": f"TikTok download error: {str(e)}", "success": False}

def download_instagram(url):
    """Download Instagram video using RapidAPI"""
    try:
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'instagram-reels-downloader-api.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {'url': url}
        
        response = requests.get(f'https://{rapidapi_host}/download', headers=headers, params=params, timeout=30)
        
        print(f"Instagram API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Instagram API Data: {data}")
            
            # Extract video URL from response
            video_url = None
            if isinstance(data, dict):
                if 'video' in data:
                    video_url = data['video']
                elif 'url' in data:
                    video_url = data['url']
                elif 'download_url' in data:
                    video_url = data['download_url']
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
        print(f"Instagram download error: {str(e)}")
        return {"error": f"Instagram download error: {str(e)}", "success": False}

def download_youtube(url):
    """Download YouTube video using RapidAPI with comprehensive debugging"""
    try:
        print(f"=== YOUTUBE DOWNLOAD DEBUG ===")
        print(f"Input URL: {url}")
        
        # Extract video ID from URL
        video_id = None
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('v=')[-1].split('&')[0]
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        
        print(f"Extracted Video ID: {video_id}")
        
        if not video_id:
            return {"error": "Could not extract video ID from YouTube URL", "success": False}
        
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'youtube-media-downloader.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        # Try multiple endpoints
        endpoints_to_try = [
            {
                'url': f'https://{rapidapi_host}/v2/video/details',
                'params': {
                    'videoId': video_id,
                    'urlAccess': 'normal',
                    'videos': 'auto',
                    'audios': 'auto'
                }
            },
            {
                'url': f'https://{rapidapi_host}/v2/video/details',
                'params': {
                    'videoId': video_id
                }
            },
            {
                'url': f'https://{rapidapi_host}/dl',
                'params': {
                    'url': url
                }
            }
        ]
        
        for i, endpoint in enumerate(endpoints_to_try):
            print(f"\n--- Trying Endpoint {i+1} ---")
            print(f"URL: {endpoint['url']}")
            print(f"Params: {endpoint['params']}")
            
            try:
                response = requests.get(endpoint['url'], headers=headers, params=endpoint['params'], timeout=30)
                print(f"Response Status: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Response Data: {json.dumps(data, indent=2)}")
                    
                    # Try to extract video URL from response
                    video_url = None
                    
                    # Method 1: Check for videos.items array (new API structure)
                    if 'videos' in data and 'items' in data['videos'] and isinstance(data['videos']['items'], list) and len(data['videos']['items']) > 0:
                        # Get the best quality video with audio
                        video_items = data['videos']['items']
                        best_video = None
                        
                        # First try to find a video with audio
                        for video in video_items:
                            if video.get('hasAudio', False):
                                best_video = video
                                break
                        
                        # If no video with audio, take the first one
                        if not best_video and video_items:
                            best_video = video_items[0]
                        
                        if best_video:
                            video_url = best_video.get('url')
                            print(f"Found video URL in videos.items array: {video_url}")
                            print(f"Video quality: {best_video.get('quality', 'unknown')}")
                            print(f"Video size: {best_video.get('sizeText', 'unknown')}")
                    
                    # Method 2: Check for direct videos array (fallback)
                    elif 'videos' in data and isinstance(data['videos'], list) and len(data['videos']) > 0:
                        video_url = data['videos'][0].get('url')
                        print(f"Found video URL in videos array: {video_url}")
                    
                    # Method 3: Check for direct URL fields
                    elif 'url' in data:
                        video_url = data['url']
                        print(f"Found video URL in url field: {video_url}")
                    
                    # Method 4: Check for download_url
                    elif 'download_url' in data:
                        video_url = data['download_url']
                        print(f"Found video URL in download_url field: {video_url}")
                    
                    # Method 5: Check for video_url
                    elif 'video_url' in data:
                        video_url = data['video_url']
                        print(f"Found video URL in video_url field: {video_url}")
                    
                    # Method 6: Check for link
                    elif 'link' in data:
                        video_url = data['link']
                        print(f"Found video URL in link field: {video_url}")
                    
                    # Method 7: Check for formats array
                    elif 'formats' in data and isinstance(data['formats'], list) and len(data['formats']) > 0:
                        video_url = data['formats'][0].get('url')
                        print(f"Found video URL in formats array: {video_url}")
                    
                    if video_url:
                        print(f"SUCCESS: Found video URL: {video_url}")
                        return {
                            "download_url": video_url,
                            "title": data.get('title', 'YouTube Video'),
                            "platform": "youtube",
                            "success": True,
                            "debug_info": {
                                "video_id": video_id,
                                "endpoint_used": f"endpoint_{i+1}",
                                "api_host": rapidapi_host,
                                "video_quality": best_video.get('quality', 'unknown') if 'best_video' in locals() else 'unknown',
                                "video_size": best_video.get('sizeText', 'unknown') if 'best_video' in locals() else 'unknown'
                            }
                        }
                    else:
                        print("No video URL found in response")
                else:
                    print(f"API returned error status: {response.status_code}")
                    print(f"Error response: {response.text}")
                    
            except Exception as e:
                print(f"Error with endpoint {i+1}: {str(e)}")
                continue
        
        # If all endpoints fail, try a fallback API
        print("\n--- Trying Fallback API ---")
        return download_youtube_fallback(url)
        
    except Exception as e:
        print(f"YouTube download error: {str(e)}")
        return {"error": f"YouTube download error: {str(e)}", "success": False}

def download_youtube_fallback(url):
    """Fallback YouTube download using a different API"""
    try:
        print("Using fallback YouTube API")
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'youtube-mp36.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        params = {'url': url}
        
        response = requests.get(f'https://{rapidapi_host}/dl', headers=headers, params=params, timeout=30)
        print(f"Fallback API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Fallback API Data: {data}")
            
            if 'link' in data:
                return {
                    "download_url": data['link'],
                    "title": data.get('title', 'YouTube Video'),
                    "platform": "youtube",
                    "success": True,
                    "debug_info": {
                        "api_host": rapidapi_host,
                        "method": "fallback"
                    }
                }
        
        return {"error": "All YouTube APIs failed to extract video", "success": False}
        
    except Exception as e:
        print(f"Fallback YouTube download error: {str(e)}")
        return {"error": f"YouTube download failed: {str(e)}", "success": False}

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
                    "message": "YouTube API test completed",
                    "api_host": "youtube-media-downloader.p.rapidapi.com"
                }
            except Exception as e:
                response = {
                    "status": "Test failed",
                    "test_url": test_url,
                    "error": str(e),
                    "message": "YouTube API test failed",
                    "api_host": "youtube-media-downloader.p.rapidapi.com"
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
            "version": "2.0.0",
            "test_endpoint": "/api/download/test",
            "apis": {
                "youtube": "youtube-media-downloader.p.rapidapi.com",
                "tiktok": "tiktok-video-no-watermark2.p.rapidapi.com",
                "instagram": "instagram-reels-downloader-api.p.rapidapi.com"
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