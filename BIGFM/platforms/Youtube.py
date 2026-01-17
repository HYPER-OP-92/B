import asyncio
import os
import re
from typing import Union, Optional

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 🔐 PUT YOUR API KEY HERE (optional but recommended)
API_KEY = "AIzaSyBlbkp4_XbjOZAMG6mr_QMmurBW9tcpu0s"

youtube = None
if API_KEY:
    youtube = build("youtube", "v3", developerKey=API_KEY, static_discovery=False)

cookies_file = "BIGFM/cookies.txt"
if not os.path.exists(cookies_file):
    cookies_file = None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(r"(youtube\.com|youtu\.be)")
        self.listbase = "https://youtube.com/playlist?list="

    # ---------- SAFE DURATION ----------
    def parse_duration(self, duration: str):
        if not duration:
            return "00:00", 0

        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return "00:00", 0

        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)

        total = h * 3600 + m * 60 + s
        return (f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"), total

    # ---------- URL EXTRACT ----------
    async def url(self, message: Message) -> Optional[str]:
        for msg in filter(None, [message, message.reply_to_message]):
            text = msg.text or msg.caption
            entities = msg.entities or msg.caption_entities or []
            for e in entities:
                if e.type == MessageEntityType.URL:
                    return text[e.offset:e.offset + e.length]
                if e.type == MessageEntityType.TEXT_LINK:
                    return e.url
        return None

    # ---------- ID EXTRACT ----------
    def _extract_id(self, text: str):
        if not text:
            return None
        m = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", text)
        return m.group(1) if m else None

    # ---------- DETAILS ----------
    async def details(self, query: str):
        if not query or len(query.strip()) < 3:
            return None

        vidid = self._extract_id(query)

        # 🔹 GOOGLE API FIRST
        if youtube and vidid:
            try:
                res = await asyncio.to_thread(
                    youtube.videos().list(
                        part="snippet,contentDetails",
                        id=vidid
                    ).execute
                )
                if res["items"]:
                    item = res["items"][0]
                    title = item["snippet"]["title"]
                    thumb = item["snippet"]["thumbnails"]["high"]["url"]
                    dmin, dsec = self.parse_duration(item["contentDetails"]["duration"])
                    return title, dmin, dsec, thumb, vidid
            except HttpError:
                pass
            except Exception:
                pass

        # 🔹 YT-DLP FALLBACK (ALWAYS WORKS)
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "geo_bypass": True,
            "default_search": "ytsearch",
            "format": "bestaudio/best"
        }

        search = f"{self.base}{vidid}" if vidid else query
        loop = asyncio.get_running_loop()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(
                    None, lambda: ydl.extract_info(search, False)
                )
                if not info:
                    return None

                data = info["entries"][0] if "entries" in info else info

                return (
                    data.get("title", "Unknown"),
                    data.get("duration_string", "00:00"),
                    data.get("duration", 0),
                    data.get("thumbnail"),
                    data.get("id"),
                )
        except Exception:
            return None

    # ---------- TRACK ----------
    async def track(self, query):
        data = await self.details(query)
        if not data:
            return None, None

        title, dmin, dsec, thumb, vidid = data
        return {
            "title": title,
            "link": self.base + vidid,
            "vidid": vidid,
            "duration_min": dmin,
            "thumb": thumb,
        }, vidid

    async def exists(self, link):
        return bool(self.regex.search(link or ""))

    # ---------- STREAM ----------
    async def video(self, link):
        if not link:
            return None

        cmd = [
            "yt-dlp", "-g",
            "-f", "best[height<=720][ext=mp4]/best",
            "--no-playlist",
            "--geo-bypass",
            link
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE
        )
        out, _ = await proc.communicate()
        return out.decode().strip() if out else None

    # ---------- DOWNLOAD ----------
    async def download(self, link, video=False):
        loop = asyncio.get_running_loop()

        def _dl():
            opts = {
                "format": "best[height<=720][ext=mp4]" if video else "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "geo_bypass": True
            }
            if cookies_file:
                opts["cookiefile"] = cookies_file

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, True)
                return f"downloads/{info['id']}.{info['ext']}"

        return await loop.run_in_executor(None, _dl)


