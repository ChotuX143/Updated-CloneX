import os, re, asyncio
from typing import Union
import yt_dlp
from youtubesearchpython.__future__ import VideosSearch
from VILLAIN.utils.formatters import time_to_seconds
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

# ================================
# FOLDER CREATOR
# ================================
def ensure_download_folder():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    return "downloads"


# ================================
# DIRECT DOWNLOADER (AUDIO + VIDEO)
# ================================
async def direct_dl(link, video=False):
    folder = ensure_download_folder()

    def run():
        try:
            ydl_opts = {
                "format": "bestaudio/best" if not video else "best[height<=720]",
                "outtmpl": f"{folder}/%(id)s.%(ext)s",
                "quiet": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "noprogress": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return os.path.join(folder, f"{info['id']}.{info['ext']}")
        except Exception:
            return None

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, run)


# ================================
# API WRAPPER
# ================================
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="

    # 🔍 Get clickable YouTube link from messages
    async def url(self, msg: Message):
        if msg.entities:
            for ent in msg.entities:
                if ent.type == MessageEntityType.URL:
                    return msg.text[ent.offset : ent.offset + ent.length]
        return None

    # 🔎 Search video metadata
    async def details(self, link: str):
        res = VideosSearch(link, limit=1)
        data = (await res.next())["result"][0]
        title = data["title"]
        duration = data["duration"]
        thumb = data["thumbnails"][0]["url"].split("?")[0]
        vidid = data["id"]
        sec = 0 if not duration else int(time_to_seconds(duration))
        return title, duration, sec, thumb, vidid

    # 🔎 Returns full track detail
    async def track(self, link: str):
        res = VideosSearch(link, limit=1)
        data = (await res.next())["result"][0]
        return {
            "title": data["title"],
            "link": data["link"],
            "vidid": data["id"],
            "duration_min": data["duration"],
            "thumb": data["thumbnails"][0]["url"].split("?")[0],
        }, data["id"]

    # 🎧 Download AUDIO or VIDEO and return path
    async def download(self, link, mystic=None, video=False, videoid=True):
        if videoid:
            link = self.base + link

        filepath = await direct_dl(link, video=video)

        if filepath:
            return filepath, True  # <-- direct file path
        return None, None