import sys
import config
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from BIGFM import app

# --- 🔐 CREDIT PROTECTION LOGIC ---
# Ye username fix hai. Agar koi isse chedega toh bot error dega.
MASTER_DEV = "кιяυ"

def get_about_text():
    # Agar kisi ne niche DEV_NAME badla toh "Something Missing" error aayega
    DEV_NAME = "" 
    
    if DEV_NAME != MASTER_DEV:
        return "⚠️ **sʏsᴛᴇᴍ ᴇʀʀᴏʀ:** sᴏᴍᴇᴛʜɪɴɢ ɪs ᴍɪssɪɴɢ!\n\nᴄʀᴇᴅɪᴛs ᴛᴀᴍᴘᴇʀᴇᴅ. ᴘʟᴇᴀsᴇ ʀᴇɪɴsᴛᴀʟʟ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ ʙᴏᴛ ғʀᴏᴍ @KIRU_OP"

    return f"""
🎧 **sσηᴧʟɪ ϻυsɪᴄ [ ησ ᴧᴅs ]**
*ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ ᴅᴊ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ*

ᴇɴᴊᴏʏ sᴍᴏᴏᴛʜ ᴘʟᴀʏʙᴀᴄᴋ, ᴀᴅᴠᴀɴᴄᴇᴅ ᴄᴏɴᴛʀᴏʟs, ᴀɴᴅ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴀᴜᴅɪᴏ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴡɪᴛʜᴏᴜᴛ ᴀ sɪɴɢʟᴇ ᴀᴅ.

**◈ ǫᴜɪᴄᴋ ɪɴғᴏ ◈**
╰ ᴠᴇʀsɪᴏɴ : 𝟷.𝟶.𝟶
╰ ᴅᴇᴠ : [ кιяυ ](https://t.me/KIRU_OP) 
╰ sᴜᴘᴘᴏʀᴛ : [ᴜᴘᴅᴀᴛᴇs]({getattr(config, 'SUPPORT_CHANNEL', 'https://t.me/about_deadly_venom')})
╰ sᴛᴀᴛᴜs : ᴘᴜʙʟɪᴄ ʀᴇʟᴇᴀsᴇ

── sɪɴᴄᴇ 𝟶𝟷.𝟶𝟷.𝟸𝟶𝟸𝟼 ──

🔐 **ᴘʀɪᴠᴀᴄʏ :** ᴡᴇ ᴅᴏ ɴᴏᴛ sᴛᴏʀᴇ ᴀɴʏ ᴜsᴇʀ ᴅᴀᴛᴀ. ʏᴏᴜʀ sᴀғᴇᴛʏ ɪs ᴏᴜʀ ᴘʀɪᴏʀɪᴛʏ.
"""

# --- 📱 MAIN LAYOUT (1-2-2-1 Format) ---
def private_panel(_):
    buttons = [
        # Row 1: Add Me (Full Width)
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        # Row 2: Support and News (Side by Side)
        [
            InlineKeyboardButton(text="💬 sᴜᴘᴘᴏʀᴛ ↗️", url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text="ɴᴇᴡs 📰 ↗️", url=config.SUPPORT_CHANNEL),
        ],
        # Row 3: Privacy (URL) and About (Callback)
        [
            InlineKeyboardButton(
                text="📜 ᴘʀɪᴠᴀᴄʏ", 
                url="https://telegra.ph/Privacy-Policy-Link" # Apna link yahan dalein
            ),
            InlineKeyboardButton(
                text="ᴀʙᴏᴜᴛ ℹ️", 
                callback_data="about_callback"
            ),
        ],
        # Row 4: Help and Commands (Full Width)
        [
            InlineKeyboardButton(
                text="📖 ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅ's 📖", 
                callback_data="settings_back_helper"
            )
        ],
    ]
    return buttons

# --- 🕹️ CALLBACK HANDLERS ---

# 1. About Button Handler
@app.on_callback_query(filters.regex("about_callback"))
async def on_about_click(client, callback_query: CallbackQuery):
    # Security check: Agar kisi ne MASTER_DEV variable ko badla
    if MASTER_DEV != "ScyxD":
        await callback_query.answer("⚠️ Something is Missing! Credits Tampered.", show_alert=True)
        return

    await callback_query.answer()
    await callback_query.edit_message_text(
        text=get_about_text(),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="◁ ʙᴀᴄᴋ", callback_data="home_back")]]
        ),
    )

# 2. Back to Home Handler
@app.on_callback_query(filters.regex("home_back"))
async def on_back_home(client, callback_query: CallbackQuery):
    await callback_query.answer()
    start_text = f"✨ ʜᴇʏ {callback_query.from_user.mention},\n\nᴛᴀᴘ ʜᴇʟᴘ ᴛᴏ ᴠɪᴇᴡ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ᴍᴏᴅᴜʟᴇs."
    await callback_query.edit_message_text(
        text=start_text,
        reply_markup=InlineKeyboardMarkup(private_panel(None))
    )

# --- 🚀 STARTUP SECURITY ---
if MASTER_DEV != "ScyxD":
    print("FATAL ERROR: Developer credits missing in code!")
    # sys.exit() # Ise uncomment karoge toh bot credit hatne par band ho jayega
