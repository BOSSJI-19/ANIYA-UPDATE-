import os
import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, SESSION_STRING
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients (DO NOT start them here)
app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True  # Important for Render
)
call_py = PyTgCalls(app)

# --- CORE PLAY FUNCTION (with compatibility layer) ---
async def play_audio(chat_id, file_path_or_url):
    """
    Universal play function. Accepts local file path or direct audio URL.
    """
    try:
        logger.info(f"Attempting to play: {file_path_or_url} in chat {chat_id}")
        
        # 1. CHECK INPUT
        # If it's a local file, verify it exists on Render's ephemeral disk
        if not file_path_or_url.startswith(('http://', 'https://')):
            if not os.path.exists(file_path_or_url):
                logger.error(f"Local file not found on Render: {file_path_or_url}")
                # On Render, you should stream from URLs. Local files are tricky.
                return False
            input_arg = file_path_or_url
        else:
            input_arg = file_path_or_url  # It's already a URL
        
        # 2. ATTEMPT TO IMPORT AND USE MODERN API (with AudioQuality)
        try:
            from pytgcalls.types import AudioPiped, AudioQuality
            logger.info("Using modern API (AudioPiped with AudioQuality)")
            stream = AudioPiped(
                input_arg,
                audio_quality=AudioQuality.STUDIO  # Or HIGH, MEDIUM, LOW
            )
        
        # 3. FALLBACK: If AudioQuality import fails, use basic AudioPiped
        except ImportError:
            logger.warning("AudioQuality not found. Using basic AudioPiped.")
            from pytgcalls.types import AudioPiped
            stream = AudioPiped(input_arg)
            # You can also try 'InputAudioStream' if 'AudioPiped' fails
            # from pytgcalls.types.input_stream import InputAudioStream
            # stream = InputAudioStream(input_arg)
        
        # 4. JOIN CALL AND STREAM
        await call_py.join_group_call(chat_id, stream)
        logger.info(f"Successfully joined voice chat {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Play function failed: {e}", exc_info=True)
        return False

# --- STOP FUNCTION ---
async def stop_audio(chat_id):
    """Leave the voice call."""
    try:
        await call_py.leave_group_call(chat_id)
        logger.info(f"Left voice chat: {chat_id}")
    except Exception as e:
        logger.error(f"Error leaving call: {e}")

# --- START FUNCTION (Call this from main.py post_init) ---
async def start_music_bot():
    """Initialize and start the music client. CALL THIS FROM main.py."""
    logger.info("Starting Music Assistant...")
    try:
        # Start the Pyrogram client
        await app.start()
        logger.info("Pyrogram client started.")
        # Start the PyTgCalls client
        await call_py.start()
        logger.info("✅ PyTgCalls (Music System) Ready!")
    except Exception as e:
        logger.critical(f"Failed to start music system: {e}")
        # Don't raise the error; let the main bot run without music
        # This prevents the entire bot from crashing