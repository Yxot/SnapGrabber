# SnapGrabber

All-in-one social media video downloader with ad monetization.

## Features
- Download from 20+ social media platforms
- Auto platform detection
- Format options: MP4, MP3, resolutions
- No watermarks
- Mobile-first UI
- Ad monetization (AdSense/Adsterra)
- Analytics ready

## Supported Platforms
- **TikTok** - Video downloads without watermarks
- **Instagram** - Posts, Reels, Stories
- **Facebook** - Videos and Reels
- **Twitter/X** - Video tweets
- **YouTube** - Videos and Shorts
- **Reddit** - Video posts
- **Pinterest** - Video pins
- **Snapchat** - Public stories
- **Vimeo** - Videos
- **Bilibili** - Videos
- **Dailymotion** - Videos
- **Imgur** - Video posts
- **iFunny** - Videos
- **Izlesene** - Videos
- **Kuaishou** - Videos
- **Douyin** - Videos
- **CapCut** - Templates
- **Threads** - Posts
- **ESPN** - Sports videos
- **IMDB** - Trailers

## Tech Stack
- Frontend: HTML, Tailwind CSS, JavaScript
- Backend: Python (FastAPI)
- Downloader: Universal RapidAPI service

## Setup
1. Install backend dependencies: `pip install -r backend/requirements.txt`
2. Run backend: `uvicorn backend.app:app --reload`
3. Open `frontend/index.html` in your browser

## API Configuration
The app uses RapidAPI services for downloading:
- **TikTok**: `tiktok-video-no-watermark2.p.rapidapi.com`
- **Universal**: `instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com`

## Monetization
- Insert your ad codes in `frontend/index.html` as instructed.

## Legal
- For personal use only. Not affiliated with any social media platforms.
- See `privacy.html` and `dmca.html` for policies. 