from pyrogram import filters
from PurviBots import app
from PurviBots.utils.database import mongodb
import random
import time

# 🔗 DB collection
db = mongodb["economy"]
users = db["users"]


# 🧠 Get/Create User
async def get_user(user_id):
    user = await users.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "coins": 100,
            "alive": True,
            "last_kill": 0,
            "last_rob": 0,
            "protect_until": 0
        }
        await users.insert_one(user)
    return user


# 💾 Update user
async def update_user(user_id, data):
    await users.update_one({"_id": user_id}, {"$set": data})


# 🔪 KILL
@app.on_message(filters.command("kill") & filters.group)
async def kill(client, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    now = time.time()

    if now - user["last_kill"] < 300:
        return await message.reply("⏳ Wait 5 min before next kill")

    reward = random.randint(50, 150)

    await update_user(user_id, {
        "coins": user["coins"] + reward,
        "alive": False,
        "last_kill": now
    })

    await message.reply(f"🔪 Killed enemy! +{reward} coins")


# ❤️ REVIVE
@app.on_message(filters.command("revive") & filters.group)
async def revive(client, message):
    user_id = message.from_user.id
    await update_user(user_id, {"alive": True})
    await message.reply("❤️ You are revived")


# 🛡 PROTECT
@app.on_message(filters.command("protect") & filters.group)
async def protect(client, message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("Usage: /protect 1h / 30m / 1d")

    time_str = message.command[1].lower()

    try:
        if "h" in time_str:
            seconds = int(time_str.replace("h", "")) * 3600
        elif "m" in time_str:
            seconds = int(time_str.replace("m", "")) * 60
        elif "d" in time_str:
            seconds = int(time_str.replace("d", "")) * 86400
        else:
            return await message.reply("❌ Invalid format")
    except:
        return await message.reply("❌ Invalid time")

    protect_until = time.time() + seconds

    await update_user(user_id, {"protect_until": protect_until})

    await message.reply(f"🛡 Protected for {time_str}")


# 🔍 CHECK
@app.on_message(filters.command("check") & filters.group)
async def check(client, message):
    user = await get_user(message.from_user.id)

    if user["protect_until"] > time.time():
        remaining = int(user["protect_until"] - time.time())
        await message.reply(f"🛡 Protected for {remaining}s")
    else:
        await message.reply("❌ No protection")


# 💸 ROB
@app.on_message(filters.command("rob") & filters.group)
async def rob(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to user to rob")

    attacker_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id

    if attacker_id == target_id:
        return await message.reply("❌ Can't rob yourself")

    attacker = await get_user(attacker_id)
    target = await get_user(target_id)

    now = time.time()

    if now - attacker["last_rob"] < 300:
        return await message.reply("⏳ Wait 5 min before rob again")

    if target["protect_until"] > now:
        return await message.reply("🛡 Target protected")

    if target["coins"] <= 0:
        return await message.reply("💀 Target has no coins")

    amount = random.randint(20, 100)
    amount = min(amount, target["coins"])

    success = random.choice([True, False])

    if success:
        await update_user(attacker_id, {
            "coins": attacker["coins"] + amount,
            "last_rob": now
        })
        await update_user(target_id, {
            "coins": target["coins"] - amount
        })

        await message.reply(f"💸 Success! Stole {amount} coins")
    else:
        loss = random.randint(10, 50)

        await update_user(attacker_id, {
            "coins": max(0, attacker["coins"] - loss),
            "last_rob": now
        })

        await message.reply(f"❌ Failed! Lost {loss} coins")
