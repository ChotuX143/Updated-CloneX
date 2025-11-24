import re
from os import getenv
# ------------------------------------
# ------------------------------------
from dotenv import load_dotenv
from pyrogram import filters
# ------------------------------------
# ------------------------------------
load_dotenv()
# ------------------------------------
# -----------------------------------------------------
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
# ------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN")
BOT_ID = getenv("BOT_ID")
# -------------------------------------------------------
OWNER_USERNAME = getenv("OWNER_USERNAME","oyekanhaa")
# --------------------------------------------------------
BOT_USERNAME = getenv("BOT_USERNAME" , "Pikaaclonebot")
# --------------------------------------------------------
BOT_NAME = getenv("BOT_NAME" , "pikachu")
# ---------------------------------------------------------
ASSUSERNAME = getenv("ASSUSERNAME" , "pikaassistant")
# ---------------------------------------------------------


#---------------------------------------------------------------
#---------------------------------------------------------------
MONGO_DB_URI = getenv("MONGO_DB_URI")
API_URL = getenv("API_URL", 'https://api.thequickearn.xyz') #youtube song url
API_KEY = getenv("API_KEY", '') # youtube song api key, generate free key or buy paid plan from panel.thequickearn.xyz

#---------------------------------------------------------------
#---------------------------------------------------------------

# ----------------------------------------------------------------
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
# ----------------------------------------------------------------

# ----------------------------------------------------------------
LOGGER_ID = int(getenv("LOGGER_ID"))
CLONE_LOGGER = LOGGER_ID
# ----------------------------------------------------------------
# ----------------------------------------------------------------
OWNER_ID = int(getenv("OWNER_ID", 7682307978))
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# config.py
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# ----------------------------------------------------------------
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
#SOURCE = getenv("SOURCE", "")
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Oyekanhaa/Kanha-clone.git",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", ''
)
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------



# ------------------------------------------------------------------------
# -------------------------------------------------------------------------
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/aboutkanha")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/kanhasworld")
#-----------------------------------------------------
# -------------------------------------------------------------------------------







# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")
# ----------------------------------------------------------------------------------




# -----------------------------------------------------------------------------------
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))
# --------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------



# ------------------------------------
# ------------------------------------
# ------------------------------------
# ------------------------------------
STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", None)
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# ------------------------------------
# ------------------------------------
# ------------------------------------
# ------------------------------------

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

STREAMI_PICS = [
           "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
        "https://graph.org/file/69ba894371860cd22d92e.jpg",
        "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
        "https://graph.org/file/3a400f1f32fc381913061.jpg",
        "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
        "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
        "https://graph.org/file/25e215c4602b241b66829.jpg",
        "https://graph.org/file/a13e9733afdad69720d67.jpg",
        "https://graph.org/file/692e89f8fe20554e7a139.jpg",
        "https://graph.org/file/db277a7810a3f65d92f22.jpg",
        "https://graph.org/file/a00f89c5aa75735896e0f.jpg",
        "https://graph.org/file/f86b71018196c5cfe7344.jpg",
        "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
        "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
        "https://graph.org/file/84de4b440300297a8ecb3.jpg",
        "https://graph.org/file/84e84ff778b045879d24f.jpg",
        "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
        "https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
        "https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
        "https://graph.org/file/37248e7bdff70c662a702.jpg",
        "https://graph.org/file/0bfe29d15e918917d1305.jpg",
        "https://graph.org/file/16b1a2828cc507f8048bd.jpg",
        "https://graph.org/file/e6b01f23f2871e128dad8.jpg",
        "https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
        "https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
        "https://graph.org/file/39d7277189360d2c85b62.jpg",
        "https://graph.org/file/5846b9214eaf12c3ed100.jpg",
        "https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
        "https://graph.org/file/3514efaabe774e4f181f2.jpg"

]

START_IMG_URL = getenv(
    "START_IMG_URL", "https://files.catbox.moe/9nfozh.jpg"
)

HELP_IMG_URL = getenv(
    "HELP_IMG_URL", "https://files.catbox.moe/fchk2z.jpg"
)

PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://files.catbox.moe/fchk2z.jpg"
)
PLAYLIST_IMG_URL = "https://i.ibb.co/gL3ykkyh/play-music.jpg"
STATS_IMG_URL = "https://i.ibb.co/pBqPtFYn/statistics.jpg"
TELEGRAM_AUDIO_URL = "https://i.ibb.co/gL3ykkyh/play-music.jpg"
TELEGRAM_VIDEO_URL = "https://i.ibb.co/gL3ykkyh/play-music.jpg"
STREAM_IMG_URL = "https://i.ibb.co/0VKCS20y/stream.jpg"
SOUNCLOUD_IMG_URL = "https://i.ibb.co/S4sPf3q8/soundcloud.jpg"
YOUTUBE_IMG_URL = "https://i.ibb.co/xShkBVBK/youtube.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://i.ibb.co/XZfMS8Db/spotify.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://i.ibb.co/XZfMS8Db/spotify.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://i.ibb.co/XZfMS8Db/spotify.jpg"

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )
# ---------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------


GREET = [
    "💞", "🥂", "🔍", "🧪", "🥂", "⚡️", "🔥", "🦋", "🎩", "🌈", "🍷", "🥂", "🦋", "🥃", "🥤", "🕊️",
    "🦋", "🦋", "🕊️", "⚡️", "🕊️", "⚡️", "⚡️", "🥂", "💌", "🥂", "🥂", "🧨"
]

# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
