import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Config se API Keys ki list mangwa rahe hain
from config import YOUTUBE_API_KEYS 

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

# Cookies handling for yt-dlp
cookies_file = "BIGFM/cookies.txt"
if not os.path.exists(cookies_file):
    cookies_file = None

class YouTubeAPI:
    # --- Class Variables (Taaki state yaad rahe) ---
    # Ye variables poore bot ke liye ek hi rahenge
    current_key_index = 0
    youtube_client = None

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        
        # Agar client pehli baar ban raha hai toh initialize karein
        if YouTubeAPI.youtube_client is None:
            self._build_youtube_client()

    def _build_youtube_client(self):
        """Current active key se client build karta hai"""
        if not YOUTUBE_API_KEYS:
            raise Exception("Config mein koi YOUTUBE_API_KEY nahi mili!")
        
        # Globally client ko update karna
        YouTubeAPI.youtube_client = build(
            "youtube", 
            "v3", 
            developerKey=YOUTUBE_API_KEYS[YouTubeAPI.current_key_index], 
            static_discovery=False
        )

    def _rotate_key(self):
        """Jab quota khatm ho jaye toh permanent agli key par switch karein"""
        YouTubeAPI.current_key_index = (YouTubeAPI.current_key_index + 1) % len(YOUTUBE_API_KEYS)
        self._build_youtube_client()
        print(f"CRITICAL: Quota Exhausted! Switched to Key Index {YouTubeAPI.current_key_index} for all future requests.")

    def parse_duration(self, duration):
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
        return duration_str, total_seconds

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            vidid = link
        else:
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            vidid = match.group(1) if match else None

        # Retry loop: Agar key ka quota khatm hota hai toh shift karke dobara try karein
        for _ in range(len(YOUTUBE_API_KEYS)):
            try:
                if not vidid:
                    # Search logic
                    search_response = await asyncio.to_thread(
                        YouTubeAPI.youtube_client.search().list(q=link, part="id", maxResults=1, type="video").execute
                    )
                    if not search_response.get("items"): return None
                    vidid = search_response["items"][0]["id"]["videoId"]

                # Video details logic
                video_response = await asyncio.to_thread(
                    YouTubeAPI.youtube_client.videos().list(part="snippet,contentDetails", id=vidid).execute
                )
                
                if not video_response.get("items"): return None

                video_data = video_response["items"][0]
                title = video_data["snippet"]["title"]
                thumbnail = video_data["snippet"]["thumbnails"]["high"]["url"]
                duration_iso = video_data["contentDetails"]["duration"]
                duration_min, duration_sec = self.parse_duration(duration_iso)
                
                return title, duration_min, duration_sec, thumbnail, vidid

            except HttpError as e:
                if e.resp.status in [403, 429]: # Quota khatm hone ka error code
                    self._rotate_key()
                    # Agli key ke saath loop phir se chalega
                    continue
                else:
                    raise e
        return None

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        for _ in range(len(YOUTUBE_API_KEYS)):
            try:
                search_response = await asyncio.to_thread(
                    YouTubeAPI.youtube_client.search().list(q=link, part="snippet", maxResults=10, type="video").execute
                )
                if not search_response.get("items"): return None

                result = search_response["items"][query_type]
                vidid = result["id"]["videoId"]
                title = result["snippet"]["title"]
                thumbnail = result["snippet"]["thumbnails"]["high"]["url"]
                
                video_res = await asyncio.to_thread(
                    YouTubeAPI.youtube_client.videos().list(part="contentDetails", id=vidid).execute
                )
                duration_iso = video_res["items"][0]["contentDetails"]["duration"]
                duration_min, _ = self.parse_duration(duration_iso)

                return title, duration_min, thumbnail, vidid
            except HttpError as e:
                if e.resp.status in [403, 429]:
                    self._rotate_key()
                    continue
                else:
                    raise e
        return None

    # --- Baki Title, Duration, Track functions details() ko call karte hain ---
    # Isliye wo automatically updated key use karenge.

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]
        return None

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        opts = ["yt-dlp", "-g", "-f", "best[height<=?720][ext=mp4]/best", "--geo-bypass", "--no-playlist", f"{link}"]
        if cookies_file:
            opts.insert(1, "--cookies"), opts.insert(2, cookies_file)
        proc = await asyncio.create_subprocess_exec(*opts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, "Error")

    async def download(self, link, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None):
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()
        common_opts = {"geo_bypass": True, "quiet": True, "no_warnings": True}
        if cookies_file: common_opts["cookiefile"] = cookies_file

        def dl():
            opts = {**common_opts, "format": "bestaudio/best" if not video else "best[height<=?720][ext=mp4]", "outtmpl": "downloads/%(id)s.%(ext)s"}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return os.path.join("downloads", f"{info['id']}.{info['ext']}")
        
        return await loop.run_in_executor(None, dl), True
