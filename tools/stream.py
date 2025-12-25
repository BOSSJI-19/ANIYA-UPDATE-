from pyrogram import Client
from pytgcalls import PyTgCalls

from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.quality import HighQualityAudio

from config import API_ID, API_HASH, SESSION, LOGGER_ID
from tools.queue import put_queue, pop_queue, clear_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

# ─── CLIENT ───
worker = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)

call_py = PyTgCalls(worker)

# ─── START ───
async def start_music_worker():
    await worker.start()
    await call_py.start()

    await worker.send_message(
        LOGGER_ID,
        "✅ Music Assistant Started 🎵\n"
        "• Engine: PyTgCalls 0.9.7\n"
        "• Mode: Audio VC"
    )

# ─── PLAY ───
async def play_stream(chat_id, file_path, title, duration, user):

    if not isinstance(file_path, str):
        print("❌ Invalid path:", file_path)
        return None, None

    if is_active_chat(chat_id):
        pos = await put_queue(chat_id, file_path, title, duration, user)
        return False, pos

    try:
        await call_py.join_group_call(
            int(chat_id),
            InputStream(
                audio=file_path,                 # ✅ path
                audio_quality=HighQualityAudio() # ✅ keyword ONLY
            ),
        )

        add_active_chat(chat_id)
        await put_queue(chat_id, file_path, title, duration, user)
        return True, 0

    except Exception as e:
        print("❌ Play Error:", e)
        return None, None

# ─── AUTO NEXT ───
@call_py.on_stream_end()
async def stream_end_handler(_, update):
    chat_id = update.chat_id
    next_song = await pop_queue(chat_id)

    if next_song:
        file_path = next_song["file"]

        await call_py.change_stream(
            chat_id,
            InputStream(
                audio=file_path,
                audio_quality=HighQualityAudio()
            ),
        )
    else:
        await call_py.leave_group_call(chat_id)
        remove_active_chat(chat_id)
        await clear_queue(chat_id)

# ─── STOP ───
async def stop_stream(chat_id):
    await call_py.leave_group_call(chat_id)
    remove_active_chat(chat_id)
    await clear_queue(chat_id)
