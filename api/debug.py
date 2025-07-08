from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Debug endpoint to test YouTube API directly"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Test the YouTube API directly
        test_url = "https://youtu.be/ooMsDvZUrAg?si=qf2SHRR9RXdCjIUV"
        video_id = "ooMsDvZUrAg"
        
        rapidapi_key = '164e51757bmsh7607ec502ddd08ap19830fjsnaee61ed9f238'
        rapidapi_host = 'youtube-media-downloader.p.rapidapi.com'
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        # Test multiple endpoints
        results = {}
        
        # Test 1: Video details endpoint
        try:
            params1 = {
                'videoId': video_id,
                'urlAccess': 'normal',
                'videos': 'auto',
                'audios': 'auto'
            }
            response1 = requests.get(f'https://{rapidapi_host}/v2/video/details', headers=headers, params=params1, timeout=30)
            results['endpoint_1'] = {
                'status': response1.status_code,
                'data': response1.json() if response1.status_code == 200 else response1.text
            }
        except Exception as e:
            results['endpoint_1'] = {'error': str(e)}
        
        # Test 2: Simple video details
        try:
            params2 = {'videoId': video_id}
            response2 = requests.get(f'https://{rapidapi_host}/v2/video/details', headers=headers, params=params2, timeout=30)
            results['endpoint_2'] = {
                'status': response2.status_code,
                'data': response2.json() if response2.status_code == 200 else response2.text
            }
        except Exception as e:
            results['endpoint_2'] = {'error': str(e)}
        
        # Test 3: Direct download endpoint
        try:
            params3 = {'url': test_url}
            response3 = requests.get(f'https://{rapidapi_host}/dl', headers=headers, params=params3, timeout=30)
            results['endpoint_3'] = {
                'status': response3.status_code,
                'data': response3.json() if response3.status_code == 200 else response3.text
            }
        except Exception as e:
            results['endpoint_3'] = {'error': str(e)}
        
        # Test 4: Fallback API
        try:
            fallback_host = 'youtube-mp36.p.rapidapi.com'
            fallback_headers = {
                'x-rapidapi-key': rapidapi_key,
                'x-rapidapi-host': fallback_host
            }
            fallback_params = {'url': test_url}
            response4 = requests.get(f'https://{fallback_host}/dl', headers=fallback_headers, params=fallback_params, timeout=30)
            results['fallback_api'] = {
                'status': response4.status_code,
                'data': response4.json() if response4.status_code == 200 else response4.text
            }
        except Exception as e:
            results['fallback_api'] = {'error': str(e)}
        
        response = {
            "test_url": test_url,
            "video_id": video_id,
            "api_host": rapidapi_host,
            "results": results
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 