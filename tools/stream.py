import asyncio
import os
import html 
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped, Update, HighQualityAudio 
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from pyrogram import Client

# Configs
from config import API_ID, API_HASH, SESSION, BOT_TOKEN, OWNER_NAME, INSTAGRAM_LINK
from tools.queue import put_queue, pop_queue, clear_queue, get_queue
from tools.database import add_active_chat, remove_active_chat

# --- GLOBAL DICTIONARIES ---
LAST_MSG_ID = {}   
QUEUE_MSG_ID = {}

# --- ⚠️ SAFE CLIENT SETUP ---
print("🟡 [STREAM] Loading Music Module...")

worker_app = None
worker = None

try:
    if SESSION:
        worker_app = Client(
            "MusicWorker",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION,
            in_memory=True,
        )
        worker = PyTgCalls(worker_app)
        print("✅ [STREAM] Music Client Loaded Successfully!")
    else:
        print("⚠️ [STREAM] Session String Missing! Music will not work.")
except Exception as e:
    print(f"❌ [STREAM ERROR] Client Load Failed: {e}")

main_bot = Bot(token=BOT_TOKEN)

# --- HELPER: PROGRESS BAR ---
def get_progress_bar(duration):
    return "◉————————————"

# --- 🔥 HELPER: SAFE UI SENDER ---
async def send_now_playing(chat_id, song_data):
    try:
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass
        
        title = html.escape(str(song_data["title"]))
        user = html.escape(str(song_data["by"]))
        duration = str(song_data["duration"])
        link = song_data["link"]
        thumbnail = song_data["thumbnail"]

        if len(title) > 30: display_title = title[:30] + "..."
        else: display_title = title
        
        bar_display = get_progress_bar(duration)

        buttons = [
            [InlineKeyboardButton(f"⏳ {duration}", callback_data="GetTimer")],
            [
                InlineKeyboardButton("II", callback_data="music_pause"),
                InlineKeyboardButton("▶", callback_data="music_resume"),
                InlineKeyboardButton("‣‣I", callback_data="music_skip"),
                InlineKeyboardButton("▢", callback_data="music_stop")
            ],
            [
                InlineKeyboardButton("📺 ʏᴏᴜᴛᴜʙᴇ", url=link),
                InlineKeyboardButton("📸 ɪɴsᴛᴀɢʀᴀᴍ", url=INSTAGRAM_LINK)
            ],
            [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")]
        ]
        
        caption = f"""
<b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ</b>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{display_title}</a>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {user}</blockquote>

{bar_display}

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
        msg = await main_bot.send_photo(
            chat_id,
            photo=thumbnail,
            caption=caption,
            has_spoiler=True, 
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )
        LAST_MSG_ID[chat_id] = msg.message_id
        return True
    except Exception as e:
        print(f"⚠️ [UI ERROR] Message nahi gaya: {e}")
        return False

# --- 🔥 STARTUP LOGIC ---
async def start_music_worker():
    print("🔵 Starting Music Assistant...")
    if not worker: return
    try:
        if not worker_app.is_connected:
            await worker_app.start()
        try: await worker.start()
        except: pass
        print("✅ Assistant Started!")
    except Exception as e:
        print(f"❌ Assistant Error: {e}")

# --- 1. PLAY LOGIC (NO-CUTTING FIX) ---
async def play_stream(chat_id, file_path, title, duration, user, link, thumbnail):
    if not worker: return None, "Music System Error"
    
    safe_title = title
    safe_user = user
    stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())

    try:
        # ✅ STEP 1: Pehle Database mein Queue update karo
        # Ye zaroori hai taaki list maintain rahe
        position = await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
        
        # ✅ STEP 2: CHECK - KYA BOT ABHI VC MEIN HAI?
        is_active = False
        try:
            for call in worker.active_calls:
                if call.chat_id == chat_id:
                    is_active = True
                    break
        except: pass

        # === LOGIC TREE ===

        # CASE A: Bot Active Hai + UI Message Maujood Hai (Matlab Gaana Baj Raha Hai)
        if is_active and chat_id in LAST_MSG_ID:
            # Current gaana chalne do. Naye wale ko QUEUE mein rakho.
            # Position return karo taaki user ko "Added to Queue" dikhe.
            return False, position

        # CASE B: Bot Active Hai PAR Koi Message Nahi Hai (Idle Mode)
        elif is_active and chat_id not in LAST_MSG_ID:
            print(f"⚡ [IDLE PLAY] Bot is active but idle. Playing {safe_title}")
            try:
                await worker.change_stream(int(chat_id), stream)
                
                # UI Update
                song_data = {"title": safe_title, "duration": duration, "by": safe_user, "link": link, "thumbnail": thumbnail}
                await send_now_playing(chat_id, song_data)
                return True, 0
            except:
                # Agar change fail ho jaye to Rejoin
                try: await worker.leave_group_call(int(chat_id))
                except: pass
                await asyncio.sleep(0.5)
                await worker.join_group_call(int(chat_id), stream)
                
                song_data = {"title": safe_title, "duration": duration, "by": safe_user, "link": link, "thumbnail": thumbnail}
                await send_now_playing(chat_id, song_data)
                return True, 0

        # CASE C: Bot Active Hi Nahi Hai (First Song)
        else:
            # Join and Play
            try: await worker.leave_group_call(int(chat_id))
            except: pass
            
            await asyncio.sleep(0.5)
            await worker.join_group_call(int(chat_id), stream)
            await add_active_chat(chat_id)
            
            # UI Update
            song_data = {"title": safe_title, "duration": duration, "by": safe_user, "link": link, "thumbnail": thumbnail}
            await send_now_playing(chat_id, song_data)
            
            return True, 0

    except Exception as e:
        return None, str(e)

# --- 2. STREAM END HANDLER ---
if worker:
    @worker.on_stream_end()
    async def stream_end_handler(client, update: Update):
        chat_id = update.chat_id
        print(f"🔄 Stream Ended in {chat_id}")
        
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass 
            del LAST_MSG_ID[chat_id]
        
        await asyncio.sleep(1)
        
        # 1. Purana hatao
        await pop_queue(chat_id)
        
        # 2. Next Check
        queue = await get_queue(chat_id)
        
        if queue and len(queue) > 0:
            next_song = queue[0]
            print(f"🎵 Playing Next: {next_song['title']}")
            try:
                stream = AudioPiped(next_song["file"], audio_parameters=HighQualityAudio())
                try:
                    await worker.change_stream(chat_id, stream)
                except:
                    # Rejoin Fallback
                    try: await worker.leave_group_call(chat_id)
                    except: pass
                    await asyncio.sleep(0.5)
                    await worker.join_group_call(chat_id, stream)
                
                await send_now_playing(chat_id, next_song)
            except Exception as e:
                print(f"❌ Auto-Play Error: {e}")
                await stop_stream(chat_id)
        else:
            print(f"✅ Queue Empty for {chat_id}, Leaving VC.")
            await stop_stream(chat_id)

# --- 3. CONTROLS ---
async def skip_stream(chat_id):
    if not worker: return False
    
    if chat_id in LAST_MSG_ID:
        try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except: pass
        if chat_id in LAST_MSG_ID: del LAST_MSG_ID[chat_id]

    await pop_queue(chat_id)
    
    queue = await get_queue(chat_id)
    if queue and len(queue) > 0:
        next_song = queue[0]
        try:
            stream = AudioPiped(next_song["file"], audio_parameters=HighQualityAudio())
            await worker.change_stream(chat_id, stream)
            await send_now_playing(chat_id, next_song)
            return True 
        except Exception as e:
            await stop_stream(chat_id)
            return False
    else:
        await stop_stream(chat_id)
        return False

async def stop_stream(chat_id):
    if not worker: return False
    try:
        await worker.leave_group_call(int(chat_id))
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass
            del LAST_MSG_ID[chat_id]
        return True
    except: return False

async def pause_stream(chat_id):
    if not worker: return False
    try: await worker.pause_stream(chat_id); return True
    except: return False

async def resume_stream(chat_id):
    if not worker: return False
    try: await worker.resume_stream(chat_id); return True
    except: return False

async def get_current_playing(chat_id):
    queue = await get_queue(chat_id)
    if queue and len(queue) > 0: return queue[0]
    return None
    
