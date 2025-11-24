import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram import filters, Client
from VILLAIN import app
from VILLAIN.misc import SUDOERS
from VILLAIN.utils.decorators.language import language

from VILLAIN.utils.database.clonedb import get_owner_id_from_db, get_cloned_support_chat, get_cloned_support_channel
from config import SUPPORT_CHAT, OWNER_ID

from VILLAIN.utils.database import clonebotdb


@Client.on_message(filters.command("setchannel"))
@language
async def set_channel(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

    if len(message.command) != 2:
        await message.reply_text(_["C_P_I_2"])
        return
    
    channel = message.command[1]
    if channel.startswith("@"):
        channel = channel[1:] 

    result = clonebotdb.update_one({"bot_id": bot_id}, {"$set": {"channel": channel}})
    if result.modified_count > 0:
        await message.reply_text(_["C_P_I_4"].format(channel))
    else:
        await message.reply_text(_["C_P_I_6"])


@Client.on_message(filters.command("setsupport"))
@language
async def set_support(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

    if len(message.command) != 2:
        await message.reply_text(_["C_P_I_1"])
        return

    support = message.command[1]
    if support.startswith("@"):
        support = support[1:] 

    result = clonebotdb.update_one({"bot_id": bot_id}, {"$set": {"support": support}})
    if result.modified_count > 0:
        await message.reply_text(_["C_P_I_3"].format(support))
    else:
        await message.reply_text(_["C_P_I_5"])


@Client.on_message(filters.command("botinfo"))
@language
async def bot_info(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

    channel = await get_cloned_support_channel(bot_id)
    support = await get_cloned_support_chat(bot_id)
    
    await message.reply_text(
        f"**Bᴏᴛ Iɴғᴏ:**\n"
        f"➤ **Bᴏᴛ ID:** `{bot_id}`\n"
        f"➤ **Cʜᴀɴɴᴇʟ:** @{channel}\n"
        f"➤ **Sᴜᴘᴘᴏʀᴛ Cʜᴀᴛ:** @{support}"
    )


def get_logging_status(bot_id):
    bot_data = clonebotdb.find_one({"bot_id": bot_id})
    return bot_data.get("logging", True)

def get_log_channel(bot_id):
    bot_data = clonebotdb.find_one({"bot_id": bot_id})
    return bot_data.get("logchannel", "-100")


@Client.on_message(filters.command("logstatus"))
@language
async def check_log_status(client, message, _):
    bot_id = client.me.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

    logging_status = get_logging_status(bot_id)
    log_channel = get_log_channel(bot_id)

    if logging_status:
        C_LOGGER_STATUS = "Enabled"
    else:
        C_LOGGER_STATUS = "False"

    if str(log_channel) == "-100":
        C_LOGGER_VALUE = "Not Set"
    else:
        C_LOGGER_VALUE = log_channel

    text = f"**Lᴏɢɢɢᴇʀ Sᴛᴀᴛᴜs:**\n\n"
    text += f" - Sᴛᴀᴛᴜs: `{C_LOGGER_STATUS}`\n"
    text += f" - Lᴏɢɢᴇʀ ID: `{C_LOGGER_VALUE}`"

    await message.reply_text(text)


@Client.on_message(filters.command("logger"))
@language
async def toggle_logging(client: Client, message: Message, _):
    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

    if len(message.command) != 2:
        return await message.reply_text("**ᴇxᴀᴍᴘʟᴇ :** \n/logger [ᴇɴᴀʙʟᴇ | ᴅɪsᴀʙʟᴇ]")

    option = message.command[1].lower()
    if option not in ["enable", "disable"]:
        return await message.reply_text("**ᴇxᴀᴍᴘʟᴇ :** \n/logger [ᴇɴᴀʙʟᴇ | ᴅɪsᴀʙʟᴇ]")

    logging_status = option == "enable"

    result = clonebotdb.update_one(
        {"bot_id": bot_id}, 
        {"$set": {"logging": logging_status}}, 
        upsert=True
    )

    if result.modified_count > 0 or result.upserted_id:
        await message.reply_text(f"{'ᴇɴᴀʙʟᴇᴅ ʟᴏɢɢɪɴɢ.' if logging_status else 'ᴅɪsᴀʙʟᴇᴅ ʟᴏɢɢɪɴɢ.'}")
    else:
        await message.reply_text("Fᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ʟᴏɢɢɪɴɢ sᴛᴀᴛᴜs!")


@Client.on_message(filters.command("setlogger"))
@language
async def set_log_channel(client: Client, message: Message, _):
    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

    if len(message.command) != 2:
        return await message.reply_text("**ᴇxᴀᴍᴘʟᴇ :** \n- `/setlogger -100xxxxxxxx`")

    try:
        group_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Iɴᴠᴀʟɪᴅ Lᴏɢɢᴇʀ ID! Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɴᴜᴍᴇʀɪᴄ ᴠᴀʟᴜᴇ.")

    if not str(group_id).startswith("-100"):
        return await message.reply_text("Iɴᴠᴀʟɪᴅ Lᴏɢɢᴇʀ ID! ᴏʀ Mᴀᴋᴇ sᴜʀᴇ ʙᴏᴛ ɪs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀɴᴅ ʜᴀs ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs.")

    try:
        test_msg = await client.send_message(group_id, "Bᴏᴛ ʟᴏɢɢɪɴɢ ᴇɴᴀʙʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
        
        result = clonebotdb.update_one(
            {"bot_id": bot_id}, 
            {"$set": {"logchannel": group_id}}, 
            upsert=True
        )

        if result.modified_count > 0 or result.upserted_id:
            return await message.reply_text(f"Lᴏɢɢɪɴɢ ᴇɴᴀʙʟᴇᴅ ғᴏʀ `{group_id}`.")
        else:
            return await message.reply_text("Fᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ ʟᴏɢ ɢʀᴏᴜᴘ!")

    except Exception as e:
        return await message.reply_text(f"Bᴏᴛ ᴄᴀɴ'ᴛ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!")
