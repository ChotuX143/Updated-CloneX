import re
import asyncio
import random
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
        await settings_col.insert_one({"_id": chat_id, "enabled": True})
        return True
    return data.get("enabled", True)

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
        # reply kisi aur user ko ho
        if message.reply_to_message:
            replied_user = message.reply_to_message.from_user
            if replied_user and not replied_user.is_self:
                return True

        # mention kisi aur ko ho
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

def pick_non_repeating_reply(replies, last_reply=None):
    if not replies:
        return "Hmm... samajh rahi hoon 😊"

    filtered = [r for r in replies if r.strip() != (last_reply or "").strip()]
    if filtered:
        return random.choice(filtered)
    return random.choice(replies)

# ================= REPLIES =================
FALLBACK_REPLIES = [
    "Hmm... samajh rahi hoon 😊",
    "Acha ji, aur batao 💖",
    "Haan bolo na 🥀",
    "Main sun rahi hoon 😊",
    "Theek hai, samajh gayi 💕",
    "Achha, phir kya hua? 👀",
    "Hmmm... interesting hai ✨",
    "Bolo jaan, sun rahi hoon 💖",
    "Samajh gayi, aur batao 😌",
    "Okay ji 😊",
    "Haan theek hai 💕",
    "Baat to sahi hai 😌",
]

KEYWORD_REPLIES = {
    "hi": ["Hii 😊", "Hello ji 👋", "Heyy 💖", "Hii bolo na 😄"],
    "hello": ["Hello 💕", "Hey there 😊", "Hello ji, kaise ho?"],
    "hey": ["Heyy 😌", "Haan bolo 👀", "Hey ji 💖"],
    "bye": ["Bye 👋", "Take care 💖", "Phir milte hain 😊"],
    "good night": ["Good night 🌙", "Sweet dreams 😴💖", "Shubh ratri ✨"],
    "good morning": ["Good morning ☀️", "Subah mubarak 🌸", "Morning ji 😊"],
    "love": ["Aww 💖", "Itna pyaar 😌", "Cute ho tum ❤️"],
    "miss you": ["Miss you too 🥺", "Aww ye cute tha 💕", "Main bhi yaad karungi 😌"],
    "thanks": ["Welcome 😊", "Koi baat nahi 💖", "Anytime 😄"],
    "thank you": ["Most welcome 💕", "Koi issue nahi 😊", "Hamesha 😌"],
    "ok": ["Okay 👍", "Theek hai 😊", "Done ✅"],
    "acha": ["Acha ji 😄", "Samajh gayi 😊", "Haan theek hai 💕"],
    "hmm": ["Hmm 👀", "Kya soch rahe ho? 😏", "Bolo na 😊"],
    "sad": ["Aisa mat feel karo 🥺", "Main hoon na, tension mat lo 💖", "Sab theek ho jayega 🌸"],
    "alone": ["Tum akele nahi ho 🥺", "Main yahin hoon 💖", "Khud ko itna akela mat samjho 🌸"],
    "study": ["Padhai pe focus rakho 📚", "Kis subject me help chahiye? 😊", "Chalo study ki baat karte hain ✨"],
    "exam": ["Exam ka stress mat lo 😊", "Revision karo, sab ho jayega 📚", "Main hoon help ke liye 💖"],
    "kaise ho": ["Main theek hoon 😊", "Bilkul acchi hoon, tum batao? 💕", "Main mast hoon 😄"],
    "kya kar rahe ho": ["Tumse baat 😊", "Reply de rahi hoon 💖", "Bas yahin hoon 😌"],
    "kon ho": ["Main Tamanna hoon 😊", "Tamanna yahin hai 💖", "Main Tamanna, tum batao? 😌"],
    "who are you": ["Main Tamanna hoon 😊", "Tamanna yahin hai 💖", "Main Tamanna, tum batao? 😌"],
}

# ================= AI / SMART REPLY =================
async def generate_ai_reply(chat_id: int, user_id: int, user_name: str, text: str):
    memory = await get_user_memory(chat_id, user_id)
    last_reply = memory.get("last_reply") if memory else ""
    last_message = memory.get("last_message") if memory else ""

    clean = text.strip().lower()

    # keyword-based smart replies first
    for key, replies in KEYWORD_REPLIES.items():
        if key in clean:
            return pick_non_repeating_reply(replies, last_reply)

    # if g4f not installed, fallback
    if not G4F_AVAILABLE:
        return pick_non_repeating_reply(FALLBACK_REPLIES, last_reply)

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
            return pick_non_repeating_reply(FALLBACK_REPLIES, last_reply)

        if len(final_answer) > 250:
            final_answer = final_answer[:250].strip()

        if final_answer.strip() == (last_reply or "").strip():
            return pick_non_repeating_reply(FALLBACK_REPLIES, last_reply)

        return final_answer

    except Exception:
        return pick_non_repeating_reply(FALLBACK_REPLIES, last_reply)

# ================= COMMANDS =================
@dev.on_message(filters.command("chatboton") & filters.group)
async def chatbot_on(_, message: Message):
    if not message.from_user:
        return

    try:
        member = await dev.get_chat_member(message.chat.id, message.from_user.id)
        is_admin = bool(member.privileges and member.privileges.can_manage_chat)
    except Exception:
        is_admin = False

    if not is_admin and not is_owner(message.from_user.id):
        return await message.reply_text("❌ Only admins or owner can enable chatbot.")

    await set_chatbot(message.chat.id, True)
    await message.reply_text("✅ **Tamanna chatbot enabled.**")

@dev.on_message(filters.command("chatbotoff") & filters.group)
async def chatbot_off(_, message: Message):
    if not message.from_user:
        return

    try:
        member = await dev.get_chat_member(message.chat.id, message.from_user.id)
        is_admin = bool(member.privileges and member.privileges.can_manage_chat)
    except Exception:
        is_admin = False

    if not is_admin and not is_owner(message.from_user.id):
        return await message.reply_text("❌ Only admins or owner can disable chatbot.")

    await set_chatbot(message.chat.id, False)
    await message.reply_text("❌ **Tamanna chatbot disabled.**")

@dev.on_message(filters.command("chatbot") & filters.group)
async def chatbot_status(_, message: Message):
    state = await is_chatbot_enabled(message.chat.id)
    await message.reply_text(
        f"🤖 **Tamanna Chatbot Status:** {'Enabled ✅' if state else 'Disabled ❌'}"
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
