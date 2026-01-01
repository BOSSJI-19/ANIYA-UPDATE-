import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

# Configs
from config import OWNER_ID
from tools.stream import worker_app  # Assistant Client

# ✅ CORRECTED IMPORT (Database Fix)
from tools.database import get_served_users, get_served_chats 

# --- SUDO SETTINGS ---
SUDO_USERS = [6356015122, int(OWNER_ID)]

# --- 1. BROADCAST USERS (DM) ---
async def broadcast_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ!**")

    status_msg = await update.message.reply_text("🔄 **ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ ᴜsᴇʀs (ᴅᴍs)...**")
    
    users = await get_served_users()
    sent = 0
    failed = 0
    
    msg = update.message.reply_to_message
    
    for user_id in users:
        try:
            await context.bot.copy_message(chat_id=user_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            sent += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
            
    await status_msg.edit_text(f"✅ **ᴅᴍ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ**\n\n📤 **sᴇɴᴛ:** {sent}\n❌ **ꜰᴀɪʟᴇᴅ:** {failed}")

# --- 2. BROADCAST GROUPS (GC) ---
async def broadcast_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ!**")

    status_msg = await update.message.reply_text("🔄 **ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ ɢʀᴏᴜᴘs...**")
    
    chats = await get_served_chats()
    sent = 0
    failed = 0
    
    msg = update.message.reply_to_message
    
    for chat_id in chats:
        try:
            await context.bot.copy_message(chat_id=chat_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            sent += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
            
    await status_msg.edit_text(f"✅ **ɢʀᴏᴜᴘ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ**\n\n📤 **sᴇɴᴛ:** {sent}\n❌ **ꜰᴀɪʟᴇᴅ:** {failed}")

# --- 3. BROADCAST ASSISTANT (AC) ---
async def broadcast_assistant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ!**")

    status_msg = await update.message.reply_text("🔄 **ᴀssɪsᴛᴀɴᴛ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...**")
    
    reply = update.message.reply_to_message
    query = reply.text or reply.caption
    
    chats = await get_served_chats()
    sent = 0
    failed = 0

    if not query:
         return await status_msg.edit_text("❌ **ᴛᴇxᴛ ʀᴇǫᴜɪʀᴇᴅ ꜰᴏʀ ᴀssɪsᴛᴀɴᴛ ʙʀᴏᴀᴅᴄᴀsᴛ!**")

    for chat_id in chats:
        try:
            await worker_app.send_message(chat_id, query)
            sent += 1
            await asyncio.sleep(1.5)
        except:
            failed += 1

    await status_msg.edit_text(f"✅ **ᴀssɪsᴛᴀɴᴛ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ**\n\n📤 **sᴇɴᴛ:** {sent}\n❌ **ꜰᴀɪʟᴇᴅ:** {failed}")

# --- 4. BROADCAST ALL (MEGA COMMAND) ---
async def broadcast_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS: return

    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ **ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ `/broadcastall`**")

    status_msg = await update.message.reply_text("🚀 **sᴛᴀʀᴛɪɴɢ ɢʟᴏʙᴀʟ ʙʀᴏᴀᴅᴄᴀsᴛ...**\n⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...")

    msg = update.message.reply_to_message
    query = msg.text or msg.caption
    
    users_list = await get_served_users()
    chats_list = await get_served_chats()
    
    dm_sent, dm_fail = 0, 0
    gc_sent, gc_fail = 0, 0
    ac_sent, ac_fail = 0, 0

    # PHASE 1: BOT -> DMs
    await status_msg.edit_text("🔄 **ᴘʜᴀsᴇ 1: sᴇɴᴅɪɴɢ ᴛᴏ ᴅᴍs...**")
    for u_id in users_list:
        try:
            await context.bot.copy_message(chat_id=u_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            dm_sent += 1
            await asyncio.sleep(0.1)
        except: dm_fail += 1

    # PHASE 2: BOT -> GROUPS
    await status_msg.edit_text(f"✅ ᴅᴍs ᴅᴏɴᴇ ({dm_sent}).\n🔄 **ᴘʜᴀsᴇ 2: sᴇɴᴅɪɴɢ ᴛᴏ ɢʀᴏᴜᴘs...**")
    for c_id in chats_list:
        try:
            await context.bot.copy_message(chat_id=c_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            gc_sent += 1
            await asyncio.sleep(0.1)
        except: gc_fail += 1

    # PHASE 3: ASSISTANT -> GROUPS
    if query:
        await status_msg.edit_text(f"✅ ʙᴏᴛ ɢʀᴏᴜᴘs ᴅᴏɴᴇ ({gc_sent}).\n🔄 **ᴘʜᴀsᴇ 3: ᴀssɪsᴛᴀɴᴛ sᴇɴᴅɪɴɢ...**")
        for c_id in chats_list:
            try:
                await worker_app.send_message(c_id, query)
                ac_sent += 1
                await asyncio.sleep(1.5)
            except: ac_fail += 1
    else:
        await status_msg.edit_text("⚠️ **ɴᴏ ᴛᴇxᴛ ꜰᴏᴜɴᴅ, sᴋɪᴘᴘɪɴɢ ᴀssɪsᴛᴀɴᴛ.**")

    # FINAL REPORT
    report = f"""
✅ **ɢʟᴏʙᴀʟ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ**

👤 **ʙᴏᴛ ᴅᴍs:** {dm_sent} (Fail: {dm_fail})
📢 **ʙᴏᴛ ɢʀᴏᴜᴘs:** {gc_sent} (Fail: {gc_fail})
🎸 **ᴀssɪsᴛᴀɴᴛ:** {ac_sent} (Fail: {ac_fail})

⚡ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ:** {user.first_name}
"""
    await status_msg.edit_text(report)

# --- HANDLER REGISTRATION ---
def register_broadcast_handlers(app):
    app.add_handler(CommandHandler(["broadcast", "broadcastdm"], broadcast_users))
    app.add_handler(CommandHandler(["broadcastgc", "broadcastgroup"], broadcast_groups))
    app.add_handler(CommandHandler(["broadcastac"], broadcast_assistant))
    app.add_handler(CommandHandler(["broadcastall", "bcall"], broadcast_all_command))
    print("📢 Broadcast Module Loaded!")
    
