from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4"
    quality: str = "720"
    bitrate: str = "128"

@app.get("/")
def root():
    return {"status": "ok", "service": "Sion Hub Backend"}

@app.post("/api/download")
async def download(req: DownloadRequest):
    try:
        if req.format == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
        else:
            h = req.quality
            ydl_opts = {
                'format': f'best[height<={h}][ext=mp4]/best[height<={h}]/best',
                'quiet': True,
                'no_warnings': True,
            }

        ydl_opts['skip_download'] = True

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=False)

            url_direct = info.get('url')
            if not url_direct and 'formats' in info and info['formats']:
                url_direct = info['formats'][-1].get('url')

            if not url_direct:
                raise HTTPException(500, "URL tidak ditemukan")

            return {
                'success': True,
                'url': url_direct,
                'title': info.get('title', 'video'),
                'thumbnail': info.get('thumbnail', ''),
                'format': req.format,
            }
    except Exception as e:
        raise HTTPException(500, str(e))
