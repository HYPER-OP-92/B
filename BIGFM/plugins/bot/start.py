import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from youtubesearchpython.__future__ import VideosSearch

import config
from BIGFM import app
from BIGFM.misc import _boot_
from BIGFM.plugins.sudo.sudoers import sudoers_list
from BIGFM.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from BIGFM.utils import bot_sys_stats
from BIGFM.utils.decorators.language import LanguageStart
from BIGFM.utils.formatters import get_readable_time
from BIGFM.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# --- [ FIX: ABOUT TEXT FUNCTION ] ---
def get_about_text():
    DEV_USERNAME = "KIRU_OP" # Apna Telegram Username yahan likhein
    return f"""
🎧 ** sʜʏᴧᴍ ᴠɪʙє [ 🇮🇳 | 🌸 ] ** ɪs ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴀɴᴅ ʜɪɢʜ-ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ᴛᴏ ᴅᴇʟɪᴠᴇʀ ᴄʀʏsᴛᴀʟ-ᴄᴇᴀʀ ᴀᴜᴅɪᴏ sᴛʀᴇᴀᴍɪɴɢ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs ᴡɪᴛʜ ᴇᴀsᴇ. ᴇɴᴊᴏʏ sᴍᴏᴏᴛʜ ᴘʟᴀʏʙᴀᴄᴋ, ᴀᴅᴠᴀɴᴄᴇᴅ ᴄᴏɴᴛʀᴏʟs ᴀɴᴅ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴍᴜsɪᴄ ᴇxᴘᴇʀɪᴇɴᴄᴇ ✨

❖ **ʙᴏᴛ ғᴜʟʟ ɪɴғᴏʀᴍᴀᴛɪᴏɴ :**
├──🚀 **ᴠᴇʀsɪᴏɴ** : `𝟷.𝟶.𝟶`
├──👨‍💻 **ᴅᴇᴠᴇʟᴏᴘᴇʀ** : @{DEV_USERNAME}
├──📢 **ᴜᴘᴅᴀᴛᴇ's** : [ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ]({config.SUPPORT_CHANNEL})
├──💾 **ᴅᴀᴛᴀʙᴀsᴇ** : `ᴍᴏɴɢᴏᴅʙ`
├──🖥️ **sᴇʀᴠᴇʀ** : `ᴠɪʀᴛᴜᴀʟ ᴘʀɪᴠᴀᴛᴇ sᴇʀᴠᴇʀ`
└──⚡ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ** : `ʏᴏᴜᴛᴜʙᴇ ᴍᴜsɪᴄ`

📝 **ʟᴀɴɢᴜᴀɢᴇ & ғʀᴀᴍᴇᴡᴏʀᴋ :**
*ᴍᴏᴅᴇʀɴ ᴘʏᴛʜᴏɴ | ᴘʏ-ᴛɢᴄᴀʟʟs ᴠ𝟸.x | ᴘʏʀᴏɢʀᴀᴍ*

🟢 **ᴏɴʟɪɴᴇ sɪɴᴄᴇ :** `𝟶𝟷/𝟶𝟷/𝟸𝟶𝟸𝟻`

🔐 **ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ :**
> ɪғ ʏᴏᴜ ᴜsᴇ **sσηᴧʟɪ ϻυsɪᴄ [ ησ ᴧᴅs ]** ғᴏʀ ᴀɴʏ ᴘᴜʀᴘᴏsᴇ, ʏᴏᴜ ᴀɢʀᴇᴇ ᴛᴏ ᴛʜᴇ ᴛᴇʀᴍs ᴀɴᴅ ᴄᴏɴᴅɪᴛɪᴏɴs ᴡʀɪᴛᴛᴇɴ ɪɴ `/ᴘʀɪᴠᴀᴄʏ`. ᴛʜᴇ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ ᴍᴀʏ ʙᴇ ᴜᴘᴅᴀᴛᴇᴅ ᴏʀ ᴄʜᴀɴɢᴇᴅ ᴀᴛ ᴀɴʏ ᴛɪᴍᴇ ᴡɪᴛʜᴏᴜᴛ ᴘʀɪᴏʀ ɴᴏᴛɪᴄᴇ.
"""

# --- [ FIX: ABOUT CALLBACK HANDLER ] ---
@app.on_callback_query(filters.regex("about_callback"))
async def on_about_click(client, query: CallbackQuery):
    await query.answer()
    await query.edit_message_text(
        text=get_about_text(),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("◁ ʙᴀᴄᴋ", callback_data="settingsback_helper")]]
        )
    )

# --- [ FIX: BACK BUTTON HANDLER ] ---
@app.on_callback_query(filters.regex("settingsback_helper"))
async def on_back_click(client, query: CallbackQuery):
    await query.answer()
    language = await get_lang(query.message.chat.id)
    _ = get_string(language)
    UP, CPU, RAM, DISK = await bot_sys_stats()
    out = private_panel(_)
    await query.edit_message_text(
        text=_["start_2"].format(query.from_user.mention, app.mention, UP, DISK, CPU, RAM),
        reply_markup=InlineKeyboardMarkup(out),
    )

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_GROUP),
                protect_content=True,
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_GROUP),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        UP, CPU, RAM, DISK = await bot_sys_stats()
        await message.reply_photo(
            photo=config.START_IMG_URL,
            caption=_["start_2"].format(message.from_user.mention, app.mention, UP, DISK, CPU, RAM),
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOG_GROUP_ID,
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_GROUP,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex) 
