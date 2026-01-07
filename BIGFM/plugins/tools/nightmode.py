from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import enums, filters
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Aapke bot ke imports
from BIGFM import app 
from BIGFM.core.mongo import mongodb

# --- DATABASE LOGIC (Isi file mein) ---
nightdb = mongodb.nightmode

async def get_nightchats() -> list:
    chats = nightdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    async for chat in chats:
        chats_list.append(chat)
    return chats_list

async def nightmode_on(chat_id: int):
    return await nightdb.insert_one({"chat_id": chat_id})

async def nightmode_off(chat_id: int):
    return await nightdb.delete_one({"chat_id": chat_id})

# --- PERMISSIONS ---
CLOSE_CHAT = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_send_polls=False,
    can_change_info=False,
    can_add_web_page_previews=False,
    can_pin_messages=False,
    can_invite_users=True,
)

OPEN_CHAT = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_send_polls=True,
    can_change_info=True,
    can_add_web_page_previews=True,
    can_pin_messages=True,
    can_invite_users=True,
)

# --- BUTTONS ---
buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("๏ ᴇɴᴀʙʟᴇ ๏", callback_data="add_night"),
            InlineKeyboardButton("๏ ᴅɪsᴀʙʟᴇ ๏", callback_data="rm_night"),
        ]
    ]
)

add_buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ]
    ]
)

# --- COMMANDS ---
@app.on_message(filters.command("nightmode") & filters.group)
async def _nightmode(_, message: Message):
    return await message.reply_photo(
        photo="https://telegra.ph//file/06649d4d0bbf4285238ee.jpg",
        caption="**ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ɴɪɢʜᴛᴍᴏᴅᴇ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**",
        reply_markup=buttons,
    )

# --- CALLBACK ---
@app.on_callback_query(filters.regex("^(add_night|rm_night)$"))
async def nightcb(_, query: CallbackQuery):
    data = query.data
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    # Admin check
    user = await app.get_chat_member(chat_id, user_id)
    if user.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await query.answer("Aap admin nahi hain!", show_alert=True)

    check_night = await nightdb.find_one({"chat_id": chat_id})

    if data == "add_night":
        if check_night:
            await query.message.edit_caption("**๏ ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.**")
        else:
            await nightmode_on(chat_id)
            await query.message.edit_caption("**๏ ɴɪɢʜᴛᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ! Group 12AM band hoga aur 6AM khulega.**")

    elif data == "rm_night":
        if check_night:
            await nightmode_off(chat_id)
            await query.message.edit_caption("**๏ ɴɪɢʜᴛᴍᴏᴅᴇ ᴅɪsᴀʙʟᴇᴅ.**")
        else:
            await query.message.edit_caption("**๏ ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ.**")

# --- AUTO FUNCTIONS ---

async def start_nightmode():
    chats = await get_nightchats()
    for chat in chats:
        chat_id = int(chat["chat_id"])
        try:
            await app.send_photo(
                chat_id,
                photo="https://telegra.ph//file/06649d4d0bbf4285238ee.jpg",
                caption="**ᴍᴀʏ ᴛʜᴇ ᴀɴɢᴇʟs ғʀᴏᴍ ʜᴇᴀᴠᴇɴ ʙʀɪɴɢ ᴛʜᴇ sᴡᴇᴇᴛᴇsᴛ ᴏғ ᴀʟʟ ᴅʀᴇᴀᴍs ғᴏʀ ʏᴏᴜ.\n\nɢʀᴏᴜᴘ ɪs ᴄʟᴏsɪɴɢ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴇᴠᴇʀʏᴏɴᴇ !**",
                reply_markup=add_buttons,
            )
            await app.set_chat_permissions(chat_id, CLOSE_CHAT)
        except:
            continue

async def close_nightmode():
    chats = await get_nightchats()
    for chat in chats:
        chat_id = int(chat["chat_id"])
        try:
            await app.send_photo(
                chat_id,
                photo="https://telegra.ph//file/14ec9c3ff42b59867040a.jpg",
                caption="**ɢʀᴏᴜᴘ ɪs ᴏᴘᴇɴɪɴɢ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ᴇᴠᴇʀʏᴏɴᴇ !\n\nᴍᴀʏ ᴛʜɪs ᴅᴀʏ ᴄᴏᴍᴇ ᴡɪᴛʜ ᴀʟʟ ᴛʜᴇ ʟᴏᴠᴇ ʏᴏᴜʀ ʜᴇᴀʀᴛ ᴄᴀɴ ʜᴏʟᴅ.**",
                reply_markup=add_buttons,
            )
            await app.set_chat_permissions(chat_id, OPEN_CHAT)
        except:
            continue

# --- SCHEDULER ---
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(start_nightmode, trigger="cron", hour=0, minute=0) # 12 AM
scheduler.add_job(close_nightmode, trigger="cron", hour=6, minute=0) # 6 AM
scheduler.start()

__MODULE__ = "Nɪɢʜᴛᴍᴏᴅᴇ"
__HELP__ = "/nightmode - Enable/Disable automatic group closing."
