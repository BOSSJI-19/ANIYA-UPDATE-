from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ChatMemberStatus, ParseMode

# Database Functions
from tools.database import save_filter, get_filter, delete_filter, get_all_filters

# --- 1. SET FILTER COMMAND ---
async def add_filter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ɢʀᴏᴜᴘs.")

    # Permission Check: Kya user Admin hai aur Change Info power hai?
    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await update.message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ꜰɪʟᴛᴇʀs!**")
    
    # Check specific power (Change Info) - Optional but requested
    if member.status == ChatMemberStatus.ADMINISTRATOR and not member.can_change_info:
        return await update.message.reply_text("❌ **ʏᴏᴜ ɴᴇᴇᴅ 'ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴꜰᴏ' ʀɪɢʜᴛs!**")

    # Arguments Check
    if not context.args:
        return await update.message.reply_text("⚠️ **ᴜsᴀɢᴇ:** Reply to a message with `/filter [keyword]`")
    
    keyword = context.args[0].lower()
    reply = update.message.reply_to_message

    if not reply:
        return await update.message.reply_text("❌ **ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ (ᴛᴇxᴛ/ᴍᴇᴅɪᴀ)!**")

    # Data Extract Logic
    file_data = {}
    
    if reply.sticker:
        file_data = {"type": "sticker", "id": reply.sticker.file_id}
    elif reply.photo:
        file_data = {"type": "photo", "id": reply.photo[-1].file_id, "caption": reply.caption}
    elif reply.video:
        file_data = {"type": "video", "id": reply.video.file_id, "caption": reply.caption}
    elif reply.audio:
        file_data = {"type": "audio", "id": reply.audio.file_id, "caption": reply.caption}
    elif reply.document:
        file_data = {"type": "doc", "id": reply.document.file_id, "caption": reply.caption}
    elif reply.animation:
        file_data = {"type": "gif", "id": reply.animation.file_id, "caption": reply.caption}
    elif reply.voice:
        file_data = {"type": "voice", "id": reply.voice.file_id}
    elif reply.text:
        file_data = {"type": "text", "content": reply.text}
    else:
        return await update.message.reply_text("❌ **ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ!**")

    # Save to Database
    await save_filter(chat.id, keyword, file_data)
    await update.message.reply_text(f"✅ **ꜰɪʟᴛᴇʀ sᴀᴠᴇᴅ!**\nKeyword: `{keyword}`")

# --- 2. STOP FILTER COMMAND ---
async def stop_filter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # Admin Check
    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return

    if not context.args:
        return await update.message.reply_text("⚠️ **ᴜsᴀɢᴇ:** `/stop [keyword]`")

    keyword = context.args[0].lower()
    deleted = await delete_filter(chat.id, keyword)
    
    if deleted:
        await update.message.reply_text(f"🗑️ **ꜰɪʟᴛᴇʀ '{keyword}' ᴅᴇʟᴇᴛᴇᴅ!**")
    else:
        await update.message.reply_text("❌ **ꜰɪʟᴛᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!**")

# --- 3. FILTER LIST COMMAND ---
async def list_filters_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    filters_list = await get_all_filters(chat.id)
    
    if not filters_list:
        return await update.message.reply_text("❌ **ɴᴏ ᴀᴄᴛɪᴠᴇ ꜰɪʟᴛᴇʀs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
    
    text = "📝 **ᴀᴄᴛɪᴠᴇ ꜰɪʟᴛᴇʀs:**\n\n"
    for kw in filters_list:
        text += f"🔹 `{kw}`\n"
        
    await update.message.reply_text(text)

# --- 4. MAIN LISTENER (Jo message check karega) ---
async def filter_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    # Sirf groups mein aur text messages par
    if chat.type == "private" or not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()
    
    # Database se check karo
    data = await get_filter(chat.id, text)
    
    if data:
        # Send Logic (Without Reply as requested)
        try:
            msg_type = data["type"]
            
            if msg_type == "text":
                await context.bot.send_message(chat.id, data["content"])
            
            elif msg_type == "sticker":
                await context.bot.send_sticker(chat.id, data["id"])
            
            elif msg_type == "photo":
                await context.bot.send_photo(chat.id, data["id"], caption=data.get("caption"))
            
            elif msg_type == "video":
                await context.bot.send_video(chat.id, data["id"], caption=data.get("caption"))
            
            elif msg_type == "audio":
                await context.bot.send_audio(chat.id, data["id"], caption=data.get("caption"))
                
            elif msg_type == "doc":
                await context.bot.send_document(chat.id, data["id"], caption=data.get("caption"))
                
            elif msg_type == "gif":
                await context.bot.send_animation(chat.id, data["id"], caption=data.get("caption"))
                
            elif msg_type == "voice":
                await context.bot.send_voice(chat.id, data["id"])
                
        except Exception as e:
            print(f"Filter Error: {e}")

# --- REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(CommandHandler(["filter", "save"], add_filter_cmd))
    app.add_handler(CommandHandler(["stop", "stopfilter"], stop_filter_cmd))
    app.add_handler(CommandHandler(["filters", "filterlist"], list_filters_cmd))
    
    # Listener (Dhyan rahe, ye sabse end mein register hona chahiye main.py mein usually)
    # Lekin yahan tools loader ke through ho raha hai to Text Filter use karenge
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_listener))
    
    print("  ✅ Filter Module Loaded!")
  
