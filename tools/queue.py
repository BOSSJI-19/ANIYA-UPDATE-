import os
from config import DURATION_LIMIT_MIN
from tools.database import get_db_queue, save_db_queue, clear_db_queue

QUEUE_LIMIT = 50

async def put_queue(chat_id, file, title, duration, user, link, thumbnail, stream_type="audio"):
    """
    Song ko queue mein add karta hai (With Thumbnail & Link support).
    """
    
    # 🔒 SAFETY: Check karo file path sahi hai ya nahi
    if not isinstance(file, str):
        print(f"❌ Queue Error: File path text nahi hai! ({type(file)})")
        return {"error": "File Error"}

    queue = await get_db_queue(chat_id)

    if len(queue) >= QUEUE_LIMIT:
        return {"error": "Queue Full"}

    # 🔥 IMPORTANT: Link aur Thumbnail bhi save kar rahe hain ab
    song = {
        "title": title,
        "file": str(file),
        "duration": duration,
        "by": user,
        "link": link,          # ✅ Added for Next Song
        "thumbnail": thumbnail, # ✅ Added for Next Song
        "streamtype": stream_type,
        "played": 0,
    }

    queue.append(song)

    await save_db_queue(chat_id, queue)

    return len(queue) - 1


async def pop_queue(chat_id):
    """
    Current song hataata hai aur next song return karta hai.
    """
    queue = await get_db_queue(chat_id)

    if not queue:
        return None

    # 1. Jo baj raha tha use hatao (First item)
    queue.pop(0)

    # 2. Database update karo
    await save_db_queue(chat_id, queue)

    # 3. Agar queue mein aur gaane bache hain, toh agla return karo
    if queue:
        next_song = queue[0]

        # Safety Check
        if not isinstance(next_song.get("file"), str):
            print("❌ Queue Corrupted: Next song file path missing.")
            return None

        return next_song

    return None

async def get_queue(chat_id):
    return await get_db_queue(chat_id)

async def clear_queue(chat_id):
    """
    Chupchap database se queue saaf kar dega.
    (Koi message nahi bhejega)
    """
    await clear_db_queue(chat_id)
    print(f"🧹 Queue Cleared Silently for {chat_id}")
    
