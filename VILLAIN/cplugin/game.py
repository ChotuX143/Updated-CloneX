import random
import time
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, OWNER_ID

# ---------------- DB ---------------- #
mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["rpg_bot"]
users = db["users"]

# ---------------- SAFE USER FETCH ---------------- #
async def get_real_user(client, input_user):
    try:
        user = await client.get_users(input_user)

        if not user or not user.id:
            return None

        return user
    except:
        return None

# ---------------- USER ---------------- #
async def get_user(user_id):
    user = await users.find_one({"_id": user_id})

    if not user:
        user = {
            "_id": user_id,
            "balance": 1000,
            "xp": 0,
            "level": 1,
            "protected": False,
            "dead": False,
            "last_rob": 0,
            "last_kill": 0
        }
        await users.insert_one(user)

    return user

# ---------------- BALANCE ---------------- #
@Client.on_message(filters.command(["balance", "bal"]))
async def balance(client, message):

    user_id = None
    name = None

    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            return await message.reply("❌ Channel pe ye command nahi chalega")

        if not message.reply_to_message.from_user:
            return await message.reply("❌ Invalid user")

        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        user = await get_real_user(client, message.command[1])
        if not user:
            return await message.reply("❌ Invalid user")

        user_id = user.id
        name = user.first_name

    else:
        user_id = message.from_user.id
        name = message.from_user.first_name

    user = await get_user(user_id)

    await message.reply_text(
        f"💰 **Balance of {name}:**\n\n"
        f"💸 Coins: `{user['balance']}`\n"
        f"⭐ Level: `{user['level']}`\n"
        f"🔥 XP: `{user['xp']}`"
    )

# ---------------- ADD MONEY ---------------- #
@Client.on_message(filters.command("addmoney") & filters.user(OWNER_ID))
async def addmoney(client, message):

    user_id = None
    amount = None

    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            return await message.reply("❌ Channel allowed nahi")

        if not message.reply_to_message.from_user:
            return await message.reply("❌ Invalid user")

        user_id = message.reply_to_message.from_user.id

        try:
            amount = int(message.command[1])
        except:
            return await message.reply("Usage: /addmoney amount")

    elif len(message.command) >= 3:
        user = await get_real_user(client, message.command[1])
        if not user:
            return await message.reply("❌ Invalid user")

        user_id = user.id

        try:
            amount = int(message.command[2])
        except:
            return await message.reply("❌ Invalid amount")

    else:
        return await message.reply("❌ Wrong usage")

    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )

    await message.reply(f"✅ {amount} coins added")

# ---------------- GIVE ---------------- #
@Client.on_message(filters.command("give"))
async def give(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to user")

    if message.reply_to_message.sender_chat:
        return await message.reply("❌ Channel allowed nahi")

    if not message.reply_to_message.from_user:
        return await message.reply("❌ Invalid user")

    sender = await get_user(message.from_user.id)

    if sender["dead"]:
        return await message.reply("☠️ Tum dead ho")

    receiver_id = message.reply_to_message.from_user.id

    try:
        amount = int(message.command[1])
    except:
        return await message.reply("Usage: /give amount")

    if sender["balance"] < amount:
        return await message.reply("❌ Not enough balance")

    await users.update_one({"_id": sender["_id"]}, {"$inc": {"balance": -amount}})
    await users.update_one({"_id": receiver_id}, {"$inc": {"balance": amount}})

    await message.reply("✅ Transfer successful")

# ---------------- PROTECT ---------------- #
PROTECT_TIME = 86400

@Client.on_message(filters.command("protect"))
async def protect(client, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    now = time.time()

    if user.get("protected") and user.get("protect_time", 0) > now:
        return await message.reply("🛡️ Already protected")

    await users.update_one(
        {"_id": user_id},
        {"$set": {"protected": True, "protect_time": now + PROTECT_TIME}}
    )

    await message.reply("🛡️ Protection Enabled")

# ---------------- REVIVE ---------------- #
@Client.on_message(filters.command("revive"))
async def revive(client, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user.get("dead"):
        return await message.reply("❌ Already alive")

    if user.get("balance", 0) < 300:
        return await message.reply("❌ Need 300 coins")

    await users.update_one(
        {"_id": user_id},
        {"$set": {"dead": False}, "$inc": {"balance": -300}}
    )

    await message.reply("❤️ Revived")

# ---------------- KILL ---------------- #
@Client.on_message(filters.command("kill"))
async def kill(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to user")

    if message.reply_to_message.sender_chat:
        return await message.reply("❌ Channel allowed nahi")

    if not message.reply_to_message.from_user:
        return await message.reply("❌ Invalid user")

    killer = await get_user(message.from_user.id)

    if killer.get("dead"):
        return await message.reply("☠️ Tum dead ho")

    target_id = message.reply_to_message.from_user.id
    target = await get_user(target_id)

    if target.get("dead"):
        return await message.reply("☠️ Already dead")

    if target.get("protected") and target.get("protect_time", 0) > time.time():
        return await message.reply("🛡️ Protected")

    if killer.get("balance", 0) < 500:
        return await message.reply("❌ Need 500 coins")

    reward = random.randint(100, 200)

    await users.update_one(
        {"_id": message.from_user.id},
        {"$inc": {"balance": -500 + reward}}
    )

    await users.update_one({"_id": target_id}, {"$set": {"dead": True}})

    await message.reply(f"☠️ Killed!\nReward: {reward}")

# ---------------- ROB ---------------- #
@Client.on_message(filters.command("rob"))
async def rob(client, message):
    user_id = message.from_user.id

    if not message.reply_to_message:
        return await message.reply("❌ Reply to rob")

    if message.reply_to_message.sender_chat:
        return await message.reply("❌ Channel not allowed")

    if not message.reply_to_message.from_user:
        return await message.reply("❌ Invalid user")

    target_id = message.reply_to_message.from_user.id

    if target_id == user_id:
        return await message.reply("❌ Can't rob yourself")

    if len(message.command) < 2:
        return await message.reply("Usage: /rob amount")

    try:
        amount = int(message.command[1])
    except:
        return await message.reply("❌ Invalid amount")

    if amount <= 0:
        return await message.reply("❌ Amount > 0")

    target = await get_user(target_id)

    if target.get("protected") and target.get("protect_time", 0) > time.time():
        return await message.reply("🛡️ Protected")

    if target.get("balance", 0) <= 0:
        return await message.reply("❌ No balance")

    if target.get("balance", 0) < amount:
        return await message.reply("❌ Not enough coins")

    await users.update_one({"_id": user_id}, {"$inc": {"balance": amount}})
    await users.update_one({"_id": target_id}, {"$inc": {"balance": -amount}})

    await message.reply(f"💰 Robbed {amount}")

# ---------------- TOP ---------------- #
@Client.on_message(filters.command("top"))
async def top(client, message):
    text = "🏆 Top Users:\n\n"
    rank = 1

    async for user in users.find().sort("balance", -1).limit(10):
        try:
            u = await client.get_users(user["_id"])
            name = u.first_name
        except:
            name = user["_id"]

        text += f"{rank}. {name} - 💰 {user['balance']}\n"
        rank += 1

    await message.reply(text)
