import asyncio
import aiohttp

from tools.stream import play_stream, worker
from tools.thumbnails import get_thumb
from tools.database import get_db_queue
from tools.queue import clear_queue
from tools.catbox import download_from_catbox
from tools.youtube import YouTubeAPI
from config import MUSIC_API_URL, MUSIC_API_KEY

YouTube = YouTubeAPI()

# ─────────────────────────────
# API CALL (ONLY VIDEO ID)
# ─────────────────────────────
async def fetch_from_api(video_id: str):
    url = f"{MUSIC_API_URL}/getvideo"
    params = {
        "query": video_id,   # 🔥 ONLY VIDEO ID
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
async def process_stream(chat_id, user_name, query):
    """
    FINAL FLOW (LOCKED):
    User query
      → YouTube search (BOT)
      → video_id, title, duration
      → API(video_id)
      → catbox link
      → download
      → VC play
    """

    # ─────────────────────
    # 1️⃣ YOUTUBE SEARCH (BOT SIDE)
    # ─────────────────────
    try:
        result, vidid = await YouTube.track(query)
        if not result:
            return "❌ song not found.", None

        title = result["title"]
        duration = result["duration_min"]
        yt_link = result["link"]

    except Exception as e:
        return f"❌ search error: {e}", None

    # ─────────────────────
    # 2️⃣ API CALL (VIDEO ID ONLY)
    # ─────────────────────
    try:
        api_data = await fetch_from_api(vidid)
        if not api_data or api_data.get("status") != 200:
            return "❌ api failed to provide file.", None

        catbox_link = api_data["link"]

    except Exception as e:
        return f"❌ api error: {e}", None

    # ─────────────────────
    # 3️⃣ VC STATUS CHECK
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
    # 4️⃣ THUMBNAIL
    # ─────────────────────
    thumbnail = await get_thumb(vidid)

    # ─────────────────────
    # 5️⃣ DOWNLOAD FROM CATBOX
    # ─────────────────────
    try:
        file_path = await download_from_catbox(catbox_link)
    except Exception as e:
        return f"❌ download failed: {e}", None

    # ─────────────────────
    # 6️⃣ PLAY / QUEUE
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
    # 7️⃣ RESPONSE
    # ─────────────────────
    response = {
        "title": title,
        "duration": duration,
        "thumbnail": thumbnail,
        "user": user_name,
        "link": yt_link,
        "vidid": vidid,
        "status": status,
        "position": position
    }

    return None, response
