
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.exceptions import NoActiveGroupCall

from config import API_ID, API_HASH, SESSION
from tools.queue import put_queue, pop_queue, clear_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat


# --- CLIENT SETUP ---
worker = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)

call_py = PyTgCalls(worker)


async def start_music_worker():
    print("🔵 Starting Music Assistant...")
    await worker.start()
    await call_py.start()
    print("✅ Assistant & PyTgCalls Started!")


# --- PLAY LOGIC ---
async def play_stream(chat_id, file_path, title, duration, user):
    if await is_active_chat(chat_id):
        pos = await put_queue(chat_id, file_path, title, duration, user)
        return False, pos

    stream = AudioPiped(
        file_path,
        audio_parameters=HighQualityAudio(),
    )

    await call_py.join_group_call(chat_id, stream)
    await add_active_chat(chat_id)
    await put_queue(chat_id, file_path, title, duration, user)

    return True, 0


# --- STREAM END HANDLER ---
@call_py.on_stream_end()
async def stream_end_handler(client, update: Update):
    if not isinstance(update, StreamAudioEnded):
        return

    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    next_song = await pop_queue(chat_id)

    if next_song:
        stream = AudioPiped(
            next_song["file"],
            audio_parameters=HighQualityAudio(),
        )
        await call_py.change_stream(chat_id, stream)
    else:
        print("🛑 Queue empty, leaving VC")
        try:
            await call_py.leave_group_call(chat_id)
        except NoActiveGroupCall:
            pass
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)


# --- STOP COMMAND ---
async def stop_stream(chat_id):
    try:
        await call_py.leave_group_call(chat_id)
    except NoActiveGroupCall:
        pass
    await remove_active_chat(chat_id)
    await clear_queue(chat_id)
    return True
