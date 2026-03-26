from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, Message
import config
import asyncio
from VILLAIN import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT
            ),
        ],
    ]
    return buttons



def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
        ],
        [
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID),
            InlineKeyboardButton(
                text="💌 ʏᴛ-ᴀᴘɪ",
                callback_data="oapi"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_2"],
                callback_data="clone_me"
            ),
            InlineKeyboardButton(
                text="ɢᴧϻ𝛆𝐬",
                callback_data="shiv"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="settings_back_helper"
            ),
        ],
    ]
    return buttons


def private_panell(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
    ]
    return buttons







#-----------------------------+-------------##



import sys
import platform
from time import time
from datetime import datetime
import pyrogram
from pyrogram import filters
from pyrogram.types import CallbackQuery
  

# Pyrogram version
pver = pyrogram.__version__

# Bot start time (uptime ke liye)
BOT_START_TIME = datetime.now()

def get_uptime():
    uptime = datetime.now() - BOT_START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


@app.on_callback_query(filters.regex("oapi"))
async def show_bot_info(c: app, q: CallbackQuery):
    start = time()
    m = await c.send_message(q.message.chat.id, "🧾ᴀᴘɪ sᴛᴀᴛᴜs........")
    delta_ping = (time() - start) * 1000
    await m.delete()

    # Short popup text (under 200 chars)
    short_txt = f"""
🧾ᴀᴘɪ sᴛᴀᴛᴜs

ᴅʙ : ᴏɴʟɪɴᴇ
ʀɪsʜᴜ ᴀᴘɪ : ʀᴇsᴘᴏɴsɪᴠᴇ
ᴀᴘɪ ᴘɪɴɢ : {delta_ping:.2f} ms
ᴀᴘɪ ᴜᴘᴛɪᴍᴇ : {get_uptime()}

✅ ᴇᴠᴇʀʏᴛʜɪɴɢ ғɪɴᴇ
"""

    await q.answer(short_txt.strip(), show_alert=True)








