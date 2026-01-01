import os
from tools.database import get_db_queue, save_db_queue, clear_db_queue

# Limit taaki database heavy na ho
QUEUE_LIMIT = 50

async def put_queue(chat_id, file, title, duration, user, link, thumbnail, stream_type="audio"):
    """
    Song ko database queue mein add karta hai.
    Bilkul PrinceMusic logic par based: Simple Append.
    """
    
    # 1. Database se list nikalo
    queue = await get_db_queue(chat_id)
    
    # ⚠️ SAFETY: Agar queue None hai (First Song), toh empty list banao
    if not queue:
        queue = []

    # 2. Limit Check
    if len(queue) >= QUEUE_LIMIT:
        return {"error": "Queue Full"}

    # 3. Song Data Structure (PrinceMusic style clean data)
    song = {
        "title": title,
        "file": str(file),
        "duration": duration,
        "by": user,
        "link": link,
        "thumbnail": thumbnail,
        "streamtype": stream_type,
        "played": 0,
    }

    # 4. List mein last mein add karo
    queue.append(song)

    # 5. Database mein save karo
    await save_db_queue(chat_id, queue)
    
    # Position return karo (0 means playing, >0 means in queue)
    return len(queue) - 1

async def pop_queue(chat_id):
    """
    Current song (Index 0) ko delete karta hai.
    """
    queue = await get_db_queue(chat_id)

    if not queue:
        return None

    # Pehla gaana (jo baj chuka hai) remove karo
    removed_song = queue.pop(0)

    # Wapis save karo
    await save_db_queue(chat_id, queue)
    
    return removed_song

async def get_queue(chat_id):
    """
    Poori list return karta hai.
    """
    queue = await get_db_queue(chat_id)
    if not queue:
        return []
    return queue

async def clear_queue(chat_id):
    """
    Queue saaf kar deta hai.
    """
    await clear_db_queue(chat_id)
    print(f"🧹 Queue Cleared for {chat_id}")

async def get_current_song(chat_id):
    """
    Jo gaana abhi baj raha hai (Index 0) wo nikalta hai.
    """
    queue = await get_db_queue(chat_id)
    if queue and len(queue) > 0:
        return queue[0]
    return None
            
