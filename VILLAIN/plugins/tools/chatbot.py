import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, OWNER_ID
from VILLAIN import app as dev

# ================= SAFE G4F IMPORT =================
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
settings_col = db["settings"]
memory_col = db["memory"]

# ================= OWNER CHECK =================
def is_owner(user_id: int):
    if isinstance(OWNER_ID, list):
        return user_id in OWNER_ID
    return user_id == OWNER_ID

# ================= SETTINGS =================
async def is_chatbot_enabled(chat_id: int):
    data = await settings_col.find_one({"_id": chat_id})
    if not data:
        # default OFF
        await settings_col.insert_one({"_id": chat_id, "enabled": False})
        return False
    return data.get("enabled", False)

async def set_chatbot(chat_id: int, state: bool):
    await settings_col.update_one(
        {"_id": chat_id},
        {"$set": {"enabled": state}},
        upsert=True
    )

# ================= MEMORY =================
async def get_user_memory(chat_id: int, user_id: int):
    return await memory_col.find_one({"_id": f"{chat_id}_{user_id}"})

async def save_user_memory(chat_id: int, user_id: int, user_name: str, message_text: str, reply_text: str):
    await memory_col.update_one(
        {"_id": f"{chat_id}_{user_id}"},
        {
            "$set": {
                "chat_id": chat_id,
                "user_id": user_id,
                "user_name": user_name,
                "last_message": message_text.strip().lower(),
                "last_reply": reply_text.strip(),
            }
        },
        upsert=True
    )

# ================= HELPERS =================
def clean_text(text: str):
    if not text:
        return ""
    return text.strip()

def contains_link(text: str):
    if not text:
        return False
    link_pattern = r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)"
    return bool(re.search(link_pattern, text, flags=re.IGNORECASE))

def is_message_for_someone_else(message: Message):
    try:
        # अगर reply kisi aur user ko hai
        if message.reply_to_message:
            replied_user = message.reply_to_message.from_user
            if replied_user and not replied_user.is_self:
                return True

        # अगर mention kisi aur ka hai
        if message.entities and message.text:
            for entity in message.entities:
                etype = str(entity.type).lower()
                if "mention" in etype:
                    mention_text = message.text[entity.offset: entity.offset + entity.length]
                    if mention_text.lower() != f"@{BOT_USERNAME.lower()}":
                        return True
        return False
    except Exception:
        return False

# ================= AI REPLY =================
async def generate_ai_reply(chat_id: int, user_id: int, user_name: str, text: str):
    memory = await get_user_memory(chat_id, user_id)
    last_reply = memory.get("last_reply") if memory else ""
    last_message = memory.get("last_message") if memory else ""

    clean = text.strip().lower()

    if not G4F_AVAILABLE:
        if clean == last_message:
            return "Achha, kuch aur bolo na 😊"
        return "Hmm... bolo, main sun rahi hoon 💖"

    prompt = f"""
Tumhara naam TAMANNA 💖 hai.
Tum ek real, sweet, friendly, emotional ladki ho.
Tum study help, normal baat, support aur pyari conversation karti ho.
Tumhara tone human-like hona chahiye.

Owner: @l_HEART_BEAT_l

Rules:
- Har valid message ka short reply dena hai
- Reply Hindi / Hinglish / simple mixed language me ho
- Reply 1 ya 2 line ka ho
- Emoji halka aur natural use karo 😊💖🥀
- Same reply repeat mat karo
- Natural, pyara aur soft tone rakho
- Sad message par emotional support do
- Study message par helpful reply do
- Kabhi AI, model, system, bot, prompt ka zikr mat karo
- Over long reply mat do
- Last reply se alag reply dena

Previous user message: {last_message}
Previous Tamanna reply: {last_reply}

Current user name: {user_name}
Current user message: {text}

Tamanna:
"""

    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": prompt}],
        )

        final_answer = str(response).strip()

        if not final_answer:
            return "Hmm... samajh rahi hoon 😊"

        if len(final_answer) > 250:
            final_answer = final_answer[:250].strip()

        if final_answer.strip() == (last_reply or "").strip():
            return "Acha ji, aur batao 💖"

        return final_answer

    except Exception:
        if clean == last_message:
            return "Same baat phir se boli na 😄"
        return "Thoda sa ruk jao na 🥀"

# ================= COMMAND =================
@dev.on_message(filters.command("chatbot") & filters.group)
async def chatbot_control(_, message: Message):
    if not message.from_user:
        return

    try:
        member = await dev.get_chat_member(message.chat.id, message.from_user.id)
        is_admin = bool(member.privileges and member.privileges.can_manage_chat)
    except Exception:
        is_admin = False

    if not is_admin and not is_owner(message.from_user.id):
        return await message.reply_text("❌ Only admins or owner can control chatbot.")

    if len(message.command) < 2:
        state = await is_chatbot_enabled(message.chat.id)
        return await message.reply_text(
            f"🤖 **Tamanna Chatbot Status:** {'Enabled ✅' if state else 'Disabled ❌'}\n\n"
            "**Usage:**\n`/chatbot on`\n`/chatbot off`"
        )

    arg = message.command[1].lower()

    if arg == "on":
        await set_chatbot(message.chat.id, True)
        await message.reply_text("✅ **Tamanna Chatbot Enabled 💖**")

    elif arg == "off":
        await set_chatbot(message.chat.id, False)
        await message.reply_text("❌ **Tamanna Chatbot Disabled 🥀**")

    else:
        await message.reply_text(
            "⚠️ **Invalid option**\n\n**Use:**\n`/chatbot on`\n`/chatbot off`"
        )

# ================= MAIN HANDLER =================
@dev.on_message(
    filters.text
    & filters.group
    & ~filters.bot
    & ~filters.via_bot
    & ~filters.regex(r"^[/#]")
)
async def smart_bot_handler(client, message: Message):
    try:
        if not message or not message.text:
            return

        if not message.from_user:
            return

        # default OFF rahega jab tak /chatbot on na ho
        if not await is_chatbot_enabled(message.chat.id):
            return

        text = clean_text(message.text)

        if len(text) < 2:
            return

        if is_message_for_someone_else(message):
            return

        if contains_link(text):
            return

        if text.startswith("/") or text.startswith("#"):
            return

        await message.reply_chat_action(ChatAction.TYPING)
        await asyncio.sleep(1)

        final_answer = await generate_ai_reply(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            user_name=message.from_user.first_name,
            text=text
        )

        if not final_answer:
            final_answer = "Hmm... samajh rahi hoon 😊"

        await save_user_memory(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            user_name=message.from_user.first_name,
            message_text=text,
            reply_text=final_answer
        )

        await message.reply_text(final_answer)

    except Exception:
        try:
            await message.reply_text("Thoda sa ruk jao na 🥀")
        except Exception:
            pass
