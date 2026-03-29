import random
from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID
from VILLAIN import app

# =========================================
# 𝗥𝗘𝗔𝗟𝗜𝗦𝗧𝗜𝗖 𝗟𝗨𝗗𝗢 𝗚𝗔𝗠𝗘 𝗙𝗢𝗥 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠
# =========================================

ludo_games = {}

MAX_PLAYERS = 4
MIN_PLAYERS = 2
TOKENS_PER_PLAYER = 4
BOARD_END = 57

COLORS = [
    {"name": "Red", "emoji": "🔴"},
    {"name": "Green", "emoji": "🟢"},
    {"name": "Yellow", "emoji": "🟡"},
    {"name": "Blue", "emoji": "🔵"},
]

SAFE_CELLS = {1, 9, 14, 22, 27, 35, 40, 48}

START_POSITIONS = {
    "Red": 1,
    "Green": 14,
    "Yellow": 27,
    "Blue": 40,
}


def is_owner(user_id):
    if isinstance(OWNER_ID, list):
        return user_id in OWNER_ID
    return user_id == OWNER_ID


def get_game(chat_id):
    return ludo_games.get(chat_id)


def get_current_player(game):
    uid = game["turn_order"][game["turn_index"]]
    return game["players"][uid]


def next_turn(game):
    game["turn_index"] = (game["turn_index"] + 1) % len(game["turn_order"])


def token_text(pos):
    if pos == 0:
        return "🏠"
    if pos >= BOARD_END:
        return "✅"
    return f"{pos}"


@app.on_message(filters.command("ludo") & filters.group)
async def create_ludo(_, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if chat_id in ludo_games:
        return await message.reply_text(
            "❌ 𝗔 𝗟𝘂𝗱𝗼 𝗚𝗮𝗺𝗲 𝗶𝘀 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝘂𝗻𝗻𝗶𝗻𝗴!"
        )

    ludo_games[chat_id] = {
        "host_id": user.id,
        "host_name": user.first_name,
        "started": False,
        "turn_index": 0,
        "turn_order": [user.id],
        "players": {
            user.id: {
                "name": user.first_name,
                "color": "Red",
                "emoji": "🔴",
                "tokens": [0, 0, 0, 0],
            }
        },
    }

    await message.reply_text(
        "🎲 𝗥𝗘𝗔𝗟𝗜𝗦𝗧𝗜𝗖 𝗟𝗨𝗗𝗢 𝗚𝗔𝗠𝗘 𝗖𝗥𝗘𝗔𝗧𝗘𝗗!\n\n"
        f"👑 𝗛𝗼𝘀𝘁: {user.first_name}\n"
        "🔴 𝗖𝗼𝗹𝗼𝗿: Red\n\n"
        "📌 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:\n"
        "/joinludo\n/startludo\n/ludostatus"
    )


@app.on_message(filters.command("joinludo") & filters.group)
async def join_ludo(_, message: Message):
    game = get_game(message.chat.id)
    user = message.from_user

    if not game:
        return await message.reply_text("❌ 𝗡𝗼 𝗔𝗰𝘁𝗶𝘃𝗲 𝗚𝗮𝗺𝗲!")

    if user.id in game["players"]:
        return await message.reply_text("⚠️ 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗜𝗻 𝗚𝗮𝗺𝗲!")

    color = COLORS[len(game["turn_order"])]
    game["turn_order"].append(user.id)
    game["players"][user.id] = {
        "name": user.first_name,
        "color": color["name"],
        "emoji": color["emoji"],
        "tokens": [0, 0, 0, 0],
    }

    await message.reply_text(
        f"✅ {user.first_name} 𝗝𝗼𝗶𝗻𝗲𝗱!\n"
        f"{color['emoji']} 𝗖𝗼𝗹𝗼𝗿: {color['name']}"
    )


@app.on_message(filters.command("startludo") & filters.group)
async def start_ludo(_, message: Message):
    game = get_game(message.chat.id)

    if message.from_user.id != game["host_id"]:
        return await message.reply_text("❌ 𝗢𝗻𝗹𝘆 𝗛𝗼𝘀𝘁 𝗖𝗮𝗻 𝗦𝘁𝗮𝗿𝘁!")

    game["started"] = True
    player = get_current_player(game)

    await message.reply_text(
        "🚀 𝗟𝗨𝗗𝗢 𝗦𝗧𝗔𝗥𝗧𝗘𝗗!\n\n"
        f"🎯 𝗙𝗶𝗿𝘀𝘁 𝗧𝘂𝗿𝗻: {player['emoji']} {player['name']}"
    )


@app.on_message(filters.command("roll") & filters.group)
async def roll(_, message: Message):
    game = get_game(message.chat.id)
    user = message.from_user

    player = get_current_player(game)

    if user.id != game["turn_order"][game["turn_index"]]:
        return await message.reply_text(
            f"⏳ 𝗪𝗮𝗶𝘁! 𝗧𝘂𝗿𝗻: {player['name']}"
        )

    dice = random.randint(1, 6)

    await message.reply_text(
        "🎲 𝗗𝗜𝗖𝗘 𝗥𝗢𝗟𝗟\n\n"
        f"👤 {player['name']}\n"
        f"🎯 𝗗𝗶𝗰𝗲: {dice}"
    )

    if dice != 6:
        next_turn(game)

@app.on_message(filters.command("ludostatus") & filters.group)
async def status(_, message: Message):
    game = get_game(message.chat.id)

    text = "🎲 𝗟𝗨𝗗𝗢 𝗦𝗧𝗔𝗧𝗨𝗦\n\n"

    for uid in game["turn_order"]:
        p = game["players"][uid]
        tokens = " | ".join(
            [f"{p['emoji']}{i+1}:{token_text(pos)}" for i, pos in enumerate(p["tokens"])]
        )
        text += f"{p['emoji']} {p['name']}\n{tokens}\n\n"

    await message.reply_text(text)


@app.on_message(filters.command("endludo") & filters.group)
async def end(_, message: Message):
    chat_id = message.chat.id
    game = get_game(chat_id)

    if message.from_user.id != game["host_id"] and not is_owner(message.from_user.id):
        return await message.reply_text("❌ 𝗡𝗼𝘁 𝗔𝗹𝗹𝗼𝘄𝗲𝗱!")

    del ludo_games[chat_id]

    await message.reply_text("🛑 𝗟𝗨𝗗𝗢 𝗘𝗡𝗗𝗘𝗗!")
