import asyncio
import os
import re
import random
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError
import config 

# --- API ROTATION LOGIC ---
API_KEYS = [k.strip() for k in config.API_KEY.split(",")]
API_INDEX = 0 

def get_youtube_client():
    global API_INDEX
    return build("youtube", "v3", developerKey=API_KEYS[API_INDEX], static_discovery=False)

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
        return ""
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    def parse_duration(self, duration):
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
        return duration_str, total_seconds

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

    async def details(self, link: str, videoid: Union[bool, str] = None):
        global API_INDEX
        if videoid: vidid = link
        else:
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            vidid = match.group(1) if match else None
        
        for _ in range(len(API_KEYS)):
            youtube = get_youtube_client() 
            try:
                if not vidid:
                    res = await asyncio.to_thread(youtube.search().list(q=link, part="id", maxResults=1, type="video").execute)
                    if not res.get("items"): return None
                    vidid = res["items"][0]["id"]["videoId"]
                
                res = await asyncio.to_thread(youtube.videos().list(part="snippet,contentDetails", id=vidid).execute)
                if not res.get("items"): return None
                item = res["items"][0]
                title, (d_min, d_sec) = item["snippet"]["title"], self.parse_duration(item["contentDetails"]["duration"])
                return title, d_min, d_sec, item["snippet"]["thumbnails"]["high"]["url"], vidid
            except HttpError as e:
                if e.resp.status in [403, 429]:
                    API_INDEX = (API_INDEX + 1) % len(API_KEYS)
                    continue 
                return None
        return None

    async def title(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[0] if res else "Unknown"

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[1] if res else "00:00"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[3] if res else None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        if not res: return None, None
        title, d_min, d_sec, thumb, vidid = res
        return {"title": title, "link": self.base + vidid, "vidid": vidid, "duration_min": d_min, "thumb": thumb}, vidid

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        # Bypass for streaming
        opts = ["yt-dlp", "-g", "-f", "best[height<=?480][ext=mp4]/best", "--no-playlist", "--geo-bypass", 
                "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "--extractor-args", "youtube:player_client=ios,android", f"{link}"]
        proc = await asyncio.create_subprocess_exec(*opts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, "")

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        playlist = await shell_cmd(f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}")
        return [k for k in playlist.split("\n") if k != ""]

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        global API_INDEX
        for _ in range(len(API_KEYS)):
            youtube = get_youtube_client()
            try:
                res = await asyncio.to_thread(youtube.search().list(q=link, part="snippet", maxResults=10, type="video").execute)
                if not res.get("items"): return None
                result = res["items"][query_type]
                vidid, title, thumb = result["id"]["videoId"], result["snippet"]["title"], result["snippet"]["thumbnails"]["high"]["url"]
                video_res = await asyncio.to_thread(youtube.videos().list(part="contentDetails", id=vidid).execute)
                d_min, _ = self.parse_duration(video_res["items"][0]["contentDetails"]["duration"])
                return title, d_min, thumb, vidid
            except HttpError as e:
                if e.resp.status in [403, 429]:
                    API_INDEX = (API_INDEX + 1) % len(API_KEYS)
                    continue
                return None
        return None

    async def download(self, link: str, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None) -> str:
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()
        ytdl_opts = {
            "quiet": True, "no_warnings": True, "geo_bypass": True, "nocheckcertificate": True,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "extractor_args": {"youtube": {"player_client": ["ios", "android"], "player_skip": ["webpage", "configs"]}},
        }
        if songvideo:
            ytdl_opts.update({"format": f"{format_id}+140", "outtmpl": f"downloads/{title}", "merge_output_format": "mp4"})
        elif songaudio:
            ytdl_opts.update({"format": "bestaudio/best", "outtmpl": f"downloads/{title}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]})

        try:
            def dl():
                with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                    info = ydl.extract_info(link, download=True)
                    return ydl.prepare_filename(info)
            downloaded_file = await loop.run_in_executor(None, dl)
            return downloaded_file, True
        except Exception:
            return None, False

cookies = None
