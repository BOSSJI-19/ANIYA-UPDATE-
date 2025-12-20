import time
import sys
import os
import psutil
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import get_total_users, get_total_groups

# --- RESTART COMMAND ---
async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sirf Owner use kar sakta hai
    user = update.effective_user
    if str(user.id) != str(OWNER_ID): 
        return

    msg = await update.message.reply_text("🔄 **Restarting System...**")
    await time.sleep(2)
    await msg.edit_text("✅ **System Rebooted!**\nBack online in 5 seconds.")
    
    # Python Process Restart Logic
    os.execl(sys.executable, sys.executable, *sys.argv)

# --- PING COMMAND (Image + Modules) ---
async def ping_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("⚡")
    end_time = time.time()
    
    # Calculate Latency
    ping_ms = round((end_time - start_time) * 1000)
    
    # System Stats
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
    except:
        cpu = 0
        ram = 0
        disk = 0
    
    # Loaded Modules List (Display ke liye)
    modules_list = [
        "Admin", "Bank", "Economy", "Games",
        "Market", "Ranking", "Anti-Spam", 
        "WordSeek", "Logger", "AI Chat", "Group Tools"
    ]
    modules_str = " | ".join(modules_list)
    
    # Ping Image (Anime Style)
    PING_IMG = "https://i.ibb.co/QGGKVnw/image.png" 
    
    caption = f"""╭───〔 🤖 **sʏsᴛᴇᴍ sᴛᴀᴛᴜs** 〕───
┆
┆ ⚡ **ᴘɪɴɢ:** `{ping_ms}ms`
┆ 💻 **ᴄᴘᴜ:** `{cpu}%`
┆ 💾 **ʀᴀᴍ:** `{ram}%`
┆ 💿 **ᴅɪsᴋ:** `{disk}%`
┆
╰──────────────────────
📚 **ʟᴏᴀᴅᴇᴅ ᴍᴏᴅᴜʟᴇs:**
`{modules_str}`"""

    await msg.delete()
    await update.message.reply_photo(
        photo=PING_IMG,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN
    )

# --- STATS COMMAND (Users & Groups) ---
async def stats_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sirf Owner dekh sakta hai
    user = update.effective_user
    if str(user.id) != str(OWNER_ID): 
        return

    # Database se count lo
    try:
        users = get_total_users()
        groups = get_total_groups()
    except:
        users = 0
        groups = 0

    text = f"""📊 **CURRENT DATABASE STATS**
    
👤 **Total Users:** `{users}`
👥 **Total Groups:** `{groups}`
    
⚡ **Server Status:** Running Smoothly
    """
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
