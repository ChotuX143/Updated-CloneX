import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, OWNER_ID
from VILLAIN import app as dev

# ================= SAFE G4F =================
try:
    import g4f
    G4F_AVAILABLE = True
except:
    g4f = None
    G4F_AVAILABLE = False

# ================= CONFIG =================
BOT_USERNAME = "TamannaCloneBot"

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["tamanna_chatbot"]

settings_col = db["settings"]
memory_col = db["memory"]
used_col = db["used_replies"]

# ================= OWNER =================
def is_owner(user_id):
    if isinstance(OWNER_ID, list):
        return user_id in OWNER_ID
    return user_id == OWNER_ID

# ================= SETTINGS =================
async def is_chatbot_enabled(chat_id):
    data = await settings_col.find_one({"_id": chat_id})
    if not data:
        await settings_col.insert_one({"_id": chat_id, "enabled": False})
        return False
    return data.get("enabled", False)

async def set_chatbot(chat_id, state):
    await settings_col.update_one(
        {"_id": chat_id},
        {"$set": {"enabled": state}},
        upsert=True
    )

# ================= MEMORY =================
async def get_user_memory(chat_id, user_id):
    return await memory_col.find_one({"_id": f"{chat_id}_{user_id}"})

async def save_user_memory(chat_id, user_id, name, msg, reply):
    await memory_col.update_one(
        {"_id": f"{chat_id}_{user_id}"},
        {"$set": {"last_message": msg.lower(), "last_reply": reply}},
        upsert=True
    )

# ================= USED REPLIES =================
async def is_reply_used(chat_id, reply):
    return await used_col.find_one({"chat_id": chat_id, "reply": reply})

async def save_used_reply(chat_id, reply):
    await used_col.insert_one({
        "chat_id": chat_id,
        "reply": reply
    })

# ================= HELPERS =================
def clean_text(text):
    return text.strip() if text else ""

def contains_link(text):
    return bool(re.search(r"(https?://|t\.me/|www\.)", text.lower()))

def is_message_for_someone_else(message: Message):
    try:
        if message.reply_to_message:
            u = message.reply_to_message.from_user
            if u and not u.is_self:
                return True

        if message.entities and message.text:
            for e in message.entities:
                if "mention" in str(e.type).lower():
                    m = message.text[e.offset:e.offset+e.length]
                    if m.lower() != f"@{BOT_USERNAME.lower()}":
                        return True
        return False
    except:
        return False

# ================= AI UNIQUE REPLY =================
async def generate_ai_reply(chat_id, user_id, name, text):
    if not G4F_AVAILABLE:
        return None

    memory = await get_user_memory(chat_id, user_id)
    last_reply = memory.get("last_reply") if memory else ""
    last_message = memory.get("last_message") if memory else ""

    for _ in range(5):  # retry for unique reply
        prompt = f"""
Tum Tamanna ho 💖

Rules:
- 1 line reply
- max 10 words
- Hinglish
- har reply UNIQUE
- kabhi repeat nahi

User: {text}
Tamanna:
"""

        try:
            res = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": prompt}],
            )

            reply = str(res).strip()

            # 1 line force
            reply = reply.split("\n")[0].strip()

            # length limit
            if len(reply) > 80:
                reply = reply[:80]

            used = await is_reply_used(chat_id, reply)

            if not used and reply != last_reply:
                await save_used_reply(chat_id, reply)
                return reply

        except:
            continue

    return None

# ================= COMMAND =================
@dev.on_message(filters.command("chatbot") & filters.group)
async def chatbot_control(_, message: Message):
    if not message.from_user:
        return

    try:
        m = await dev.get_chat_member(message.chat.id, message.from_user.id)
        admin = m.privileges and m.privileges.can_manage_chat
    except:
        admin = False

    if not admin and not is_owner(message.from_user.id):
        return await message.reply_text("❌ Admin only")

    if len(message.command) < 2:
        state = await is_chatbot_enabled(message.chat.id)
        return await message.reply_text(
            f"🤖 Status: {'ON ✅' if state else 'OFF ❌'}\n/chatbot on\n/chatbot off"
        )

    arg = message.command[1].lower()

    if arg == "on":
        await set_chatbot(message.chat.id, True)
        await message.reply_text("✅ Chatbot ON")

    elif arg == "off":
        await set_chatbot(message.chat.id, False)
        await message.reply_text("❌ Chatbot OFF")

# ================= MAIN =================
@dev.on_message(filters.text & filters.group & ~filters.bot)
async def chatbot_handler(_, message: Message):
    try:
        if not message.from_user:
            return

        if not await is_chatbot_enabled(message.chat.id):
            return

        text = clean_text(message.text)

        if len(text) < 2:
            return

        if contains_link(text):
            return

        if is_message_for_someone_else(message):
            return

        if text.startswith("/") or text.startswith("#"):
            return

        await message.reply_chat_action(ChatAction.TYPING)
        await asyncio.sleep(1)

        reply = await generate_ai_reply(
            message.chat.id,
            message.from_user.id,
            message.from_user.first_name,
            text
        )

        if not reply:
            return

        await save_user_memory(
            message.chat.id,
            message.from_user.id,
            message.from_user.first_name,
            text,
            reply
        )

        await message.reply_text(reply)

    except:
        pass
