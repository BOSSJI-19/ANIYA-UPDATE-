import asyncio
from tools.youtube import YouTubeAPI
from tools.stream import play_stream, worker 
from tools.thumbnails import get_thumb
from tools.database import get_db_queue
from tools.queue import clear_queue 

# 🔥 IMPORTANT IMPORT: Ye bot ko freeze hone se bachaega
from tools.utils import run_sync 

# Initialize YouTube
YouTube = YouTubeAPI()

async def process_stream(chat_id, user_name, query):
    """
    Complete Flow: Search -> VC Check -> Download -> Thumbnail -> Stream/Queue
    Updated with NON-BLOCKING Logic 🚀
    """
    
    # --- 1. SEARCHING (Non-Blocking) ---
    try:
        if "youtube.com" in query or "youtu.be" in query:
             # Agar Link hai (Background me info nikalo)
             title = await run_sync(YouTube.title, query)
             duration = await run_sync(YouTube.duration, query)
             thumbnail = await run_sync(YouTube.thumbnail, query)
             
             if "v=" in query:
                 vidid = query.split("v=")[-1].split("&")[0]
             else:
                 vidid = query.split("/")[-1]
             link = query
        else:
            # Agar Name hai (Background Search)
            # 'run_sync' use kiya taaki bot search karte time atke nahi
            result, vidid = await run_sync(YouTube.track, query)
            
            if not result:
                return "❌ Song not found.", None
            title = result["title"]
            duration = result["duration_min"]
            thumbnail = result["thumb"]
            link = result["link"]
            
    except Exception as e:
        return f"❌ Search Error: {e}", None

    # --- VC STATUS CHECK (Existing Logic) ---
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
            print(f"🧹 Queue Cleared for {chat_id} (VC was Closed)")
            
    except Exception as e:
        print(f"VC Check Error: {e}")

    # --- 2. THUMBNAIL GENERATION (Non-Blocking) ---
    # Image processing heavy hoti hai, isliye background me dala
    final_thumb = await run_sync(get_thumb, vidid)
    if not final_thumb:
        final_thumb = thumbnail 

    # --- 3. DOWNLOADING (Non-Blocking) ---
    try:
        # Sabse heavy kaam (Download) ab background me hoga 🚀
        file_path, direct = await run_sync(
            YouTube.download,
            link, 
            mystic=None,
            title=title,
            format_id="bestaudio"
        )
    except Exception as e:
        return f"❌ Download Error: {e}", None

    # --- 4. PLAYING / QUEUING ---
    # Play Stream already async hai, isko wrap karne ki need nahi
    status, position = await play_stream(
        chat_id, 
        file_path, 
        title, 
        duration, 
        user_name, 
        link,        
        final_thumb  
    )

    # --- 5. RESULT ---
    response = {
        "title": title,
        "duration": duration,
        "thumbnail": final_thumb, 
        "user": user_name,
        "link": link,
        "vidid": vidid,
        "status": status,    # True (Playing) / False (Queued)
        "position": position # Queue Number
    }
    
    return None, response
    
