import uuid
from telegram import Update
from telegram.constants import ParseMode, ChatAction
from telegram.ext import CommandHandler, ContextTypes
from pymongo import MongoClient
from config import MONGO_URL, BOT_NAME, ASSISTANT_ID # 🔥 Config check kar lena

# --- DATABASE CONNECTION ---
try:
    mongo = MongoClient(MONGO_URL)
    db = mongo["Music_Database"]
    queue_col = db["Music_Queue"]
    print("✅ Music Database Connected in PTB!")
except Exception as e:
    print(f"❌ Database Error in play.py: {e}")

# --- PLAY COMMAND ---
async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. No Song Name Provided
    if not context.args:
        text = f"""
<blockquote><b>❌ Incorrect Usage</b></blockquote>

<b>Usage:</b> <code>/play [Song Name]</code>
<b>Example:</b> <code>/play Arjan Valley</code>
"""
        return await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    song_name = " ".join(context.args)
    
    # 2. Searching Message (Fancy)
    search_text = f"""
<blockquote><b>🔍 Searching...</b></blockquote>
<code>{song_name}</code>
"""
    status_msg = await update.message.reply_text(search_text, parse_mode=ParseMode.HTML)
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    try:
        # 3. Invite Link Logic
        try:
            invite_link = await context.bot.export_chat_invite_link(chat.id)
        except:
            err_text = """
<blockquote><b>❌ Permission Error</b></blockquote>
Please make me an <b>Admin</b> with <b>Invite Users</b> permission so the assistant can join.
"""
            return await status_msg.edit_text(err_text, parse_mode=ParseMode.HTML)

        # 4. DB Entry
        task = {
            "chat_id": chat.id,
            "title": chat.title,
            "link": invite_link,
            "song": song_name,
            "requester": user.first_name,
            "requester_id": user.id,
            "status": "pending",
            "timestamp": update.message.date
        }
        
        queue_col.insert_one(task)

        # 5. Success Message (Fully Decorated)
        success_text = f"""
<blockquote><b>✅ Added to Queue</b></blockquote>

<b>🎶 Title :</b> {song_name}
<b>👤 Request By :</b> {user.first_name}
<b>⏳ Status :</b> <code>Processing...</code>

<blockquote><i>Assistant is joining via Invite Link...</i></blockquote>
"""
        await status_msg.edit_text(success_text, parse_mode=ParseMode.HTML)

    except Exception as e:
        await status_msg.edit_text(f"<blockquote><b>❌ System Error</b></blockquote>\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)

# --- STOP COMMAND (FORCE STOP) 🛑 ---
async def stop_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    # 1. Permission Check
    user_member = await chat.get_member(update.effective_user.id)
    if user_member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("<blockquote><b>❌ Access Denied</b></blockquote>\nOnly Admins can stop music.", parse_mode=ParseMode.HTML)

    msg = await update.message.reply_text("<blockquote><b>🛑 Stopping...</b></blockquote>", parse_mode=ParseMode.HTML)

    try:
        # 2. Clear Database Queue
        queue_col.delete_many({"chat_id": chat.id})
        
        # 3. Kick Assistant
        try:
            await chat.ban_member(ASSISTANT_ID)
            await chat.unban_member(ASSISTANT_ID)
            
            stop_text = f"""
<blockquote><b>🛑 Music Stopped</b></blockquote>

<b>🗑 Queue :</b> Cleared
<b>👋 Assistant :</b> Disconnected
"""
            await msg.edit_text(stop_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            warn_text = f"""
<blockquote><b>⚠️ Partial Success</b></blockquote>
Queue cleared, but failed to kick Assistant.
<b>Reason:</b> <code>Check ID or Admin Rights</code>
"""
            await msg.edit_text(warn_text, parse_mode=ParseMode.HTML)
            
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

# --- REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(CommandHandler(["play", "p"], play_music))
    app.add_handler(CommandHandler(["stop", "end", "leave", "skip"], stop_music))
