from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from BIGFM import app

def help_pannel(_, START: Union[bool, int] = None):
    # Back/Close logic
    first = [InlineKeyboardButton(text="◁ ʙᴀᴄᴋ", callback_data=f"close")]
    second = [
        InlineKeyboardButton(
            text="◁ ʙᴀᴄᴋ",
            callback_data=f"settingsback_helper",
        ),
    ]
    mark = second if START else first
    
    upl = InlineKeyboardMarkup(
        [
            # Row 1 (Header Style)
            [
                InlineKeyboardButton(
                    text="ʙᴜɢ ʀᴇᴘᴏʀᴛ sᴇᴄᴛɪᴏɴ",
                    callback_data="help_callback hb1",
                ),
            ],
            # Row 2
            [
                InlineKeyboardButton(text="ᴀᴅᴍɪɴ", callback_data="help_callback hb2"),
                InlineKeyboardButton(text="ᴀᴜᴛʜ", callback_data="help_callback hb3"),
                InlineKeyboardButton(text="ʙʟᴀᴄᴋʟɪsᴛ", callback_data="help_callback hb4"),
            ],
            # Row 3
            [
                InlineKeyboardButton(text="ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="help_callback hb5"),
                InlineKeyboardButton(text="ᴘɪɴɢ", callback_data="help_callback hb6"),
                InlineKeyboardButton(text="ᴘʟᴀʏ", callback_data="help_callback hb7"),
            ],
            # Row 4
            [
                InlineKeyboardButton(text="sᴜᴅᴏ", callback_data="help_callback hb8"),
                InlineKeyboardButton(text="ᴠɪᴅᴇᴏᴄʜᴀᴛ", callback_data="help_callback hb9"),
                InlineKeyboardButton(text="sᴛᴀʀᴛ", callback_data="help_callback hb10"),
            ],
            # Row 5
            [
                InlineKeyboardButton(text="ʟʏʀɪᴄs", callback_data="help_callback hb11"),
                InlineKeyboardButton(text="ᴘʟᴀʏʟɪsᴛ", callback_data="help_callback hb12"),
                InlineKeyboardButton(text="ɢʙᴀɴ", callback_data="help_callback hb13"),
            ],
            # Row 6 (Ab yahan 3 buttons hain)
            [
                InlineKeyboardButton(text="ɢʟᴏʙᴀʟ", callback_data="help_callback hb14"),
                InlineKeyboardButton(text="ᴇxᴛʀᴀ", callback_data="help_callback hb15"),
                InlineKeyboardButton(text="sᴏɴɢ", callback_data="help_callback hb16"), # Ye missing tha
            ],
            # Row 7 (Navigation Buttons)
            [
                InlineKeyboardButton(text="◁ ʙᴀᴄᴋ", callback_data="close"),
                InlineKeyboardButton(text="ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{app.username}?startgroup=true"),
                InlineKeyboardButton(text="ɴᴇxᴛ ▷", callback_data="help_callback hb_page2"),
            ],
            # Row 8 (Dynamic Back Button)
            mark,
        ]
    )
    return upl
