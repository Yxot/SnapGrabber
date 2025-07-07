import instaloader
import asyncio
import os
import re
from urllib.parse import urlparse

async def download(url):
    """
    Instagram video downloader using instaloader
    """
    try:
        # Create downloads directory
        downloads_dir = "downloads"
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        
        # Extract shortcode from URL
        shortcode_match = re.search(r'/p/([^/]+)/', url)
        if not shortcode_match:
            return {"error": "Invalid Instagram URL format"}
        
        shortcode = shortcode_match.group(1)
        
        # Initialize Instaloader
        L = instaloader.Instaloader(
            dirname_pattern=downloads_dir,
            filename_pattern='{shortcode}',
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True
        )
        
        # Download the post
        loop = asyncio.get_event_loop()
        post = await loop.run_in_executor(None, lambda: instaloader.Post.from_shortcode(L.context, shortcode))
        
        if not post.is_video:
            return {"error": "This Instagram post is not a video"}
        
        # Download the video
        await loop.run_in_executor(None, lambda: L.download_post(post, target=shortcode))
        
        # Find the downloaded file
        video_filename = f"{shortcode}.mp4"
        video_path = os.path.join(downloads_dir, video_filename)
        
        if os.path.exists(video_path):
            return {
                "download_url": f"/downloads/{video_filename}",
                "title": f"Instagram Video {shortcode}",
                "platform": "Instagram",
                "shortcode": shortcode
            }
        else:
            return {"error": "Video file not found after download"}
        
    except instaloader.exceptions.LoginRequiredException:
        return {"error": "Instagram requires login for this content"}
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        return {"error": "This is a private Instagram account"}
    except instaloader.exceptions.QueryReturnedNotFoundException:
        return {"error": "Instagram post not found"}
    except Exception as e:
        return {"error": f"Instagram download failed: {str(e)}"}

# Alternative implementation for public posts without login
async def download_public(url):
    """
    Download public Instagram posts without login
    """
    try:
        # This would require a different approach, possibly using requests
        # and parsing the page HTML to extract video URLs
        return {"error": "Public Instagram downloader needs implementation"}
        
    except Exception as e:
        return {"error": f"Instagram download failed: {str(e)}"} 