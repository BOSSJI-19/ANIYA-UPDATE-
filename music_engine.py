import os
import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioQuality
from config import API_ID, API_HASH, SESSION_STRING

# Initialize
app = Client(
    "music_assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)
call_py = PyTgCalls(app)

# Start function
async def start_music_bot():
    print("🎵 Starting Music Assistant...")
    await app.start()
    await call_py.start()
    print("✅ Music System Ready!")

# Play function - RENDER COMPATIBLE
async def play_audio(chat_id, file_path):
    try:
        # RENDER पर file path check
        if not os.path.exists(file_path):
            # Agar file local nahi hai, toh URL se stream karein
            if file_path.startswith(('http://', 'https://')):
                stream = AudioPiped(
                    file_path,
                    audio_quality=AudioQuality.STUDIO
                )
            else:
                print(f"❌ File not found on RENDER: {file_path}")
                return False
        else:
            # Local file hai
            stream = AudioPiped(
                file_path,
                audio_quality=AudioQuality.STUDIO
            )
        
        await call_py.join_group_call(chat_id, stream)
        return True
    except Exception as e:
        print(f"Play Error on RENDER: {e}")
        return False

# Stop function
async def stop_audio(chat_id):
    try:
        await call_py.leave_group_call(chat_id)
    except:
        pass