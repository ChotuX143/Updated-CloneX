import re
import os
import asyncio
import aiohttp

from pyrogram import filters
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI, OWNER_ID
from VILLAIN import app

# ================= DATABASE =================

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["chatbot_db"]
chatbot_db = db["chatbot_settings"]

# ================= CONFIG =================

BOT_USERNAME = "TamannaCloneBot"  # without @

AI_API_URL = os.getenv("AI_API_URL", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

# ================= DATABASE FUNCTIONS =================

async def is_chatbot_enabled(chat_id: int) -> bool:
    data = await chatbot_db.find_one({"chat_id": chat_id})
    return bool(data and data.get("enabled", False))


async def set_chatbot(chat_id: int, enabled: bool):
    await chatbot_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": enabled}},
        upsert=True
    )


def is_owner(user_id: int) -> bool:
    if isinstance(OWNER_ID, list):
        return user_id in OWNER_ID
    return user_id == OWNER_ID


# ================= HELPERS =================

def contains_link(text: str) -> bool:
    pattern = r"(https?://\S+|t\.me/\S+|www\.\S+)"
    return bool(re.search(pattern, text.lower()))


def is_bot_mentioned(message: Message) -> bool:
    raw_text = (message.text or message.caption or "").lower()
    return f"@{BOT_USERNAME.lower()}" in raw_text


def is_reply_to_bot(message: Message) -> bool:
    if not message.reply_to_message:
        return False

    replied = message.reply_to_message.from_user
    if not replied:
        return False

    if replied.is_self:
        return True

    username = (replied.username or "").lower()
    return username == BOT_USERNAME.lower()


def should_reply_in_group(message: Message) -> bool:
    return is_bot_mentioned(message) or is_reply_to_bot(message)


def is_gif_message(message: Message) -> bool:
    if message.animation:
        return True

    if message.document and message.document.mime_type:
        return message.document.mime_type == "image/gif"

    return False


def build_user_input(message: Message) -> str | None:
    if message.text:
        return message.text.strip()

    if is_gif_message(message):
        if message.caption:
            return f"User sent a GIF with caption: {message.caption.strip()}"
        return "User sent a GIF. Give a short cute Hinglish reaction."

    return None


def clean_response(text: str) -> str:
    if not text:
        return "Hmm... samajh rahi hoon 😊"

    text = str(text).strip()

    blocked = [
        "as an ai",
        "i am an ai",
        "i'm an ai",
        "language model",
        "openai",
        "assistant",
        "i am a bot",
        "i'm a bot",
        "artificial intelligence",
        "system prompt",
        "model",
    ]

    low = text.lower()
    for bad in blocked:
        if bad in low:
            return "Acha... tum aur batao na 😊"

    lines = [x.strip() for x in text.split("\n") if x.strip()]
    if len(lines) > 2:
        text = "\n".join(lines[:2])

    if len(text) > 180:
        text = text[:180].rsplit(" ", 1)[0] + "..."

    return text


async def get_ai_reply(user_text: str) -> str:
    if not AI_API_URL or not AI_API_KEY:
        return "Hmm... main sun rahi hoon 😊"

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Tumhara naam TAMANNA 💖 hai. "
                    "Tum ek sweet, emotional, friendly ladki ho. "
                    "Reply short, natural, human-like Hinglish/Hindi me do. "
                    "Har baar 1 ya 2 line ka pyara short reply do. "
                    "Kabhi AI, bot, assistant, OpenAI, model, system ya prompt ka zikr mat karo. "
                    "Agar user GIF bheje to uske mood ke hisaab se cute short reaction do."
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        "temperature": 0.9,
        "max_tokens": 80,
    }

    timeout = aiohttp.ClientTimeout(total=25)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(AI_API_URL, headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"API Error: {response.status}")

            data = await response.json()

            if "choices" not in data or not data["choices"]:
                return "Hmm... samajh rahi hoon 😊"

            content = data["choices"][0]["message"]["content"]
            return clean_response(content)


# ================= TOGGLE COMMAND =================

@app.on_message(filters.command("chatbot"))
async def chatbot_toggle(_, message: Message):
    if not message.from_user:
        return

    if len(message.command) < 2:
        return await message.reply_text("Use: `/chatbot on` or `/chatbot off`")

    arg = message.command[1].lower()

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        status = str(member.status).lower()

        if "administrator" not in status and "creator" not in status and not is_owner(message.from_user.id):
            return await message.reply_text("❌ Only admins can use this.")

    if arg == "on":
        await set_chatbot(message.chat.id, True)
        return await message.reply_text("✅ Chatbot enabled.")

    if arg == "off":
        await set_chatbot(message.chat.id, False)
        return await message.reply_text("❌ Chatbot disabled.")

    await message.reply_text("Use: `/chatbot on` or `/chatbot off`")


# ================= MAIN CHATBOT =================

@app.on_message(
    (filters.text | filters.animation | filters.document)
    & ~filters.bot
    & ~filters.me
    & ~filters.via_bot
    & ~filters.regex(r"^[/#]")
)
async def smart_chatbot(_, message: Message):
    if not message.from_user:
        return

    enabled = await is_chatbot_enabled(message.chat.id)
    if not enabled:
        return

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if not should_reply_in_group(message):
            return

    user_input = build_user_input(message)
    if not user_input:
        return

    raw_text = (message.text or message.caption or "").strip()

    if message.text and len(raw_text) < 2:
        return

    if raw_text and contains_link(raw_text):
        return

    await message.reply_chat_action(ChatAction.TYPING)
    await asyncio.sleep(1)

    try:
        reply = await get_ai_reply(user_input)
        await message.reply_text(reply)
    except Exception:
        await message.reply_text("Hmm... main sun rahi hoon 😊")
