import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls

# --- py-tgcalls v2.2.0 Clean Imports ---
from pytgcalls.types import (
    AudioPiped,
    AudioVideoPiped,
    HighQualityAudio,
    MediumQualityVideo,
    Update,
)
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.exceptions import (
    AlreadyJoined,
    NoActiveGroupCall,
    TelegramServerError,
)

# Compatibility for other files
AlreadyJoinedError = AlreadyJoined 
# --------------------------------------

import config
from BIGFM import LOGGER, YouTube, app
from BIGFM.misc import db
from BIGFM.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from BIGFM.utils.exceptions import AssistantErr
from BIGFM.utils.formatters import check_duration, seconds_to_min, speed_converter
from BIGFM.utils.inline.play import stream_markup
from BIGFM.utils.stream.autoclear import auto_clean
from BIGFM.utils.thumbnails import gen_thumb
from strings import get_string

autoend = {}
counter = {}

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    def __init__(self):
        # STRING Problem Fix: Only create clients if string is provided and not empty
        self.userbot1 = None
        self.one = None
        if config.STRING1 and str(config.STRING1).strip() not in ["None", ""]:
            self.userbot1 = Client(name="AviaxAss1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.STRING1.strip())
            self.one = PyTgCalls(self.userbot1)

        self.userbot2 = None
        self.two = None
        if config.STRING2 and str(config.STRING2).strip() not in ["None", ""]:
            self.userbot2 = Client(name="AviaxAss2", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.STRING2.strip())
            self.two = PyTgCalls(self.userbot2)

        self.userbot3 = None
        self.three = None
        if config.STRING3 and str(config.STRING3).strip() not in ["None", ""]:
            self.userbot3 = Client(name="AviaxAss3", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.STRING3.strip())
            self.three = PyTgCalls(self.userbot3)

        self.userbot4 = None
        self.four = None
        if config.STRING4 and str(config.STRING4).strip() not in ["None", ""]:
            self.userbot4 = Client(name="AviaxAss4", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.STRING4.strip())
            self.four = PyTgCalls(self.userbot4)

        self.userbot5 = None
        self.five = None
        if config.STRING5 and str(config.STRING5).strip() not in ["None", ""]:
            self.userbot5 = Client(name="AviaxAss5", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.STRING5.strip())
            self.five = PyTgCalls(self.userbot5)

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def join_call(self, chat_id: int, original_chat_id: int, link, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        stream = AudioVideoPiped(link, HighQualityAudio(), MediumQualityVideo()) if video else AudioPiped(link, HighQualityAudio())
        try:
            await assistant.join_group_call(chat_id, stream)
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except AlreadyJoined:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        if not check: return
        try:
            popped = check.pop(0)
            await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
            queued = check[0]["file"]
            video = True if str(check[0]["streamtype"]) == "video" else False
            stream = AudioVideoPiped(queued, HighQualityAudio(), MediumQualityVideo()) if video else AudioPiped(queued, HighQualityAudio())
            await client.change_stream(chat_id, stream)
        except: pass

    async def start(self):
        LOGGER(__name__).info("Starting Assistant Clients...\n")
        if self.one: await self.one.start()
        if self.two: await self.two.start()
        if self.three: await self.three.start()
        if self.four: await self.four.start()
        if self.five: await self.five.start()

    async def decorators(self):
        # Set decorators for all active clients
        for ass in [self.one, self.two, self.three, self.four, self.five]:
            if not ass: continue
            @ass.on_stream_end()
            async def handler(client, update: Update):
                if isinstance(update, StreamAudioEnded):
                    await self.change_stream(client, update.chat_id)

Aviax = Call()
