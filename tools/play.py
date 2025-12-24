import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from tools.youtube import yt
from music_engine import play_audio, play_video, stop_stream, join_group

async def ensure_assistant(update, context):
    chat = update.effective_chat
    try:
        invite = await context.bot.export_chat_invite_link(chat.id)
        if await join_group(chat.id, invite): return True
    except:
        await update.message.reply_text("⚠️ Give me 'Invite Users' permission first!")
    return False

async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat_id = update.effective_chat.id
    
    query = " ".join(context.args) if context.args else None
    reply = msg.reply_to_message

    if not query and not (reply and (reply.audio or reply.voice)):
        return await msg.reply_text("Usage: `/play song` or Reply to Audio.")

    if not await ensure_assistant(update, context): return
    status = await msg.reply_text("🔎 <b>Processing...</b>", parse_mode=ParseMode.HTML)

    file_path, title, duration, link = None, "Unknown", "Unknown", ""

    try:
        if reply and (reply.audio or reply.voice):
            await status.edit_text("⬇️ <b>Downloading Telegram Audio...</b>")
            audio = reply.audio or reply.voice
            file = await context.bot.get_file(audio.file_id)
            file_path = f"downloads/{audio.file_unique_id}.mp3"
            await file.download_to_drive(file_path)
            title = audio.file_name or "Telegram Audio"
        elif query:
            await status.edit_text(f"🔎 <b>Searching:</b> `{query}`", parse_mode=ParseMode.HTML)
            details = await yt.get_details(query)
            if not details: return await status.edit_text("❌ Not Found!")
            await status.edit_text(f"⬇️ <b>Downloading:</b> {details['title']}...")
            file_path = await yt.download(details['link'], audio_only=True)
            title = details['title']
            duration = details['duration']
            link = details['link']

        if file_path and os.path.exists(file_path):
            await status.edit_text("🔈 <b>Connecting to VC...</b>")
            if await play_audio(chat_id, file_path):
                txt = f"""
<blockquote><b>🔊 sᴛʀᴇᴀᴍɪɴɢ sᴛᴀʀᴛᴇᴅ</b></blockquote>
<blockquote>
<b>🏷 ᴛɪᴛʟᴇ :</b> <a href="{link}">{title}</a>
<b>⏱ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {update.effective_user.mention_html()}
</blockquote>"""
                kb = [[InlineKeyboardButton("⏹ Stop", callback_data="stop_music")]]
                await status.edit_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
            else: await status.edit_text("❌ Check VC/Userbot Admin!")
        else: await status.edit_text("❌ Download Failed.")
    except Exception as e: await status.edit_text(f"Error: {e}")

async def stop_command(update, context):
    if await stop_stream(update.effective_chat.id):
        await update.message.reply_text("⏹ Stopped.")
    else: await update.message.reply_text("❌ Nothing playing.")

async def cb_stop(update, context):
    await stop_stream(update.effective_chat.id)
    await update.callback_query.message.edit_text("⏹ Stream Stopped.")

def register_handlers(app):
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CallbackQueryHandler(cb_stop, pattern="^stop_music$"))
