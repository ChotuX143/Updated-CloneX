import random
import time
from pyrogram import filters
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, OWNER_ID
from VILLAIN import app   

# ---------------- DB ---------------- #
mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["rpg_bot"]
users = db["users"]

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
@app.on_message(filters.command("balance"))
async def balance(_, message):
    user = await get_user(message.from_user.id)

    await message.reply_text(
        f"💰 Balance: {user['balance']}\n"
        f"⭐ Level: {user['level']}\n"
        f"🔥 XP: {user['xp']}"
    )

# ---------------- ADD MONEY ---------------- #
@app.on_message(filters.command("addmoney") & filters.user(OWNER_ID))
async def addmoney(_, message):
    try:
        user_id = int(message.command[1])
        amount = int(message.command[2])
    except:
        return await message.reply("Usage: /addmoney user_id amount")

    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}}
    )

    await message.reply("✅ Money Added")

# ---------------- GIVE ---------------- #
@app.on_message(filters.command("give"))
async def give(_, message):
    if not message.reply_to_message:
        return await message.reply("Reply to user")

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
@app.on_message(filters.command("protect"))
async def protect(_, message):
    await users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"protected": True}}
    )

    await message.reply("🛡️ Protection Enabled")

# ---------------- REVIVE ---------------- #
@app.on_message(filters.command("revive"))
async def revive(_, message):
    user = await get_user(message.from_user.id)

    if not user["dead"]:
        return await message.reply("❌ Already alive")

    await users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"dead": False}}
    )

    await message.reply("❤️ Revived!")

# ---------------- KILL ---------------- #
@app.on_message(filters.command("kill"))
async def kill(_, message):
    if not message.reply_to_message:
        return await message.reply("Reply to user")

    killer = await get_user(message.from_user.id)

    if killer["dead"]:
        return await message.reply("☠️ Tum dead ho")

    target_id = message.reply_to_message.from_user.id
    target = await get_user(target_id)

    if target["dead"]:
        return await message.reply("☠️ Already dead")

    if target["protected"]:
        return await message.reply("🛡️ Protected user")

    now = time.time()
    if now - killer["last_kill"] < 60:
        return await message.reply("⏳ Cooldown")

    if killer["balance"] < 500:
        return await message.reply("❌ Need 500 coins")

    await users.update_one({"_id": killer["_id"]}, {
        "$inc": {"balance": -500},
        "$set": {"last_kill": now}
    })

    await users.update_one({"_id": target_id}, {
        "$set": {"dead": True}
    })

    await message.reply("☠️ User killed!")

# ---------------- ROB ---------------- #
@app.on_message(filters.command("rob"))
async def rob(_, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("Usage: /rob amount")

    try:
        amount = int(message.command[1])
    except:
        return await message.reply("Invalid amount")

    if amount <= 0:
        return await message.reply("Amount > 0")

    user = await get_user(user_id)

    if user["dead"]:
        return await message.reply("☠️ Tum dead ho")

    now = time.time()
    if now - user["last_rob"] < 60:
        return await message.reply("⏳ Cooldown")

    target = await users.aggregate([
        {"$match": {"_id": {"$ne": user_id}}},
        {"$sample": {"size": 1}}
    ]).to_list(1)

    if not target:
        return await message.reply("No target")

    target = target[0]

    if target["dead"]:
        return await message.reply("☠️ Target dead")

    if target["protected"]:
        return await message.reply("🛡️ Target protected")

    if target["balance"] < amount:
        return await message.reply("❌ Target poor")

    success = random.randint(1, 100) <= 60

    if success:
        await users.update_one({"_id": user_id}, {
            "$inc": {"balance": amount},
            "$set": {"last_rob": now}
        })

        await users.update_one({"_id": target["_id"]}, {
            "$inc": {"balance": -amount}
        })

        await message.reply(f"💰 Rob success! Looted {amount}")

    else:
        penalty = int(amount * 0.3)

        await users.update_one({"_id": user_id}, {
            "$inc": {"balance": -penalty},
            "$set": {"last_rob": now}
        })

        await message.reply(f"🚔 Failed! Lost {penalty}")

# ---------------- TOP ---------------- #
@app.on_message(filters.command("top"))
async def top(_, message):
    text = "🏆 Top Users:\n\n"
    rank = 1

    async for user in users.find().sort("balance", -1).limit(10):
        text += f"{rank}. {user['_id']} - 💰 {user['balance']}\n"
        rank += 1

    await message.reply(text)
