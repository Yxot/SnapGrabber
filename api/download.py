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
        rapidapi_host = 'mediafetch-api.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host,
            'Content-Type': 'application/json'
        }
        
        # Use POST request with JSON body
        payload = {
            'url': url,
            'format': 'mp4',
            'quality': 'high'
        }
        
        response = requests.post(f'https://{rapidapi_host}/download', headers=headers, json=payload, timeout=30)
        
        print(f"TikTok API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"TikTok API Data: {data}")
            
            # Extract video URL from response
            video_url = None
            if isinstance(data, dict):
                if 'url' in data:
                    video_url = data['url']
                elif 'download_url' in data:
                    video_url = data['download_url']
                elif 'video_url' in data:
                    video_url = data['video_url']
                elif 'link' in data:
                    video_url = data['link']
                elif 'data' in data and isinstance(data['data'], dict):
                    video_url = data['data'].get('url') or data['data'].get('download_url')
            
            if video_url:
                return {
                    "download_url": video_url,
                    "title": data.get('title', data.get('data', {}).get('title', 'TikTok Video')),
                    "platform": "tiktok",
                    "success": True
                }
            else:
                return {"error": f"TikTok API did not return a valid video URL. Raw response: {json.dumps(data)}", "success": False}
        else:
            return {"error": f"TikTok API error: {response.status_code} {response.text}", "success": False}
        
    except Exception as e:
        print(f"TikTok download error: {str(e)}")
        return {"error": f"TikTok download error: {str(e)}", "success": False}

def download_instagram(url):
    """Download Instagram video using RapidAPI"""
    try:
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'mediafetch-api.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host,
            'Content-Type': 'application/json'
        }
        
        # Use POST request with JSON body
        payload = {
            'url': url,
            'format': 'mp4',
            'quality': 'high'
        }
        
        response = requests.post(f'https://{rapidapi_host}/download', headers=headers, json=payload, timeout=30)
        
        print(f"Instagram API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Instagram API Data: {data}")
            
            # Extract video URL from response
            video_url = None
            if isinstance(data, dict):
                if 'url' in data:
                    video_url = data['url']
                elif 'download_url' in data:
                    video_url = data['download_url']
                elif 'video_url' in data:
                    video_url = data['video_url']
                elif 'link' in data:
                    video_url = data['link']
                elif 'data' in data and isinstance(data['data'], dict):
                    video_url = data['data'].get('url') or data['data'].get('download_url')
            
            if video_url:
                return {
                    "download_url": video_url,
                    "title": data.get('title', data.get('data', {}).get('title', 'Instagram Video')),
                    "platform": "instagram",
                    "success": True
                }
            else:
                return {"error": f"Instagram API did not return a valid video URL. Raw response: {json.dumps(data)}", "success": False}
        else:
            return {"error": f"Instagram API error: {response.status_code} {response.text}", "success": False}
        
    except Exception as e:
        print(f"Instagram download error: {str(e)}")
        return {"error": f"Instagram download error: {str(e)}", "success": False}

