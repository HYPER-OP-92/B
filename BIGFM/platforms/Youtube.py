import asyncio, httpx, yt_dlp, os
import glob, re, random, json
from typing import Union
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from youtubesearchpython.__future__ import VideosSearch
from BIGFM.utils.formatters import time_to_seconds

# --- CONFIGURATION ---
# Google Cloud Console se API Key yaha dalein
YOUTUBE_API_KEY = "AIzaSyCHRfOCjo77bI3HYRvwIjxIke2TuFT_vh8" 

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
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.api_key = YOUTUBE_API_KEY

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def get_google_metadata(self, video_id):
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
                        duration_raw = item["contentDetails"]["duration"]
                        # ISO 8601 duration parsing (Simple)
                        m = re.search(r'(\d+)M', duration_raw)
                        s = re.search(r'(\d+)S', duration_raw)
                        mm = m.group(1) if m else "0"
                        ss = s.group(1) if s else "00"
                        return {
                            "title": item["snippet"]["title"],
                            "thumb": item["snippet"]["thumbnails"]["high"]["url"],
                            "duration": f"{mm}:{ss.zfill(2)}",
                            "id": video_id
                        }
            except: return None
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        
        v_id = link.split("v=")[-1] if "v=" in link else link.split("/")[-1]
        google_data = await self.get_google_metadata(v_id)
        
        if google_data:
            duration_sec = int(time_to_seconds(google_data["duration"]))
            return google_data["title"], google_data["duration"], duration_sec, google_data["thumb"], v_id

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        playlist = await shell_cmd(f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}")
        try:
            result = playlist.split("\n")
            return [key for key in result if key != ""]
        except: return []

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        cookie = get_cookie_file()
        loop = asyncio.get_running_loop()
        def extract():
            opts = {"format": "best[height<=720]/bestvideo+bestaudio/best", "quiet": True, "cookiefile": cookie}
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(link, download=False).get("url")
        return await loop.run_in_executor(None, extract)

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        res = result[query_type]
        return res["title"], res["duration"], res["thumbnails"][0]["url"].split("?")[0], res["id"]

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
        if videoid: link = self.base + link
        loop = asyncio.get_running_loop()
        cookie = get_cookie_file()

        def dl():
            if songvideo:
                fpath = f"downloads/{title}.mp4"
                opts = {"format": f"{format_id}+140", "outtmpl": f"downloads/{title}", "merge_output_format": "mp4", "cookiefile": cookie}
            elif songaudio:
                fpath = f"downloads/{title}.mp3"
                opts = {"format": format_id, "outtmpl": f"downloads/{title}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}], "cookiefile": cookie}
            elif video:
                opts = {"format": "bestvideo[height<=720]+bestaudio/best", "outtmpl": "downloads/%(id)s.%(ext)s", "cookiefile": cookie}
                info = yt_dlp.YoutubeDL(opts).extract_info(link, download=True)
                return os.path.join("downloads", f"{info['id']}.{info['ext']}")
            else:
                opts = {"format": "bestaudio/best", "outtmpl": "downloads/%(id)s.%(ext)s", "cookiefile": cookie}
                info = yt_dlp.YoutubeDL(opts).extract_info(link, download=True)
                return os.path.join("downloads", f"{info['id']}.{info['ext']}")
            
            yt_dlp.YoutubeDL(opts).download([link])
            return fpath

        return await loop.run_in_executor(None, dl), None
