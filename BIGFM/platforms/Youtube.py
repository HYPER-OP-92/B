import asyncio
import re
import requests
from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

# Zyada stable Instances ki list
INSTANCES = [
    "https://inv.tux.rs",
    "https://invidious.sethforprivacy.com",
    "https://invidious.snopyta.org",
    "https://yewtu.be"
]

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    def parse_duration(self, seconds):
        try:
            seconds = int(seconds)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return f"{minutes:02d}:{seconds:02d}"
        except:
            return "00:00"

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: 
            vidid = link
        else:
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            vidid = match.group(1) if match else None
        
        # Multiple instances try karega agar ek fail ho jaye
        for instance in INSTANCES:
            try:
                if not vidid:
                    search_url = f"{instance}/api/v1/search?q={link}&type=video"
                    res = requests.get(search_url, timeout=5).json()
                    if res:
                        vidid = res[0]["videoId"]
                
                if vidid:
                    api_url = f"{instance}/api/v1/videos/{vidid}"
                    item = requests.get(api_url, timeout=5).json()
                    title = item.get("title", "Unknown")
                    duration_seconds = item.get("lengthSeconds", 0)
                    duration_str = self.parse_duration(duration_seconds)
                    thumbnails = item.get("videoThumbnails", [{"url": ""}])
                    thumbnail = thumbnails[0]["url"]
                    return title, duration_str, duration_seconds, thumbnail, vidid
            except:
                continue # Agla instance try karein
        return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        if not res:
            # Error se bachne ke liye khali data return karna (None nahi)
            return {
                "title": "Unknown Track",
                "link": self.base + (videoid if videoid else "dQw4w9WgXcQ"),
                "vidid": videoid if videoid else "dQw4w9WgXcQ",
                "duration_min": "00:00",
                "thumb": None
            }, videoid
        
        title, d_min, d_sec, thumb, vidid = res
        return {
            "title": title, 
            "link": self.base + vidid, 
            "vidid": vidid, 
            "duration_min": d_min, 
            "thumb": thumb
        }, vidid

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: vidid = link
        else:
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            vidid = match.group(1) if match else None

        for instance in INSTANCES:
            try:
                api_url = f"{instance}/api/v1/videos/{vidid}"
                res = requests.get(api_url, timeout=5).json()
                for fmt in res.get("adaptiveFormats", []):
                    if "audio/" in fmt["type"]:
                        return (1, fmt["url"])
            except:
                continue
        return (0, "")

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        try:
            import subprocess
            cmd = f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
            playlist = subprocess.check_output(cmd, shell=True).decode().split("\n")
            return [k for k in playlist if k != ""]
        except:
            return []
