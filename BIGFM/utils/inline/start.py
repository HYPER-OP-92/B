import sys
import config
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from BIGFM import app

# --- 1. AAPKA TEXT FUNCTION ---
def get_about_text():
    MASTER_DEV = "кιяυ"
    DEV_NAME = "кιяυ" 
    
    if DEV_NAME != MASTER_DEV:
        return "⚠️ **sʏsᴛᴇᴍ ᴇʀʀᴏʀ:** Credits Tampered!"

    # Ye hai wo text jo aapko show karna hai
    return f"""
🎧 **sσηᴧʟɪ ϻυsɪᴄ [ ησ ᴧᴅs ]**
*ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ ᴅᴊ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ*

ᴇɴᴊᴏʏ sᴍᴏᴏᴛʜ ᴘʟᴀʏʙᴀᴄᴋ, ᴀᴅᴠᴀɴᴄᴇᴅ ᴄᴏɴᴛʀᴏʟs, ᴀɴᴅ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴀᴜᴅɪᴏ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴡɪᴛʜᴏᴜᴛ ᴀ sɪɴɢʟᴇ ᴀᴅ.

**◈ ǫᴜɪᴄᴋ ɪɴғᴏ ◈**
╰ ᴠᴇʀsɪᴏɴ : 𝟷.𝟶.𝟶
╰ ᴅᴇᴠ : [ {MASTER_DEV} ](https://t.me/KIRU_OP) 
╰ sᴜᴘᴘᴏʀᴛ : [ᴜᴘᴅᴀᴛᴇs]({getattr(config, 'SUPPORT_CHANNEL', 'https://t.me/about_deadly_venom')})
╰ sᴛᴀᴛᴜs : ᴘᴜʙʟɪᴄ ʀᴇʟᴇᴀsᴇ

── sɪɴᴄᴇ 𝟶𝟷.𝟶𝟷.𝟸𝟶𝟸𝟶 ──
"""

# --- 2. AAPKE BUTTONS ---
def private_panel(_):
    buttons = [
        [InlineKeyboardButton(text="➕ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"https://t.me/{app.username}?startgroup=true")],
        [InlineKeyboardButton(text="💬 sᴜᴘᴘᴏʀᴛ ↗️", url=config.SUPPORT_GROUP),
         InlineKeyboardButton(text="ɴᴇᴡs 📰 ↗️", url=config.SUPPORT_CHANNEL)],
        [InlineKeyboardButton(text="📜 ᴘʀɪᴠᴀᴄʏ", url="https://telegra.ph/Privacy-Policy"),
         InlineKeyboardButton(text="ᴀʙᴏᴜᴛ ℹ️", callback_data="about_callback")], # Ye callback important hai
        [InlineKeyboardButton(text="📖 ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅ's 📖", callback_data="settings_back_helper")],
    ]
    return buttons

# --- 3. FIX: CALLBACK HANDLER (ISKE BINA TEXT NAHI AYUGA) ---

@app.on_callback_query(filters.regex("about_callback"))
async def on_about_click(client, query: CallbackQuery):
    await query.answer() # Button click ka loading circle hatane ke liye
    
    # YAHAN HUM TEXT KO BULA RAHE HAIN
    tax_text = get_about_text() 
    
    await query.edit_message_text(
        text=tax_text, # Ab tax_text screen par dikhega
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("◁ ʙᴀᴄᴋ", callback_data="settings_back_helper")]
            ]
        )
    )

@app.on_callback_query(filters.regex("settings_back_helper"))
async def on_back_click(client, query: CallbackQuery):
    await query.answer()
    # Wapas main start menu par jaane ke liye
    await query.edit_message_text(
        text=f"ʜᴇʟʟᴏ {query.from_user.mention} !\nᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏ sᴏɴᴀʟɪ ᴍᴜsɪᴄ.",
        reply_markup=InlineKeyboardMarkup(private_panel(None))
) 
