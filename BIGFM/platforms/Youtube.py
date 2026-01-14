import asyncio
import os
import re
import sqlite3
import time
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build 

# --- CONFIGURATION ---
# Replace with your actual YouTube API Key
API_KEY = "AIzaSyAfG6kmGSSS0p2NM5nrMoGlhxit1whQvPk" 
DB_NAME = "youtube_cache.db"

# Global instance of YouTube API
youtube = build("youtube", "v3", developerKey=API_KEY, static_discovery=False)

# --- DATABASE SETUP (PERMANENT STORAGE) ---
def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table to store search queries (Saves 100 Quota Units per repeat search)
    cursor.execute('''CREATE TABLE IF NOT EXISTS search_history 
                      (query TEXT PRIMARY KEY, video_id TEXT)''')
    # Table to store video metadata (Saves 1 Quota Unit per repeat request)
    cursor.execute('''CREATE TABLE IF NOT EXISTS video_details 
                      (video_id TEXT PRIMARY KEY, title TEXT, duration_str TEXT, 
                       duration_sec INTEGER, thumbnail TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database on startup
init_db()

# --- DATABASE HELPER FUNCTIONS ---

def get_cached_search(query: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT video_id FROM search_history WHERE query=?", (query.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def save_search_to_cache(query: str, video_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO search_history VALUES (?, ?)", (query.lower().strip(), video_id))
        conn.commit()
    except Exception: pass
    finally: conn.close()

def get_cached_video_details(video_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, duration_str, duration_sec, thumbnail FROM video_details WHERE video_id=?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else None

def save_video_to_cache(video_id, title, dur_str, dur_sec, thumb):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO video_details VALUES (?, ?, ?, ?, ?)", 
                       (video_id, title, dur_str, dur_sec, thumb))
        conn.commit()
    except Exception: pass
    finally: conn.close()

# --- UTILITY FUNCTIONS ---

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

# Handling cookies for yt-dlp
cookies_file = "BIGFM/cookies.txt"
if not os.path.exists(cookies_file):
    cookies_file = None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    def parse_duration(self, duration):
        """Converts YouTube ISO 8601 duration (e.g., PT5M30S) to readable string and seconds."""
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
        return duration_str, total_seconds

    async def details(self, link: str, videoid: Union[bool, str] = None):
        """Fetches video details. Uses Permanent Cache to save API Quota."""
        if videoid:
            vidid = link
        else:
            # Extract Video ID from URL
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            vidid = match.group(1) if match else None
        
        # STEP 1: If it's a search query (not a link), check Search Cache
        if not vidid:
            cached_vidid = get_cached_search(link)
            if cached_vidid:
                vidid = cached_vidid
            else:
                # Perform API Search (Costs 100 Units)
                search_res = await asyncio.to_thread(
                    youtube.search().list(q=link, part="id", maxResults=1, type="video").execute
                )
                if not search_res.get("items"): return None
                vidid = search_res["items"][0]["id"]["videoId"]
                save_search_to_cache(link, vidid)

        # STEP 2: Check Video Details Cache
        cached_data = get_cached_video_details(vidid)
        if cached_data:
            # Return cached data: (title, duration_str, duration_sec, thumbnail, video_id)
            return (*cached_data, vidid)

        # STEP 3: If not in Cache, fetch from API (Costs 1 Unit)
        video_res = await asyncio.to_thread(
            youtube.videos().list(part="snippet,contentDetails", id=vidid).execute
        )
        if not video_res.get("items"): return None
        
        item = video_res["items"][0]
        title = item["snippet"]["title"]
        dur_str, dur_sec = self.parse_duration(item["contentDetails"]["duration"])
        thumb = item["snippet"]["thumbnails"]["high"]["url"]
        
        # Save to Permanent Cache
        save_video_to_cache(vidid, title, dur_str, dur_sec, thumb)
        
        return (title, dur_str, dur_sec, thumb, vidid)

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def title(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[0] if res else "Unknown"

    async def track(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        if not res: return None, None
        title, d_min, d_sec, thumb, vidid = res
        return {
            "title": title, 
            "link": self.base + vidid, 
            "vidid": vidid, 
            "duration_min": d_min, 
            "thumb": thumb
        }, vidid

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        cookie_cmd = f"--cookies {cookies_file}" if cookies_file else ""
        # Flat playlist extraction via yt-dlp (Saves huge Quota)
        cmd = f"yt-dlp {cookie_cmd} -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        playlist_ids = await shell_cmd(cmd)
        return [k for k in playlist_ids.split("\n") if k != ""]

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None) -> str:
        """Handles video/audio downloads using yt-dlp."""
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()
        common_opts = {"geo_bypass": True, "nocheckcertificate": True, "quiet": True, "no_warnings": True}
        if cookies_file: common_opts["cookiefile"] = cookies_file

        def audio_dl():
            ydl_opts = {**common_opts, "format": "bestaudio/best", "outtmpl": "downloads/%(id)s.%(ext)s"}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, False)
                path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if not os.path.exists(path): ydl.download([link])
                return path

        if songvideo or video:
            return None, "❌ Video downloading is disabled."

        if songaudio:
            fpath = f"downloads/{title}.mp3"
            def sa_dl():
                with yt_dlp.YoutubeDL({**common_opts, "format": format_id, "outtmpl": f"downloads/{title}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]}) as ydl:
                    ydl.download([link])
            await loop.run_in_executor(None, sa_dl)
            return fpath

        downloaded_file = await loop.run_in_executor(None, audio_dl)
        return downloaded_file, True
