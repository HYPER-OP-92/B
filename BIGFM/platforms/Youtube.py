import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Config se API Keys
try:
    from config import YOUTUBE_API_KEYS
except ImportError:
    YOUTUBE_API_KEYS = []

# Cookies Path
COOKIES_FILE = "BIGFM/cookies.txt"
if not os.path.exists(COOKIES_FILE):
    COOKIES_FILE = None
    print("WARNING: cookies.txt nahi mili! YouTube block kar sakta hai.")

class YouTubeAPI:
    current_key_index = 0
    youtube_client = None

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        if YouTubeAPI.youtube_client is None:
            self._build_youtube_client()

    def _build_youtube_client(self):
        if not YOUTUBE_API_KEYS: return None
        try:
            YouTubeAPI.youtube_client = build(
                "youtube", "v3", 
                developerKey=YOUTUBE_API_KEYS[YouTubeAPI.current_key_index], 
                static_discovery=False
            )
        except Exception: YouTubeAPI.youtube_client = None

    def _rotate_key(self):
        if len(YOUTUBE_API_KEYS) > 1:
            YouTubeAPI.current_key_index = (YouTubeAPI.current_key_index + 1) % len(YOUTUBE_API_KEYS)
            self._build_youtube_client()

    def format_seconds(self, seconds):
        if not seconds: return "00:00"
        seconds = int(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    async def url(self, message: Message) -> Union[str, None]:
        msgs = [message, message.reply_to_message] if message.reply_to_message else [message]
        for m in msgs:
            if m.entities:
                for e in m.entities:
                    if e.type == MessageEntityType.URL:
                        t = m.text or m.caption
                        return t[e.offset : e.offset + e.length]
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        vidid = link if videoid else (re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link).group(1) if re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link) else None)

        # 1. Try Google API (Ismein cookies ki zaroorat nahi hoti)
        if YouTubeAPI.youtube_client:
            for _ in range(len(YOUTUBE_API_KEYS)):
                try:
                    if not vidid:
                        res = await asyncio.to_thread(YouTubeAPI.youtube_client.search().list(q=link, part="id", maxResults=1, type="video").execute)
                        if not res.get("items"): break
                        vidid = res["items"][0]["id"]["videoId"]
                    vres = await asyncio.to_thread(YouTubeAPI.youtube_client.videos().list(part="snippet,contentDetails", id=vidid).execute)
                    if not vres.get("items"): break
                    v = vres["items"][0]
                    dur_iso = v["contentDetails"]["duration"]
                    m = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', dur_iso)
                    ts = int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)
                    return {
                        "title": v["snippet"]["title"],
                        "duration_min": self.format_seconds(ts),
                        "duration_sec": ts,
                        "thumbnail": v["snippet"]["thumbnails"]["high"]["url"],
                        "vidid": vidid
                    }
                except HttpError as e:
                    if e.resp.status in [403, 429]: self._rotate_key(); continue
                    break
                except Exception: break

        # 2. Fallback to yt-dlp with Cookies
        try:
            loop = asyncio.get_running_loop()
            query = f"ytsearch1:{link}" if not vidid else f"https://www.youtube.com/watch?v={vidid}"
            
            ydl_opts = {
                "quiet": True,
                "format": "bestaudio/best",
                "skip_download": True,
                "nocheckcertificate": True,
                "cookiefile": COOKIES_FILE, # Cookies ka use yahan ho raha hai
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
                if 'entries' in info: info = info['entries'][0]
                ts = info.get('duration', 0)
                return {
                    "title": info.get('title', 'Unknown'),
                    "duration_min": self.format_seconds(ts),
                    "duration_sec": ts,
                    "thumbnail": info.get('thumbnail', ''),
                    "vidid": info.get('id', '')
                }
        except Exception as e:
            print(f"Extraction Error: {e}")
            # Crash se bachne ke liye khali dict return karein (Safety Net)
            return {
                "title": "Unknown",
                "duration_min": "00:00",
                "duration_sec": 0,
                "thumbnail": "",
                "vidid": ""
            }

    # Baki functions details() ko dictionary ki tarah use karenge
    async def title(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid); return res["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid); return res["duration_min"]

    async def track(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        track_details = {
            "title": res["title"],
            "link": self.base + res["vidid"],
            "vidid": res["vidid"],
            "duration_min": res["duration_min"],
            "thumb": res["thumbnail"]
        }
        return track_details, res["vidid"]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        l = self.base + link if videoid else link
        cmd = ["yt-dlp", "--cookiefile", COOKIES_FILE, "-g", "-f", "best[height<=?720][ext=mp4]", l] if COOKIES_FILE else ["yt-dlp", "-g", "-f", "best[height<=?720][ext=mp4]", l]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, "Error")

    async def download(self, link, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None):
        l = self.base + link if videoid else link
        loop = asyncio.get_running_loop()
        def dl():
            opts = {
                "format": "bestaudio/best" if not video else "best[height<=?720][ext=mp4]",
                "outtmpl": "downloads/%(id)s.%(ext)s", 
                "quiet": True,
                "cookiefile": COOKIES_FILE,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(l, download=True)
                return os.path.join("downloads", f"{info['id']}.{info['ext']}")
        return await loop.run_in_executor(None, dl), True
