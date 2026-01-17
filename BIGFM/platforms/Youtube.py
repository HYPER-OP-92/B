import asyncio
import os
import re
from typing import Optional

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 🔑 ADD YOUR GOOGLE CLOUD API KEY(S) HERE
YOUTUBE_API_KEYS = [
    "AIzaSyBlbkp4_XbjOZAMG6mr_QMmurBW9tcpu0s"
]


class YouTubeAPI:
    current_key = 0

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(r"(youtube\.com|youtu\.be)")
        self.youtube = None

        if YOUTUBE_API_KEYS:
            self._build_client()

    # ---------------- BUILD CLIENT ----------------
    def _build_client(self):
        try:
            self.youtube = build(
                "youtube",
                "v3",
                developerKey=YOUTUBE_API_KEYS[self.current_key],
                static_discovery=False
            )
        except Exception:
            self.youtube = None

    def _rotate_key(self):
        if len(YOUTUBE_API_KEYS) > 1:
            self.current_key = (self.current_key + 1) % len(YOUTUBE_API_KEYS)
            self._build_client()

    # ---------------- URL EXTRACT ----------------
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

    # ---------------- ID EXTRACT ----------------
    def _extract_id(self, text: str) -> Optional[str]:
        if not text:
            return None
        m = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", text)
        return m.group(1) if m else None

    # ---------------- GOOGLE API DETAILS ----------------
    async def _api_details(self, vidid: str):
        if not self.youtube:
            return None

        try:
            res = await asyncio.to_thread(
                self.youtube.videos().list(
                    part="snippet,contentDetails",
                    id=vidid
                ).execute
            )

            if not res["items"]:
                return None

            item = res["items"][0]
            title = item["snippet"]["title"]
            thumb = item["snippet"]["thumbnails"]["high"]["url"]
            duration = item["contentDetails"]["duration"]

            dur_min = duration.replace("PT", "").replace("M", ":").replace("S", "")
            return title, dur_min, 0, thumb, vidid

        except HttpError as e:
            if e.resp.status in (403, 429):
                self._rotate_key()
            return None
        except Exception:
            return None

    # ---------------- DETAILS (API + FALLBACK) ----------------
    async def details(self, query: str):
        if not query or len(query.strip()) < 3:
            return None

        vidid = self._extract_id(query)

        # 🔹 TRY GOOGLE API FIRST
        if vidid:
            api_data = await self._api_details(vidid)
            if api_data:
                return api_data

        # 🔹 YT-DLP FALLBACK
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "geo_bypass": True,
            "format": "bestaudio/best",
            "default_search": "ytsearch",
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

                if "entries" in info:
                    if not info["entries"]:
                        return None
                    data = info["entries"][0]
                else:
                    data = info

                return (
                    data.get("title", "Unknown"),
                    data.get("duration_string", "00:00"),
                    data.get("duration", 0),
                    data.get("thumbnail"),
                    data.get("id"),
                )
        except Exception:
            return None

    # ---------------- HELPERS ----------------
    async def title(self, query):
        data = await self.details(query)
        return data[0] if data else "Unknown"

    async def duration(self, query):
        data = await self.details(query)
        return data[1] if data else "00:00"

    async def thumbnail(self, query):
        data = await self.details(query)
        return data[3] if data else None

    async def track(self, query):
        data = await self.details(query)
        if not data:
            return None, None

        title, dur_min, dur_sec, thumb, vidid = data
        return {
            "title": title,
            "link": self.base + vidid,
            "vidid": vidid,
            "duration_min": dur_min,
            "thumb": thumb,
        }, vidid

    async def exists(self, link):
        return bool(self.regex.search(link or ""))

    # ---------------- STREAM VIDEO ----------------
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

    # ---------------- DOWNLOAD ----------------
    async def download(self, link, video=False):
        if not link:
            return None

        loop = asyncio.get_running_loop()

        def _dl():
            opts = {
                "format": "best[height<=720][ext=mp4]" if video else "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, True)
                return f"downloads/{info['id']}.{info['ext']}"

        return await loop.run_in_executor(None, _dl)
        
