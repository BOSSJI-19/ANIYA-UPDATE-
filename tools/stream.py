from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.quality import HighQualityAudio

from config import API_ID, API_HASH, SESSION, LOGGER_ID
from tools.queue import put_queue, pop_queue, clear_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

worker = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)

call_py = PyTgCalls(worker)

async def start_music_worker():
    await worker.start()
    await call_py.start()
    await worker.send_message(LOGGER_ID, "✅ Music Assistant Started 🎵")

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
            InputStream(file_path, HighQualityAudio()),
        )

        add_active_chat(chat_id)
        await put_queue(chat_id, file_path, title, duration, user)
        return True, 0

    except Exception as e:
        print("❌ Play Error:", e)
        return None, None

@call_py.on_stream_end()
async def stream_end(_, update):
    chat_id = update.chat_id
    nxt = await pop_queue(chat_id)

    if nxt:
        await call_py.change_stream(
            chat_id,
            InputStream(nxt["file"], HighQualityAudio()),
        )
    else:
        await call_py.leave_group_call(chat_id)
        remove_active_chat(chat_id)
        await clear_queue(chat_id)

async def stop_stream(chat_id):
    await call_py.leave_group_call(chat_id)
    remove_active_chat(chat_id)
    await clear_queue(chat_id)
