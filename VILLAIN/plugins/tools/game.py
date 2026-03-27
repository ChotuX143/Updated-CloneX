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

# ---------------- SAFE USER FETCH ---------------- #
async def get_real_user(input_user):
    try:
        user = await app.get_users(input_user)

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
@app.on_message(filters.command(["balance", "bal"]))
async def balance(_, message):

    user_id = None
    name = None

    # 🔁 Reply case
    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            return await message.reply("❌ Channel pe ye command nahi chalega")

        if not message.reply_to_message.from_user:
            return await message.reply("❌ Invalid user")

        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name

    # 🔍 Mention case
    elif len(message.command) > 1:
        user = await get_real_user(message.command[1])
        if not user:
            return await message.reply("❌ Invalid user (channel allowed nahi)")

        user_id = user.id
        name = user.first_name

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
@app.on_message(filters.command("addmoney") & filters.user(OWNER_ID))
async def addmoney(_, message):

    user_id = None
    amount = None

    # 🔁 Reply case
    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            return await message.reply("❌ Channel allowed nahi")

        if not message.reply_to_message.from_user:
            return await message.reply("❌ Invalid user")

        user_id = message.reply_to_message.from_user.id

        try:
            amount = int(message.command[1])
        except:
            return await message.reply("Usage: /addmoney amount (reply user)")

    # 🔍 Username / ID case
    elif len(message.command) >= 3:
        user = await get_real_user(message.command[1])
        if not user:
            return await message.reply("❌ Sirf real user do (channel nahi)")

        user_id = user.id

        try:
            amount = int(message.command[2])
        except:
            return await message.reply("❌ Invalid amount")

    else:
        return await message.reply("❌ गलत usage!")

    # 💰 Add money
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )

    await message.reply(
        f"✅ {amount} coins added to `{user_id}`"
    )

# ---------------- GIVE ---------------- #
@app.on_message(filters.command("give"))
async def give(_, message):
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
PROTECT_TIME = 86400  # 24 hours

@app.on_message(filters.command("protect"))
async def protect(_, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    now = time.time()

    if user.get("protected") and user.get("protect_time", 0) > now:
        remaining = int(user["protect_time"] - now)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        return await message.reply(
            f"🛡️ You are already protected!\n"
            f"⏳ Remaining: {hours}h {minutes}m"
        )

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

    await message.reply("🛡️ Protection Enabled for 24 Hours!")

# ---------------- REVIVE ---------------- #
@app.on_message(filters.command("revive"))
async def revive(_, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user.get("dead"):
        return await message.reply("❌ You are already alive!")

    if user.get("balance", 0) < 300:
        return await message.reply("❌ You need 300 coins to revive!")

    await users.update_one(
        {"_id": user_id},
        {
            "$set": {"dead": False},
            "$inc": {"balance": -300}
        }
    )

    await message.reply("❤️ You are revived!\n💸 300 coins deducted")

# ---------------- KILL ---------------- #
@app.on_message(filters.command("kill"))
async def kill(_, message):
    if not message.reply_to_message:
        return await message.reply("Reply to user")

    if message.reply_to_message.sender_chat:
        return await message.reply("❌ Channel allowed nahi")

    if not message.reply_to_message.from_user:
        return await message.reply("❌ Invalid user")

    killer_id = message.from_user.id
    killer = await get_user(killer_id)

    if killer.get("dead"):
        return await message.reply("☠️ Tum dead ho! Pehle revive karo")

    target_id = message.reply_to_message.from_user.id
    target = await get_user(target_id)

    if target.get("dead"):
        return await message.reply("☠️ Victim is already dead!")

    if target.get("protected") and target.get("protect_time", 0) > time.time():
        return await message.reply("🛡️ User protected hai")

    if killer.get("balance", 0) < 500:
        return await message.reply("❌ Need 500 coins to kill")

    reward = random.randint(100, 200)

    await users.update_one(
        {"_id": killer_id},
        {"$inc": {"balance": -500 + reward}}
    )

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
@app.on_message(filters.command("rob"))
async def rob(_, message):
    user_id = message.from_user.id

    # ❌ Reply required
    if not message.reply_to_message:
        return await message.reply("❌ Reply to user to rob")

    if message.reply_to_message.sender_chat:
        return await message.reply("❌ Channel pe rob nahi kar sakte")

    if not message.reply_to_message.from_user:
        return await message.reply("❌ Invalid user")

    target_id = message.reply_to_message.from_user.id

    # ❌ Self rob block
    if target_id == user_id:
        return await message.reply("❌ Khud ko rob nahi kar sakte")

    # 💰 Amount check
    if len(message.command) < 2:
        return await message.reply("Usage: /rob amount")

    try:
        amount = int(message.command[1])
    except:
        return await message.reply("❌ Invalid amount")

    if amount <= 0:
        return await message.reply("❌ Amount > 0 hona chahiye")

    # 👤 Get users
    user = await get_user(user_id)
    target = await get_user(target_id)

    # 🛡️ Protection check
    if target.get("protected") and target.get("protect_time", 0) > time.time():
        return await message.reply("🛡️ Target protected hai! Rob fail")

    # 💸 Target balance check (IMPORTANT FIX)
    if target.get("balance", 0) <= 0:
        return await message.reply("❌ Target ke paas coins hi nahi hai")

    if target.get("balance", 0) < amount:
        return await message.reply("❌ Target ke paas itne coins nahi")

    # 💸 Transfer
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}}
    )

    await users.update_one(
        {"_id": target_id},
        {"$inc": {"balance": -amount}}
    )

    await message.reply(
        f"💰 Rob Successful!\n🎯 Looted: {amount} coins"
        )
# ---------------- TOP ---------------- #
@app.on_message(filters.command("top"))
async def top(_, message):
    text = "🏆 Top Users:\n\n"
    rank = 1

    async for user in users.find().sort("balance", -1).limit(10):
        try:
            user_obj = await app.get_users(user["_id"])
            name = user_obj.first_name
        except:
            name = user["_id"]

        text += f"{rank}. {name} - 💰 {user['balance']}\n"
        rank += 1

    await message.reply(text)
