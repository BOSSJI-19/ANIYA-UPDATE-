import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode, ChatAction

# Imports
from tools.controller import process_stream
from tools.stream import play_stream
from tools.database import get_cached_song, save_cached_song # Jo upar banaya
from config import OWNER_NAME

# --- FPLAY COMMAND (/fplay) ---
async def fplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    try: await update.message.delete()
    except: pass

    if not context.args:
        return await context.bot.send_message(chat.id, "❌ <b>Usage:</b> /fplay [Song Name]", parse_mode=ParseMode.HTML)

    query = " ".join(context.args)
    
    status_msg = await context.bot.send_message(
        chat.id,
        f"<blockquote>⚡ <b>Fast Searching...</b>\n<code>{query}</code></blockquote>", 
        parse_mode=ParseMode.HTML
    )

    # --- 🚀 STEP 1: CHECK DATABASE (CACHE) ---
    cached_data = await get_cached_song(query)

    if cached_data:
        # ✅ Agar Cache mil gaya (FAST PLAY)
        await status_msg.edit_text(f"<blockquote>🚀 <b>Found in Cache! Playing Fast...</b></blockquote>", parse_mode=ParseMode.HTML)
        
        # Data DB se uthao
        title = cached_data["title"]
        duration = cached_data["duration"]
        thumbnail = cached_data["thumbnail"]
        link = cached_data["link"]
        # Note: Hum link use kar rahe hain, par actual play ke liye fresh extraction chahiye hoti hai
        # unless tumhare paas direct file ID ho.
        # Lekin "Search" ka time bach gaya yahan!
        
        # Direct Play Logic Call karo
        success, position = await play_stream(chat.id, link, title, duration, user.first_name, link, thumbnail)
        
        # (Yahan normal play message logic aayega buttons wala... same music.py jaisa)
        # Short me dikha raha hu:
        if success:
             await context.bot.send_photo(chat.id, photo=thumbnail, caption=f"🚀 <b>Fast Play:</b> {title}")
        
        # Message delete
        try: await status_msg.delete()
        except: pass
        return

    # --- 🐢 STEP 2: AGAR CACHE NAHI HAI (NORMAL PLAY + SAVE) ---
    await status_msg.edit_text(f"<blockquote>🔍 <b>Searching Web...</b>\n<code>{query}</code></blockquote>", parse_mode=ParseMode.HTML)
    
    # Controller call karo (Search + Download)
    error, data = await process_stream(chat.id, user.first_name, query)
    
    if error:
        return await status_msg.edit_text(error)

    # --- 🔥 STEP 3: SAVE TO DATABASE FOR NEXT TIME ---
    # Hum result ko save kar lenge taaki agli baar /fplay kaam kare
    cache_entry = {
        "title": data["title"],
        "duration": data["duration"],
        "thumbnail": data["thumbnail"],
        "link": data["link"] # YouTube URL (Not stream link)
    }
    await save_cached_song(query, cache_entry)

    # Baki Play logic same rahega... (Buttons, Caption etc.)
    # ...
    # ... (Yahan music.py wala same buttons code copy kar lena)
    
    await status_msg.delete()


def register_handlers(app):
    app.add_handler(CommandHandler(["fplay", "fp"], fplay_command))
    print("  ✅ Fast-Play Module Loaded!")
