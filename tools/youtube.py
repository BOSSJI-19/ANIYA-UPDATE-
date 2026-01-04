import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

# ─────────────────────────────
# ANDROID BROWSER SPOOF
# ─────────────────────────────
ANDROID_UA = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36"
)

ANDROID_HEADERS = {
    "User-Agent": ANDROID_UA,
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.youtube.com/"
}

# ─────────────────────────────
# HELPERS
# ─────────────────────────────
def time_to_seconds(t):
    if not t:
        return 0
    parts = t.split(":")
    return sum(int(p) * 60 ** i for i, p in enumerate(reversed(parts)))

# ─────────────────────────────
# YOUTUBE API CLASS
# ─────────────────────────────
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(youtube\.com|youtu\.be)"

    # ────────────────
    # CHECK LINK
    # ────────────────
    async def exists(self, link: str, videoid: Union[str, bool] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    # ────────────────
    # GET URL FROM MESSAGE
    # ────────────────
    async def url(self, message: Message) -> Union[str, None]:
        msgs = [message]
        if message.reply_to_message:
            msgs.append(message.reply_to_message)

        for msg in msgs:
            if msg.entities:
                for e in msg.entities:
                    if e.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        return text[e.offset : e.offset + e.length]
            if msg.caption_entities:
                for e in msg.caption_entities:
                    if e.type == MessageEntityType.TEXT_LINK:
                        return e.url
        return None

    # ────────────────
    # DETAILS (TITLE, DURATION, THUMB)
    # ────────────────
    async def details(self, link: str, videoid: Union[str, bool] = None):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]

        search = VideosSearch(link, limit=1)
        r = (await search.next())["result"][0]

        title = r["title"]
        duration = r["duration"]
        thumb = r["thumbnails"][0]["url"].split("?")[0]
        vidid = r["id"]
        duration_sec = time_to_seconds(duration)

        return title, duration, duration_sec, thumb, vidid

    # ────────────────
    # STREAM URL (NO DOWNLOAD)
    # ────────────────
    async def video(self, link: str, videoid: Union[str, bool] = None):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]

        cmd = [
            "yt-dlp",
            "-g",
            "-f", "best[height<=?720][width<=?1280]",
            "--user-agent", ANDROID_UA,
            "--add-header", "Accept-Language:en-US,en;q=0.9",
            "--add-header", "Referer:https://www.youtube.com/",
            "--source-address", "0.0.0.0",
            link
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()

        if out:
            return 1, out.decode().strip().split("\n")[0]
        return 0, err.decode()

    # ────────────────
    # DOWNLOAD AUDIO / VIDEO
    # ────────────────
    async def download(
        self,
        link: str,
        mystic=None,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        link = link.split("&")[0]
        loop = asyncio.get_running_loop()

        def base_opts(fmt):
            return {
                "format": fmt,
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "source_address": "0.0.0.0",
                "http_headers": ANDROID_HEADERS,
            }

        def audio_dl():
            ydl = yt_dlp.YoutubeDL(base_opts("bestaudio/best"))
            info = ydl.extract_info(link, False)
            path = f"downloads/{info['id']}.{info['ext']}"
            if not os.path.exists(path):
                ydl.download([link])
            return path

        def video_dl():
            ydl = yt_dlp.YoutubeDL(
                base_opts("(bestvideo[height<=720][ext=mp4])+(bestaudio[ext=m4a])")
            )
            info = ydl.extract_info(link, False)
            path = f"downloads/{info['id']}.mp4"
            if not os.path.exists(path):
                ydl.download([link])
            return path

        if songaudio:
            return await loop.run_in_executor(None, audio_dl), True

        if songvideo or video:
            return await loop.run_in_executor(None, video_dl), True

        return await loop.run_in_executor(None, audio_dl), True
