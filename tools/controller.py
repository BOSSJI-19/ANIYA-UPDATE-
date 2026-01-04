import asyncio
import aiohttp

from tools.stream import play_stream, worker
from tools.thumbnails import get_thumb
from tools.database import get_db_queue
from tools.queue import clear_queue
from tools.catbox import download_from_catbox
from config import MUSIC_API_URL, MUSIC_API_KEY


async def fetch_from_api(query: str):
    """
    Call your FastAPI (catbox API)
    """
    url = f"{MUSIC_API_URL}/getvideo"
    params = {
        "query": query,
        "key": MUSIC_API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


async def process_stream(chat_id, user_name, query):
    """
    FINAL FLOW:
    Search -> API -> Catbox Download -> Thumbnail -> Stream / Queue
    """

    # ─────────────────────
    # 1️⃣ API REQUEST
    # ─────────────────────
    try:
        data = await fetch_from_api(query)
        if not data or data.get("status") != 200:
            return "❌ song not found.", None

        vidid = data["video_id"]
        catbox_link = data["link"]

    except Exception as e:
        return f"❌ api error: {e}", None

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
            print(f"🧹 queue cleared for {chat_id}")

    except Exception as e:
        print(f"vc check error: {e}")

    # ─────────────────────
    # 3️⃣ TITLE & THUMBNAIL
    # ─────────────────────
    title = vidid  # fallback (safe)
    duration = "unknown"

    thumbnail = await get_thumb(vidid)
    if not thumbnail:
        thumbnail = None

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
        f"https://youtube.com/watch?v={vidid}",
        thumbnail
    )

    # ─────────────────────
    # 6️⃣ RESPONSE
    # ─────────────────────
    response = {
        "title": title,
        "duration": duration,
        "thumbnail": thumbnail,
        "user": user_name,
        "link": f"https://youtube.com/watch?v={vidid}",
        "vidid": vidid,
        "status": status,
        "position": position
    }

    return None, response