def get_youtube_qualities(url):
    """Get all available quality options for a YouTube video"""
    try:
        print(f"=== YOUTUBE QUALITIES DEBUG ===")
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
        
        # Get video details
        params = {
            'videoId': video_id,
            'urlAccess': 'normal',
            'videos': 'auto',
            'audios': 'auto'
        }
        
        response = requests.get(f'https://{rapidapi_host}/v2/video/details', headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract video qualities
            qualities = []
            if 'videos' in data and 'items' in data['videos'] and isinstance(data['videos']['items'], list):
                video_items = data['videos']['items']
                
                for i, video in enumerate(video_items):
                    quality_info = {
                        "index": i,
                        "quality": video.get('quality', 'unknown'),
                        "size": video.get('sizeText', 'unknown'),
                        "width": video.get('width', 0),
                        "height": video.get('height', 0),
                        "has_audio": video.get('hasAudio', False),
                        "extension": video.get('extension', 'mp4'),
                        "mime_type": video.get('mimeType', ''),
                        "url": video.get('url', '')
                    }
                    qualities.append(quality_info)
            
            # Sort qualities by resolution (height)
            qualities.sort(key=lambda x: x['height'], reverse=True)
            
            return {
                "success": True,
                "title": data.get('title', 'YouTube Video'),
                "platform": "youtube",
                "video_id": video_id,
                "qualities": qualities,
                "total_qualities": len(qualities)
            }
        else:
            return {"error": f"API returned error status: {response.status_code}", "success": False}
            
    except Exception as e:
        print(f"YouTube qualities error: {str(e)}")
        return {"error": f"YouTube qualities error: {str(e)}", "success": False}

def download_youtube(url, quality_index=None):
    """Download YouTube video using RapidAPI with quality selection"""
    try:
        print(f"=== YOUTUBE DOWNLOAD DEBUG ===")
        print(f"Input URL: {url}")
        print(f"Quality Index: {quality_index}")
        
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
        
        # Get video details
        params = {
            'videoId': video_id,
            'urlAccess': 'normal',
            'videos': 'auto',
            'audios': 'auto'
        }
        
        response = requests.get(f'https://{rapidapi_host}/v2/video/details', headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract video URL based on quality selection
            video_url = None
            selected_quality = None
            
            if 'videos' in data and 'items' in data['videos'] and isinstance(data['videos']['items'], list):
                video_items = data['videos']['items']
                
                if quality_index is not None and 0 <= quality_index < len(video_items):
                    # Use specified quality
                    selected_quality = video_items[quality_index]
                    video_url = selected_quality.get('url')
                    print(f"Selected quality {quality_index}: {selected_quality.get('quality', 'unknown')}")
                else:
                    # Auto-select best quality with audio
                    best_video = None
                    for video in video_items:
                        if video.get('hasAudio', False):
                            best_video = video
                            break
                    
                    if not best_video and video_items:
                        best_video = video_items[0]
                    
                    if best_video:
                        selected_quality = best_video
                        video_url = best_video.get('url')
                        print(f"Auto-selected quality: {best_video.get('quality', 'unknown')}")
            
            if video_url:
                print(f"SUCCESS: Found video URL: {video_url}")
                return {
                    "download_url": video_url,
                    "title": data.get('title', 'YouTube Video'),
                    "platform": "youtube",
                    "success": True,
                    "quality_info": {
                        "quality": selected_quality.get('quality', 'unknown') if selected_quality else 'unknown',
                        "size": selected_quality.get('sizeText', 'unknown') if selected_quality else 'unknown',
                        "width": selected_quality.get('width', 0) if selected_quality else 0,
                        "height": selected_quality.get('height', 0) if selected_quality else 0,
                        "has_audio": selected_quality.get('hasAudio', False) if selected_quality else False,
                        "extension": selected_quality.get('extension', 'mp4') if selected_quality else 'mp4'
                    },
                    "debug_info": {
                        "video_id": video_id,
                        "api_host": rapidapi_host,
                        "quality_index": quality_index
                    }
                }
            else:
                return {"error": "No video URL found in response", "success": False}
        else:
            return {"error": f"API returned error status: {response.status_code}", "success": False}
            
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

def download_video(url, quality_index=None):
    """Main download function that routes to platform-specific handlers"""
    try:
        print(f"Starting download for URL: {url}")
        print(f"Quality Index: {quality_index}")
        
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
            return download_youtube(url, quality_index)
        else:
            return {"error": "Platform not supported", "success": False}
            
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
                "youtube": "youtube-media-downloader.p.rapidapi.com",
                "tiktok": "mediafetch-api.p.rapidapi.com",
                "instagram": "mediafetch-api.p.rapidapi.com"
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
            quality_index = data.get('quality_index')
            print(f"Extracted URL: {url}")
            print(f"Quality Index: {quality_index}")
            
            # Validate URL
            if not url:
                print("No URL provided")
                self.send_error_response("URL is required")
                return
            
            # Convert quality_index to integer if provided
            if quality_index is not None:
                try:
                    quality_index = int(quality_index)
                except (ValueError, TypeError):
                    quality_index = None
            
            # Download the video
            print("Starting video download")
            result = download_video(url, quality_index)
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