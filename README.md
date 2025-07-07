# SnapGrabber

All-in-one TikTok, YouTube, Instagram video downloader with ad monetization.

## Features
- Download from TikTok, YouTube, Instagram
- Auto platform detection
- Format options: MP4, MP3, resolutions
- Optional TikTok watermark removal
- Mobile-first UI
- Ad monetization (AdSense/Adsterra)
- Analytics ready

## Tech Stack
- Frontend: HTML, Tailwind CSS, JavaScript
- Backend: Python (FastAPI)
- Downloaders: yt-dlp, instaloader, Puppeteer

## Setup
1. Install backend dependencies: `pip install -r backend/requirements.txt`
2. Run backend: `uvicorn backend.app:app --reload`
3. Open `frontend/index.html` in your browser

## Monetization
- Insert your ad codes in `frontend/index.html` as instructed.

## Legal
- For personal use only. Not affiliated with TikTok, YouTube, or Instagram.
- See `privacy.html` and `dmca.html` for policies. 