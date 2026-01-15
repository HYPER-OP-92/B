import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# .env file load karne ke liye
load_dotenv()

# --- BASIC CONFIG ---
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", None)
BOT_TOKEN = getenv("BOT_TOKEN", None)
MONGO_DB_URI = getenv("MONGO_DB_URI", None)

# --- YOUTUBE API KEYS ---
# Multi-key support: key1, key2 format mein dalien
API_KEY = getenv("API_KEY", "AIzaSyDYXTbXOP6X9vYm4BSrCiLoMl24lvt7XGs, AIzaSyAwBmV6pjZcd8gM8paeA5mi00eejGUXeBc")

# --- LOGGER & OWNER ---
# Dhyan dein: LOGGER_ID hamesha integer (-100...) hona chahiye
LOGGER_ID = int(getenv("LOGGER_ID", "-1001511253627"))
# Kuch bots LOG_GROUP_ID mangte hain, isliye dono define kar diye
LOG_GROUP_ID = LOGGER_ID 
OWNER_ID = int(getenv("OWNER_ID", "7967418569"))

# --- SUPPORT LINKS ---
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/about_deadly_venom")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/NOBITA_SUPPORT")
# Fix for ImportError: cannot import name 'SUPPORT_GROUP'
SUPPORT_GROUP = SUPPORT_CHAT 

# --- LIMITS & DURATIONS ---
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 204857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 2073741824))

# --- ASSISTANT SETTINGS ---
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))
ASSISTANT_LEAVE_TIME = int(getenv("ASSISTANT_LEAVE_TIME", 5400))

# --- SPOTIFY ---
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

# --- SESSIONS ---
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

# --- IMAGES ---
START_IMG_URL = getenv("START_IMG_URL", "https://graph.org/file/5e7e5d40bc2f6bb9868dd-e272c7f0ec8ff537bf.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://graph.org/file/5e7e5d40bc2f6bb9868dd-e272c7f0ec8ff537bf.jpg")
PLAYLIST_IMG_URL = "https://graph.org/file/5e7e5d40bc2f6bb9868dd-e272c7f0ec8ff537bf.jpg"
STATS_IMG_URL = "https://telegra.ph/file/edd388a42dd2c499fd868.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/492a3bb2e880d19750b79.jpg"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/492a3bb2e880d19750b79.jpg"
STREAM_IMG_URL = "https://graph.org/file/ff2af8d4d10afa1baf49e.jpg"
SOUNCLOUD_IMG_URL = "https://graph.org/file/c95a687e777b55be1c792.jpg"
YOUTUBE_IMG_URL = "https://graph.org/file/e8730fdece86a1166f608.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://graph.org/file/0bb6f36796d496b4254ff.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://graph.org/file/0bb6f36796d496b4254ff.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://graph.org/file/0bb6f36796d496b4254ff.jpg"

# --- MISC (BANNED USERS & CACHE) ---
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
file_cache: dict[str, float] = {}
PRIVATE_BOT_MODE_MEM = int(getenv("PRIVATE_BOT_MODE_MEM", 1))
CACHE_DURATION = int(getenv("CACHE_DURATION", "86400"))
CACHE_SLEEP = int(getenv("CACHE_SLEEP", "3600"))

# --- UTILS ---
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# --- VALIDATION ---
if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is wrong.")

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is wrong.")
