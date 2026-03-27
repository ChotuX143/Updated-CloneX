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
from pyrogram import filters

@app.on_message(filters.command(["balance", "bal"]))
async def balance(_, message):

    user_id = None
    name = None

    # 🔁 Reply case
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name

    # 🔍 Mention case
    elif len(message.command) > 1:
        try:
            user = await app.get_users(message.command[1])
            user_id = user.id
            name = user.first_name
        except:
            return await message.reply("❌ User not found")

    # 👤 Self case
    else:
        user_id = message.from_user.id
        name = message.from_user.first_name

    # 📊 Get user data
    user = await get_user(user_id)

    # 📤 Reply
    await message.reply_text(
        f"💰 **Balance of {name}:**\n\n"
        f"💸 Coins: `{user['balance']}`\n"
        f"⭐ Level: `{user['level']}`\n"
        f"🔥 XP: `{user['xp']}`"
    )

# ---------------- ADD MONEY ---------------- #
from pyrogram import filters

@app.on_message(filters.command("addmoney") & filters.user(OWNER_ID))
async def addmoney(_, message):

    user_id = None
    amount = None

    # 🔁 Reply case
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

        try:
            amount = int(message.command[1])
        except:
            return await message.reply("Usage: /addmoney amount (reply user)")

    # 🔍 Username / ID case
    elif len(message.command) >= 3:
        try:
            user = await app.get_users(message.command[1])
            user_id = user.id
            amount = int(message.command[2])
        except:
            return await message.reply("Usage: /addmoney user_id/@username amount")

    else:
        return await message.reply("❌ गलत usage!")

    # 💰 Add money
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True  # 👈 agar user DB me nahi hai to create ho jayega
    )

    await message.reply(
        f"✅ {amount} coins added to `{user_id}`"
    )

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
import time
from pyrogram import filters

PROTECT_TIME = 86400  # 24 hours in seconds

@app.on_message(filters.command("protect"))
async def protect(_, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    now = time.time()

    # ✅ Check if already protected and not expired
    if user.get("protected") and user.get("protect_time", 0) > now:
        remaining = int(user["protect_time"] - now)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        return await message.reply(
            f"🛡️ You are already protected!\n"
            f"⏳ Remaining: {hours}h {minutes}m"
        )

    # 🛡️ Set protection
    expire_time = now + PROTECT_TIME

    await users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "protected": True,
                "protect_time": expire_time
            }
        }
    )

    await message.reply(
        "🛡️ Protection Enabled for 24 Hours!"
    )
    
# ---------------- REVIVE ---------------- #
@app.on_message(filters.command("revive"))
async def revive(_, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    # ❌ Already alive
    if not user.get("dead"):
        return await message.reply("❌ You are already alive!")

    # 💰 Check balance
    if user.get("balance", 0) < 300:
        return await message.reply("❌ You need 300 coins to revive!")

    # ❤️ Revive + Deduct coins
    await users.update_one(
        {"_id": user_id},
        {
            "$set": {"dead": False},
            "$inc": {"balance": -300}
        }
    )

    await message.reply("❤️ You are revived!\n💸 300 coins deducted")
    
# ---------------- KILL ---------------- #
import random
from pyrogram import filters

@app.on_message(filters.command("kill"))
async def kill(_, message):
    if not message.reply_to_message:
        return await message.reply("Reply to user")

    killer_id = message.from_user.id
    killer = await get_user(killer_id)

    # ☠️ Killer dead check
    if killer.get("dead"):
        return await message.reply("☠️ Tum dead ho! Pehle revive karo")

    target_id = message.reply_to_message.from_user.id
    target = await get_user(target_id)

    # ☠️ Already dead check
    if target.get("dead"):
        return await message.reply("☠️ Victim is already dead!")

    # 🛡️ Protection check (time-based bhi handle kare)
    if target.get("protected") and target.get("protect_time", 0) > time.time():
        return await message.reply("🛡️ User protected hai")

    # 💰 Kill cost check
    if killer.get("balance", 0) < 500:
        return await message.reply("❌ Need 500 coins to kill")

    # 🎁 Random reward
    reward = random.randint(100, 200)

    # 💸 Deduct cost + add reward
    await users.update_one(
        {"_id": killer_id},
        {
            "$inc": {"balance": -500 + reward}
        }
    )

    # ☠️ Kill victim
    await users.update_one(
        {"_id": target_id},
        {"$set": {"dead": True}}
    )

    await message.reply(
        f"☠️ User killed successfully!\n\n"
        f"💸 Cost: 500\n"
        f"🎁 Reward: {reward}\n"
        f"💰 Net: {reward - 500}"
        )

# ---------------- ROB ---------------- #
import time
from pyrogram import filters

@app.on_message(filters.command("rob"))
async def rob(_, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("Usage: /rob amount")

    try:
        amount = int(message.command[1])
    except:
        return await message.reply("❌ Invalid amount")

    if amount <= 0:
        return await message.reply("❌ Amount > 0 hona chahiye")

    # 👤 Robber (dead/alive both allowed)
    user = await get_user(user_id)

    # 🎯 Random target
    target = await users.aggregate([
        {"$match": {"_id": {"$ne": user_id}}},
        {"$sample": {"size": 1}}
    ]).to_list(1)

    if not target:
        return await message.reply("❌ Koi target nahi mila")

    target = target[0]

    # 🛡️ Protected check
    if target.get("protected") and target.get("protect_time", 0) > time.time():
        return await message.reply("🛡️ Target protected hai! Rob fail")

    # 💰 Balance check
    if target.get("balance", 0) < amount:
        return await message.reply("❌ Target ke paas itne coins nahi")

    # 💸 EXACT TRANSFER
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}}   # 👈 jitna rob = utna add
    )

    await users.update_one(
        {"_id": target["_id"]},
        {"$inc": {"balance": -amount}}  # 👈 utna hi deduct
    )

    await message.reply(
        f"💰 Rob Successful!\n"
        f"🎯 Looted: {amount} coins"
    )

# ---------------- TOP ---------------- #
@app.on_message(filters.command("top"))
async def top(_, message):
    text = "🏆 Top Users:\n\n"
    rank = 1

    async for user in users.find().sort("balance", -1).limit(10):
        text += f"{rank}. {user['_id']} - 💰 {user['balance']}\n"
        rank += 1

    await message.reply(text)
