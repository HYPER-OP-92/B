import asyncio
import os
import re
import glob
import random
import yt_dlp
import isodate
from typing import Union
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from googleapiclient.discovery import build

# ================= CONFIGURATION =================
YOUTUBE_API_KEY = "AIzaSyBlbkp4_XbjOZAMG6mr_QMmurBW9tcpu0s" # यहाँ अपनी API Key डालें
# =================================================

youtube_client = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_random_cookie():
    folder_path = os.path.join(os.getcwd(), "cookies")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    return random.choice(txt_files) if txt_files else None

def parse_duration(duration_iso):
    try:
        seconds = int(isodate.parse_duration(duration_iso).total_seconds())
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{sec:02d}", seconds
        return f"{minutes:02d}:{sec:02d}", seconds
    except:
        return "00:00", 0

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        for msg in messages:
            text = msg.text or msg.caption
            if not text: continue
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return text[entity.offset : entity.offset + entity.length]
            if msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def get_video_id(self, link: str):
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, link)
        return match.group(1) if match else None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        loop = asyncio.get_event_loop()
        v_id = link if videoid else await self.get_video_id(link)
        if not v_id:
            search = await loop.run_in_executor(None, lambda: youtube_client.search().list(q=link, part="id", maxResults=1, type="video").execute())
            if not search.get("items"): return None, None, None, None, None
            v_id = search["items"][0]["id"]["videoId"]
        
        video = await loop.run_in_executor(None, lambda: youtube_client.videos().list(id=v_id, part="snippet,contentDetails").execute())
        if not video.get("items"): return None, None, None, None, None
        
        item = video["items"][0]
        title = item["snippet"]["title"]
        dur_min, dur_sec = parse_duration(item["contentDetails"]["duration"])
        thumb = item["snippet"]["thumbnails"]["high"]["url"]
        return title, dur_min, dur_sec, thumb, v_id

    async def title(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[0]

    async def track(self, link: str, videoid: Union[bool, str] = None):
        title, dur_min, dur_sec, thumb, v_id = await self.details(link, videoid)
        return {"title": title, "link": self.base + v_id, "vidid": v_id, "duration_min": dur_min, "thumb": thumb}, v_id

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None) -> str:
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()

        def download_logic():
            if not os.path.exists("downloads"): os.makedirs("downloads")
            cookie_file = get_random_cookie()
            
            # ID को फाइल नेम बनाना सबसे सुरक्षित है
            v_id = link.split("=")[-1][-11:] 
            output_template = f"downloads/{v_id}.%(ext)s"

            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "cookiefile": cookie_file,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }

            if songvideo:
                ydl_opts.update({"format": f"{format_id}+140/bestvideo+bestaudio", "outtmpl": f"downloads/{v_id}.mp4", "merge_output_format": "mp4"})
                final_path = f"downloads/{v_id}.mp4"
            elif songaudio:
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "outtmpl": f"downloads/{v_id}",
                    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
                })
                final_path = f"downloads/{v_id}.mp3"
            else:
                ydl_opts.update({"format": "bestaudio/best", "outtmpl": output_template})
                final_path = f"downloads/{v_id}.mp3"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            
            # चेक करें कि फाइल बनी या नहीं
            if os.path.exists(final_path):
                return final_path
            return None

        try:
            file_path = await loop.run_in_executor(None, download_logic)
            if not file_path:
                return None, "Download Failed"
            return file_path, None
        except Exception as e:
            return None, str(e)
