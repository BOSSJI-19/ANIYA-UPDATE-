import asyncio
import aiohttp
import os

from tools.stream import play_stream, worker
from tools.thumbnails import get_thumb
from tools.database import get_db_queue
from tools.queue import clear_queue
from tools.catbox import download_from_catbox
from config import MUSIC_API_URL, MUSIC_API_KEY


async def fetch_from_api(query: str):
    """
    API Call karta hai.
    """
    url = f"{MUSIC_API_URL}/getvideo"
    params = {
        "query": query,
        "key": MUSIC_API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=60) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None


async def process_stream(chat_id, user_name, query):
    # ─────────────────────
    # 1️⃣ API REQUEST
    # ─────────────────────
    data = await fetch_from_api(query)
    
    # Error Handling agar API down ho ya song na mile
    if not data or data.get("status") != 200:
        return "❌ Song not found or API Error.", None

    # 🔥 Data Extraction (API se Title uthaya)
    vidid = data.get("id") # Make sure API returns 'id'
    title = data.get("title", "Unknown Title")
    duration = data.get("duration", "0:00")
    catbox_link = data.get("link")

    if not catbox_link:
        return "❌ Download link missing from API.", None

    # ─────────────────────
    # 2️⃣ VC STATUS CHECK
    # ─────────────────────
    try:
        queue = await get_db_queue(chat_id)
        is_streaming = False
        try:
            if chat_id in worker.active_calls:
                is_streaming = True
        except: pass

        if queue and not is_streaming:
            await clear_queue(chat_id)
    except Exception as e:
        print(f"VC Check Error: {e}")

    # ─────────────────────
    # 3️⃣ THUMBNAIL
    # ─────────────────────
    # Thumbnail ke liye Video ID chahiye
    thumbnail = await get_thumb(vidid) if vidid else None

    # ─────────────────────
    # 4️⃣ DOWNLOAD FROM CATBOX (Local File)
    # ─────────────────────
    try:
        # Link direct play bhi ho sakta hai, par download safer hai
        file_path = await download_from_catbox(catbox_link)
    except Exception as e:
        return f"❌ Download failed: {e}", None

    # ─────────────────────
    # 5️⃣ PLAY / QUEUE
    # ─────────────────────
    status, position = await play_stream(
        chat_id,
        file_path,
        title,
        duration,
        user_name,
        f"https://youtube.com/watch?v={vidid}" if vidid else catbox_link,
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
        "link": f"https://youtube.com/watch?v={vidid}" if vidid else catbox_link,
        "vidid": vidid,
        "status": status,
        "position": position
    }

    return None, response
        
