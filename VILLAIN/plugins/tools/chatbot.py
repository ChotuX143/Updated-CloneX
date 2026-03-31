import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ChatType
from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI, OWNER_ID
from VILLAIN import app

# ================= SAFE G4F =================
try:
    import g4f
    G4F_AVAILABLE = True
except Exception:
    g4f = None
    G4F_AVAILABLE = False

# ================= CONFIG =================
BOT_USERNAME = "TamannaCloneBot"   # without @

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["tamanna_chatbot"]
chatbot_col = db["chatbot_settings"]
memory_col = db["chatbot_memory"]
used_col = db["used_replies"]

# ================= OWNER CHECK =================
def is_owner(user_id: int) -> bool:
    if isinstance(OWNER_ID, list):
        return user_id in OWNER_ID
    return user_id == OWNER_ID


# ================= DB =================
async def is_chatbot_on(chat_id: int) -> bool:
    data = await chatbot_col.find_one({"_id": chat_id})
    if not data:
        await chatbot_col.insert_one({"_id": chat_id, "enabled": False})
        return False
    return data.get("enabled", False)


async def set_chatbot(chat_id: int, state: bool):
    await chatbot_col.update_one(
        {"_id": chat_id},
        {"$set": {"enabled": state}},
        upsert=True
    )


async def get_memory(chat_id: int, user_id: int):
    return await memory_col.find_one({"_id": f"{chat_id}_{user_id}"})


async def save_memory(chat_id: int, user_id: int, message_text: str, reply_text: str):
    await memory_col.update_one(
        {"_id": f"{chat_id}_{user_id}"},
        {
            "$set": {
                "chat_id": chat_id,
                "user_id": user_id,
                "last_message": message_text.lower().strip(),
                "last_reply": reply_text.strip(),
            }
        },
        upsert=True
    )


async def is_reply_used(chat_id: int, reply: str):
    return await used_col.find_one({"chat_id": chat_id, "reply": reply})


async def save_used_reply(chat_id: int, reply: str):
    await used_col.insert_one({"chat_id": chat_id, "reply": reply})


# ================= HELPERS =================
def contains_link(text: str) -> bool:
    if not text:
        return False
    link_pattern = r"(https?://\S+|t\.me/\S+|www\.\S+|\S+\.(com|in|net|org|io|me)\b)"
    return bool(re.search(link_pattern, text.lower()))


def is_for_bot(message: Message) -> bool:
    text = (message.text or "").strip()
    if not text:
        return False

    # direct reply to bot
    if message.reply_to_message:
        replied_user = message.reply_to_message.from_user
        if replied_user and replied_user.is_self:
            return True

    # mention bot username
    if f"@{BOT_USERNAME.lower()}" in text.lower():
        return True

    return False


# ================= AI REPLY =================
async def generate_g4f_reply(chat_id: int, user_id: int, text: str) -> str | None:
    if not G4F_AVAILABLE:
        return None

    memory = await get_memory(chat_id, user_id)
    last_reply = memory.get("last_reply", "") if memory else ""
    last_message = memory.get("last_message", "") if memory else ""

    for _ in range(5):
        prompt = f"""
Tumhara naam TAMANNA 💖 hai.

Tum ek sweet, natural, human-like ladki ho.

STRICT RULES:
- Sirf 1 line me short reply do
- Max 8-10 words
- Hinglish/Hindi
- Har reply unique ho
- Same reply repeat mat karo
- Last reply se alag ho
- Light emoji use karo
- AI ya bot hone ka zikr mat karo

Previous user message: {last_message}
Previous Tamanna reply: {last_reply}

User: {text}
Tamanna:
"""

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": prompt}],
            )

            reply = str(response).strip()
            reply = reply.split("\n")[0].strip()

            if len(reply) > 80:
                reply = reply[:80].strip()

            if not reply:
                continue

            already_used = await is_reply_used(chat_id, reply)
            if reply != last_reply and not already_used:
                await save_used_reply(chat_id, reply)
                return reply

        except Exception:
            continue

    return None


# ================= COMMAND =================
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_control(_, message: Message):
    if not message.from_user:
        return

    try:
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        is_admin = bool(member.privileges and member.privileges.can_manage_chat)
    except Exception:
        is_admin = False

    if not is_admin and not is_owner(message.from_user.id):
        return await message.reply_text("❌ Only admins or owner can control chatbot.")

    if len(message.command) < 2:
        enabled = await is_chatbot_on(message.chat.id)
        if enabled:
            return await message.reply_text("✅ Chatbot is enabled here.")
        return await message.reply_text("❌ Chatbot is disabled here.")

    arg = message.command[1].lower()

    if arg == "on":
        await set_chatbot(message.chat.id, True)
        return await message.reply_text("✅ Chatbot is enabled here.")

    if arg == "off":
        await set_chatbot(message.chat.id, False)
        return await message.reply_text("❌ Chatbot is disabled here.")

    return await message.reply_text("Use: /chatbot on or /chatbot off")


# ================= MAIN CHATBOT =================
@app.on_message(
    filters.text
    & ~filters.bot
    & ~filters.me
    & ~filters.via_bot
    & ~filters.regex(r"^[/#]")
)
async def smart_chat(client: Client, message: Message):
    if not message.from_user or not message.text:
        return

    text = message.text.strip()

    if len(text) < 2:
        return

    if contains_link(text):
        return

    enabled = await is_chatbot_on(message.chat.id)
    if not enabled:
        return

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if not is_for_bot(message):
            return

    try:
        await message.reply_chat_action(ChatAction.TYPING)
    except Exception:
        pass

    await asyncio.sleep(1)

    try:
        reply = await generate_g4f_reply(message.chat.id, message.from_user.id, text)

        if not reply:
            return

        await save_memory(message.chat.id, message.from_user.id, text, reply)
        await message.reply_text(reply)

    except Exception:
        try:
            await message.reply_text("Thoda wait karo na 🥀")
        except Exception:
            pass
