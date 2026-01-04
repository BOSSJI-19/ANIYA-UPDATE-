import aiohttp

from tools.stream import play_stream, worker
from tools.thumbnails import get_thumb
from tools.database import get_db_queue
from tools.queue import clear_queue
from tools.catbox import download_from_catbox
from config import MUSIC_API_URL, MUSIC_API_KEY


# ─────────────────────────────
# API CALL (ONLY VIDEO ID)
# ─────────────────────────────
async def fetch_from_api(video_id: str):
    url = f"{MUSIC_API_URL}/getvideo"
    params = {
        "query": video_id,   # ✅ ONLY VIDEO ID
        "key": MUSIC_API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


# ─────────────────────────────
# MAIN CONTROLLER
# ─────────────────────────────
async def process_stream(chat_id, user_name, data):
    """
    data comes from music.py
    data = {
        title, duration, vidid, yt_link
    }
    """

    title = data["title"]
    duration = data["duration"]
    vidid = data["vidid"]
    yt_link = data["link"]

    # ─────────────────────
    # 1️⃣ API CALL (VIDEO ID ONLY)
    # ─────────────────────
    api_data = await fetch_from_api(vidid)
    if not api_data or api_data.get("status") != 200:
        return "❌ api failed to provide file.", None

    catbox_link = api_data["link"]

    # ─────────────────────
    # 2️⃣ VC STATUS CHECK
    # ─────────────────────
    try:
        queue = await get_db_queue(chat_id)
        is_streaming = False

        try:
            if chat_id in worker.active_calls:
                is_streaming = True
        except:
            pass

        if queue and not is_streaming:
            await clear_queue(chat_id)

    except Exception as e:
        print("VC CHECK ERROR:", e)

    # ─────────────────────
    # 3️⃣ THUMBNAIL (BOT SIDE)
    # ─────────────────────
    thumbnail = await get_thumb(vidid)

    # ─────────────────────
    # 4️⃣ DOWNLOAD FROM CATBOX
    # ─────────────────────
    try:
        file_path = await download_from_catbox(catbox_link)
    except Exception as e:
        return f"❌ download failed: {e}", None

    # ─────────────────────
    # 5️⃣ PLAY / QUEUE
    # ─────────────────────
    status, position = await play_stream(
        chat_id,
        file_path,
        title,
        duration,
        user_name,
        yt_link,
        thumbnail
    )

    # ─────────────────────
    # 6️⃣ RESPONSE
    # ─────────────────────
    return None, {
        "title": title,
        "duration": duration,
        "thumbnail": thumbnail,
        "user": user_name,
        "link": yt_link,
        "vidid": vidid,
        "status": status,
        "position": position
    }
