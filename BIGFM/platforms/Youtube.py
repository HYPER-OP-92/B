import asyncio, httpx, yt_dlp, os
import glob, re, random, json
from typing import Union
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from youtubesearchpython.__future__ import VideosSearch
from BIGFM.utils.formatters import time_to_seconds

# --- CONFIGURATION ---
# Google Cloud Console (https://console.cloud.google.com/) se API Key yaha dalein
YOUTUBE_API_KEY = "AIzaSyBlbkp4_XbjOZAMG6mr_QMmurBW9tcpu0s" 

def get_cookie_file():
    try:
        folder_path = f"{os.getcwd()}/cookies"
        txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
        if not txt_files:
            return None
        return random.choice(txt_files)
    except:
        return None

async def shell_cmd(cmd):
    # Cookies support for CLI/Playlists
    cookie = get_cookie_file()
    if cookie:
        cmd += f" --cookies {cookie}"
        
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        err = errorz.decode("utf-8").lower()
        if "unavailable videos are hidden" in err:
            return out.decode("utf-8")
        return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.api_key = YOUTUBE_API_KEY

    async def get_google_metadata(self, video_id):
        """Google API se fast metadata nikalne ke liye"""
        if not self.api_key or "YOUR_GOOGLE" in self.api_key:
            return None
        
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={self.api_key}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("items"):
                        item = data["items"][0]
                        # ISO 8601 duration parsing (PT5M30S -> 5:30)
                        duration_raw = item["contentDetails"]["duration"]
                        # Simple regex to get numbers from ISO duration
                        import re
                        hours = re.search(r'(\d+)H', duration_raw)
                        mins = re.search(r'(\d+)M', duration_raw)
                        secs = re.search(r'(\d+)S', duration_raw)
                        h = hours.group(1) if hours else "0"
                        m = mins.group(1) if mins else "0"
                        s = secs.group(1) if secs else "0"
                        
                        duration_formatted = f"{m}:{s.zfill(2)}" if h == "0" else f"{h}:{m.zfill(2)}:{s.zfill(2)}"
                        
                        return {
                            "title": item["snippet"]["title"],
                            "thumb": item["snippet"]["thumbnails"]["high"]["url"],
                            "duration": duration_formatted,
                            "id": video_id
                        }
            except:
                return None
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        # Extract Video ID
        v_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link.split("/")[-1].split("?")[0]
        
        # 1. Try Google API First (Super Fast)
        google_data = await self.get_google_metadata(v_id)
        if google_data:
            duration_sec = int(time_to_seconds(google_data["duration"]))
            return google_data["title"], google_data["duration"], duration_sec, google_data["thumb"], v_id

        # 2. Fallback to scraping if Google API fails
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def video(self, link: str, videoid: Union[bool, str] = None):
        """VC Mein direct play karne ke liye direct stream link nikalta hai"""
        if videoid: link = self.base + link
        cookie = get_cookie_file()
        
        loop = asyncio.get_running_loop()
        def extract():
            opts = {
                "format": "best[height<=720]/bestvideo+bestaudio/best",
                "quiet": True,
                "cookiefile": cookie,
                "geo_bypass": True
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                return info.get("url") # Direct stream link for VC

        return await loop.run_in_executor(None, extract)

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()
        cookie = get_cookie_file()

        def audio_dl():
            opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "cookiefile": cookie,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return os.path.join("downloads", f"{info['id']}.{info['ext']}")

        def video_dl():
            opts = {
                "format": "(bestvideo[height<=720]+bestaudio/best)",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "cookiefile": cookie,
                "geo_bypass": True,
                "merge_output_format": "mp4",
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return os.path.join("downloads", f"{info['id']}.{info['ext']}")

        if songvideo or video:
            return await loop.run_in_executor(None, video_dl), None
        else:
            return await loop.run_in_executor(None, audio_dl), None
