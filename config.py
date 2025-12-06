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
OWNER_USERNAME = getenv("OWNER_USERNAME"," ")
# --------------------------------------------------------
BOT_USERNAME = getenv("BOT_USERNAME" , " ")
# --------------------------------------------------------
BOT_NAME = getenv("BOT_NAME" , " ")
# ---------------------------------------------------------
ASSUSERNAME = getenv("ASSUSERNAME" , " ")
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
OWNER_ID = int(getenv("OWNER_ID", ))
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
    "https://github.com/UFCUPDATES/TAMANNACLONE",
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
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/ll_P_U_L_lI")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/l_HEARTBEAT_l")
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
           "https://files.catbox.moe/u8ray8.jpg",
        "https://files.catbox.moe/spenfn.jpg",
        "https://files.catbox.moe/hn384x.jpg",
        "https://files.catbox.moe/0acktl.jpg",
        "https://files.catbox.moe/s1pxqw.jpg",
        "https://files.catbox.moe/2e3tyo.jpg",
        "https://files.catbox.moe/01ecpl.jpg",
        "https://files.catbox.moe/n82tpe.jpg",
        "https://files.catbox.moe/nvkq2r.jpg",
        "https://files.catbox.moe/63o774.jpg",
        "https://files.catbox.moe/h0foag.jpg",
        "https://files.catbox.moe/duwctr.jpg",
        "https://files.catbox.moe/s1hrd3.jpg",
        "https://files.catbox.moe/0n6ej5.jpg",
        "https://files.catbox.moe/3esxuh.jpg",
        "https://files.catbox.moe/i1o537.jpg",
        "https://files.catbox.moe/n02mbg.jpg",
        "https://files.catbox.moe/jofmuy.jpg",
        "https://files.catbox.moe/pysrqh.jpg",
        "https://files.catbox.moe/4as5xk.jpg",
        "https://files.catbox.moe/rtd9zp.jpg",
        "https://files.catbox.moe/m5tzvi.jpg",
        "https://files.catbox.moe/h4ae1t.jpg",
        "https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
        "https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
        "https://graph.org/file/39d7277189360d2c85b62.jpg",
        "https://graph.org/file/5846b9214eaf12c3ed100.jpg",
        "https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
        "https://graph.org/file/3514efaabe774e4f181f2.jpg"

]

START_IMG_URL = getenv(
    "START_IMG_URL", "https://files.catbox.moe/spenfn.jpg"
)

HELP_IMG_URL = getenv(
    "HELP_IMG_URL", "https://files.catbox.moe/u8ray8.jpg"
)

PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://files.catbox.moe/sp9zvc.jpg"
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
