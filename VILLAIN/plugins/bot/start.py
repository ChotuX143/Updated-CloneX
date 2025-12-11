import time
import random
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from VILLAIN import app
from VILLAIN.misc import _boot_
from VILLAIN.plugins.sudo.sudoers import sudoers_list
from VILLAIN.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from VILLAIN.utils.formatters import get_readable_time
from VILLAIN.utils.inline import help_pannel, private_panel, start_panel
from VILLAIN.utils.decorators.language import LanguageStart
from strings import get_string
from config import BANNED_USERS, STREAMI_PICS, GREET

# === Your provided constants ===
VILLAIN_STKR = [
    "CAACAgUAAxkBAAIBO2i1Spi48ZdWCNehv-GklSI9aRYWAAJ9GAACXB-pVds_sm8brMEqHgQ",
    "CAACAgUAAxkBAAIBOmi1Sogwaoh01l5-e-lJkK1VNY6MAAIlGAACKI6wVVNEvN-6z3Z7HgQ",
    "CAACAgUAAxkBAAIBPGi1Spv1tlx90xM1Q7TRNyL0fhcJAAKDGgACZSupVbmJpWW9LmXJHgQ",
    "CAACAgUAAxkBAAIBPWi1SpxJZKxuWYsZ_G06j_G_9QGkAAIsHwACdd6xVd2HOWQPA_qtHgQ",
    "CAACAgUAAxkBAAIBPmi1Sp4QFoLkZ0oN3d01kZQOHQRwAAI4FwACDDexVVp91U_1BZKFHgQ",
    "CAACAgUAAxkBAAIBP2i1SqFoa4yqgl1QSISZrQ4VuYWgAAIpFQACvTqpVWqbFSKOnWYxHgQ",
    "CAACAgUAAxkBAAIBQGi1Sqk3OGQ2jRW2rN6ZVZ7vWY2ZAAJZHQACCa-pVfefqZZtTHEdHgQ",
]

EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

emojis = ["🥰", "🔥", "💖", "😁", "😎", "🌚", "❤️‍🔥", "♥️", "🎉", "🙈"]
# ===============================

# -------------------------
# Single merged private /start
# -------------------------
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    # SAVE USER
    try:
        await add_served_user(message.from_user.id)
    except Exception:
        pass

    # 🔥 Reaction safe try/except
    try:
        await message.react(random.choice(emojis))
    except Exception:
        # ignore if reaction fails (limits/permissions)
        pass

    # Sticker animation (send then delete) — uses VILLAIN_STKR
    try:
        sticker = await message.reply_sticker(random.choice(VILLAIN_STKR))
        await asyncio.sleep(1)
        await sticker.delete()
    except Exception:
        # ignore sticker errors (if chat doesn't allow stickers or file invalid)
        pass

    # loading animation messages
    try:
        loading_1 = await message.reply_text(random.choice(GREET))
        await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ</b>")
        await asyncio.sleep(0.1)
        await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ.</b>")
        await asyncio.sleep(0.1)
        await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ..</b>")
        await asyncio.sleep(0.1)
        await loading_1.edit_text("<b>ʟᴏᴀᴅɪɴɢ...</b>")
        await asyncio.sleep(0.1)
        await loading_1.delete()
    except Exception:
        pass

    # If start has parameters
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1].strip()

        # help parameter
        if name.startswith("help") or name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(STREAMI_PICS),
                has_spoiler=True,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        # sudolist parameter
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                try:
                    return await app.send_message(
                        chat_id=config.LOGGER_ID,
                        text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>✦ ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n<b>✦ ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
                    )
                except Exception:
                    pass

        # info parameter (youtube info) — robust extraction of id
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            # normalize video id part
            video_id = name
            for p in ("info_", "info", "inf_", "inf"):
                if video_id.startswith(p):
                    video_id = video_id[len(p):]
                    break
            query = f"https://www.youtube.com/watch?v={video_id}"
            try:
                results = VideosSearch(query, limit=1)
                res = (await results.next())["result"][0]
                title = res.get("title", "Unknown Title")
                duration = res.get("duration", "Unknown")
                views = res.get("viewCount", {}).get("short", "N/A")
                thumbnail = res.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
                channellink = res.get("channel", {}).get("link", "")
                channel = res.get("channel", {}).get("name", "")
                link = res.get("link", query)
                published = res.get("publishedTime", "")
            except Exception:
                title = duration = views = thumbnail = channellink = channel = link = published = ""
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link or "https://youtube.com"),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            try:
                await m.delete()
            except Exception:
                pass
            try:
                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail or random.choice(STREAMI_PICS),
                    has_spoiler=True,
                    caption=searched_text,
                    reply_markup=key,
                )
            except Exception:
                # fallback to text message if photo fails
                await message.reply_text(searched_text, reply_markup=key)
            if await is_on_off(2):
                try:
                    return await app.send_message(
                        chat_id=config.LOGGER_ID,
                        text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
                    )
                except Exception:
                    pass
    else:
        # no params: show private panel
        out = private_panel(_)
        try:
            await message.reply_photo(
                random.choice(STREAMI_PICS),
                has_spoiler=True,
                caption=_["start_2"].format(message.from_user.mention, app.mention),
                reply_markup=InlineKeyboardMarkup(out),
            )
        except Exception:
            # fallback
            await message.reply_text(_["start_2"].format(message.from_user.mention, app.mention))
        if await is_on_off(2):
            try:
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
                )
            except Exception:
                pass

# -------------------------
# Keep your group start and welcome handlers as-is (no changes)
# -------------------------
@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        random.choice(STREAMI_PICS),
        has_spoiler=True,
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
                except Exception:
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
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_text(
                    text=_["start_3"].format(
                        message.from_user.mention,
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
