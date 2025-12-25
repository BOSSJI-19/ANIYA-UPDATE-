import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, Application, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest

# Database imports (agar aapke pass database.py hai)
from database import users_col, get_balance

# Variables
spam_chats = []

EMOJI = [
    "🦋🦋🦋🦋🦋", "🧚🌸🧋🍬🫖", "🥀🌷🌹🌺💐", "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤", "💓💕💞💗💖", "🌸💐🌺🌹🦋", "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️", "🧋🥤🧋🥛🍷", "🍬🍭🧁🎂🍡", "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚", "🫖☕🍹🍷🥛", "☕🧃🍩🍦🍙", "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️", "🌷🏵️🌸🌺💐", "💮🌼🌻🍀🍁", "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦", "🐷🐹🐭🐨🐻‍❄️", "🦋🐇🐀🐈🐈‍⬛", "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇", "🍴🍽️🔪🍶🥃", "🕌🏰🏩⛩️🏩", "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲", "🎄🎋🎍🎑🎎", "🦅🦜🕊️🦤🦢", "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳", "🐔🐟🐠🐡🦐", "🦩🦀🦑🐙🦪", "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨", " 🥬🍉🧁🧇",
]

TAGMES = [
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ 🌚**",
    "**➠ ᴄʜᴜᴘ ᴄʜᴀᴘ sᴏ ᴊᴀ 🙊**",
    "**➠ ᴘʜᴏɴᴇ ʀᴀᴋʜ ᴋᴀʀ sᴏ ᴊᴀ, ɴᴀʜɪ ᴛᴏ ʙʜᴏᴏᴛ ᴀᴀ ᴊᴀʏᴇɢᴀ..👻**",
    "**➠ ᴀᴡᴇᴇ ʙᴀʙᴜ sᴏɴᴀ ᴅɪɴ ᴍᴇɪɴ ᴋᴀʀ ʟᴇɴᴀ ᴀʙʜɪ sᴏ ᴊᴀᴏ..?? 🥲**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ᴀᴘɴᴇ ɢғ sᴇ ʙᴀᴀᴛ ᴋʀ ʀʜᴀ ʜ ʀᴀᴊᴀɪ ᴍᴇ ɢʜᴜs ᴋᴀʀ, sᴏ ɴᴀʜɪ ʀᴀʜᴀ 😜**",
    "**➠ ᴘᴀᴘᴀ ʏᴇ ᴅᴇᴋʜᴏ ᴀᴘɴᴇ ʙᴇᴛᴇ ᴋᴏ ʀᴀᴀᴛ ʙʜᴀʀ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ʜᴀɪ 🤭**",
    "**➠ ᴊᴀɴᴜ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ..?? 🌠**",
    "**➠ ɢɴ sᴅ ᴛᴄ.. 🙂**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ ᴛᴀᴋᴇ ᴄᴀʀᴇ..?? ✨**",
    "**➠ ʀᴀᴀᴛ ʙʜᴜᴛ ʜᴏ ɢʏɪ ʜᴀɪ sᴏ ᴊᴀᴏ, ɢɴ..?? 🌌**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ 11 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ɴᴀʜɪ sᴏ ɴᴀʜɪ ʀᴀʜᴀ 🕦**",
    "**➠ ᴋᴀʟ sᴜʙʜᴀ sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴀᴋ ᴊᴀɢ ʀʜᴇ ʜᴏ 🏫**",
    "**➠ ʙᴀʙᴜ, ɢᴏᴏᴅ ɴɪɢʜᴛ sᴅ ᴛᴄ..?? 😊**",
    "**➠ ᴀᴀᴊ ʙʜᴜᴛ ᴛʜᴀɴᴅ ʜᴀɪ, ᴀᴀʀᴀᴍ sᴇ ᴊᴀʟᴅɪ sᴏ ᴊᴀᴛɪ ʜᴏᴏɴ 🌼**",
    "**➠ ᴊᴀɴᴇᴍᴀɴ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🌷**",
    "**➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ sᴏɴᴇ, ɢɴ sᴅ ᴛᴄ 🏵️**",
    "**➠ ʜᴇʟʟᴏ ᴊɪ ɴᴀᴍᴀsᴛᴇ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🍃**",
    "**➠ ʜᴇʏ, ʙᴀʙʏ ᴋᴋʀʜ..? sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ ☃️**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ, ʙʜᴜᴛ ʀᴀᴀᴛ ʜᴏ ɢʏɪ..? ⛄**",
    "**➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ ʀᴏɴᴇ, ɪ ᴍᴇᴀɴ sᴏɴᴇ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ 😁**",
    "**➠ ᴍᴀᴄʜʜᴀʟɪ ᴋᴏ ᴋᴇʜᴛᴇ ʜᴀɪ ғɪsʜ, ɢᴏᴏᴅ ɴɪɢʜᴛ ᴅᴇᴀʀ ᴍᴀᴛ ᴋʀɴᴀ ᴍɪss, ᴊᴀ ʀʜɪ sᴏɴᴇ 🌄**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ʙʀɪɢʜᴛғᴜʟʟ ɴɪɢʜᴛ 🤭**",
    "**➠ ᴛʜᴇ ɴɪɢʜᴛ ʜᴀs ғᴀʟʟᴇɴ, ᴛʜᴇ ᴅᴀʏ ɪs ᴅᴏɴᴇ,, ᴛʜᴇ ᴍᴏᴏɴ ʜᴀs ᴛᴀᴋᴇɴ ᴛʜᴇ ᴘʟᴀᴄᴇ ᴏғ ᴛʜᴇ sᴜɴ... 😊**",
    "**➠ ᴍᴀʏ ᴀʟʟ ʏᴏᴜʀ ᴅʀᴇᴀᴍs ᴄᴏᴍᴇ ᴛʀᴜᴇ ❤️**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴘʀɪɴᴋʟᴇs sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ 💚**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ, ɴɪɴᴅ ᴀᴀ ʀʜɪ ʜᴀɪ 🥱**",
    "**➠ ᴅᴇᴀʀ ғʀɪᴇɴᴅ ɢᴏᴏᴅ ɴɪɢʜᴛ 💤**",
    "**➠ ʙᴀʙʏ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ 🥰**",
    "**➠ ɪᴛɴɪ ʀᴀᴀᴛ ᴍᴇ ᴊᴀɢ ᴋᴀʀ ᴋʏᴀ ᴋᴀʀ ʀʜᴇ ʜᴏ sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 😜**",
    "**➠ ᴄʟᴏsᴇ ʏᴏᴜʀ ᴇʏᴇs sɴᴜɢɢʟᴇ ᴜᴘ ᴛɪɢʜᴛ,, ᴀɴᴅ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ᴀɴɢᴇʟs, ᴡɪʟʟ ᴡᴀᴛᴄʜ ᴏᴠᴇʀ ʏᴏᴜ ᴛᴏɴɪɢʜᴛ... 💫**",
]

VC_TAG = [
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋᴇsᴇ ʜᴏ 🐱**",
    "**➠ ɢᴍ, sᴜʙʜᴀ ʜᴏ ɢʏɪ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 🌤️**",
    "**➠ ɢᴍ ʙᴀʙʏ, ᴄʜᴀɪ ᴘɪ ʟᴏ ☕**",
    "**➠ ᴊᴀʟᴅɪ ᴜᴛʜᴏ, sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ 🏫**",
    "**➠ ɢᴍ, ᴄʜᴜᴘ ᴄʜᴀᴘ ʙɪsᴛᴇʀ sᴇ ᴜᴛʜᴏ ᴠʀɴᴀ ᴘᴀɴɪ ᴅᴀʟ ᴅᴜɴɢɪ 🧊**",
    "**➠ ʙᴀʙʏ ᴜᴛʜᴏ ᴀᴜʀ ᴊᴀʟᴅɪ ғʀᴇsʜ ʜᴏ ᴊᴀᴏ, ɴᴀsᴛᴀ ʀᴇᴀᴅʏ ʜᴀɪ 🫕**",
    "**➠ ᴏғғɪᴄᴇ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ ᴊɪ ᴀᴀᴊ, ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🏣**",
    "**➠ ɢᴍ ᴅᴏsᴛ, ᴄᴏғғᴇᴇ/ᴛᴇᴀ ᴋʏᴀ ʟᴏɢᴇ ☕🍵**",
    "**➠ ʙᴀʙʏ 8 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ, ᴀᴜʀ ᴛᴜᴍ ᴀʙʜɪ ᴛᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🕖**",
    "**➠ ᴋʜᴜᴍʙʜᴋᴀʀᴀɴ ᴋɪ ᴀᴜʟᴀᴅ ᴜᴛʜ ᴊᴀᴀ... ☃️**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ... 🌄**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴀᴠᴇ ᴀ ɢᴏᴏᴅ ᴅᴀʏ... 🪴**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ʙᴀʙʏ 😇**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ɴᴀʟᴀʏᴋ ᴀʙʜɪ ᴛᴀᴋ sᴏ ʀʜᴀ ʜᴀɪ... 😵‍💫**",
    "**➠ ʀᴀᴀᴛ ʙʜᴀʀ ʙᴀʙᴜ sᴏɴᴀ ᴋʀ ʀʜᴇ ᴛʜᴇ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴋ sᴏ ʀʜᴇ ʜᴏ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ... 😏**",
    "**➠ ʙᴀʙᴜ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ᴜᴛʜ ᴊᴀᴏ ᴀᴜʀ ɢʀᴏᴜᴘ ᴍᴇ sᴀʙ ғʀɪᴇɴᴅs ᴋᴏ ɢᴍ ᴡɪsʜ ᴋʀᴏ... 🌟**",
    "**➠ ᴘᴀᴘᴀ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜ ɴᴀʜɪ, sᴄʜᴏᴏʟ ᴋᴀ ᴛɪᴍᴇ ɴɪᴋᴀʟᴛᴀ ᴊᴀ ʀʜᴀ ʜᴀɪ... 🥲**",
    "**➠ ᴊᴀɴᴇᴍᴀɴ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋʏᴀ ᴋʀ ʀʜᴇ ʜᴏ ... 😅**",
    "**➠ ɢᴍ ʙᴇᴀsᴛɪᴇ, ʙʀᴇᴀᴋғᴀsᴛ ʜᴜᴀ ᴋʏᴀ... 🍳**",
]

# ==================== HELPER FUNCTIONS ====================
async def is_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is admin in group"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['creator', 'administrator']
    except:
        return False

# ==================== COMMAND HANDLERS ====================
async def tag_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tagall command"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Check if already running
    if chat.id in spam_chats:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    # Check for text
    mode = "text_on_cmd"
    msg_text = ""
    
    if update.message.reply_to_message:
        mode = "text_on_reply"
        if update.message.reply_to_message.text:
            msg_text = update.message.reply_to_message.text
    elif context.args:
        msg_text = " ".join(context.args)
    
    # Ask for text if not provided
    if not msg_text and mode == "text_on_cmd":
        await update.message.reply_text(
            "📝 Please provide text or reply to a message!\n"
            "Example: `/tagall Good Morning` or reply to a message with `/tagall`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("🎯 Starting tag process...")
    spam_chats.append(chat.id)
    
    try:
        member_count = 0
        async for member in context.bot.get_chat_members(chat.id):
            if chat.id not in spam_chats:
                break
            
            # Skip bots
            if member.user.is_bot:
                continue
            
            member_count += 1
            user_mention = f"[{member.user.first_name}](tg://user?id={member.user.id})"
            
            if mode == "text_on_cmd":
                message_text = f"{user_mention} {random.choice(TAGMES)}"
            else:  # text_on_reply
                message_text = f"{user_mention} {msg_text}"
            
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                await asyncio.sleep(3)  # Delay between tags
            except Exception as e:
                print(f"Error tagging user: {e}")
                continue
            
    except Exception as e:
        print(f"Tag error: {e}")
    finally:
        if chat.id in spam_chats:
            spam_chats.remove(chat.id)
        await context.bot.send_message(chat_id=chat.id, text="✅ Tagging completed!")

async def tag_all_gm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gmtag command (Good Morning tag)"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Check if already running
    if chat.id in spam_chats:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    await update.message.reply_text("🌅 Starting Good Morning tag...")
    spam_chats.append(chat.id)
    
    try:
        member_count = 0
        async for member in context.bot.get_chat_members(chat.id):
            if chat.id not in spam_chats:
                break
            
            # Skip bots
            if member.user.is_bot:
                continue
            
            member_count += 1
            user_mention = f"[{member.user.first_name}](tg://user?id={member.user.id})"
            message_text = f"{user_mention} {random.choice(VC_TAG)}"
            
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                await asyncio.sleep(4)  # Delay between tags
            except Exception as e:
                print(f"Error tagging user: {e}")
                continue
            
    except Exception as e:
        print(f"Tag error: {e}")
    finally:
        if chat.id in spam_chats:
            spam_chats.remove(chat.id)
        await context.bot.send_message(chat_id=chat.id, text="✅ Good Morning tagging completed!")

async def tag_all_gn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gntag command (Good Night tag)"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Check if already running
    if chat.id in spam_chats:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    await update.message.reply_text("🌙 Starting Good Night tag...")
    spam_chats.append(chat.id)
    
    try:
        member_count = 0
        async for member in context.bot.get_chat_members(chat.id):
            if chat.id not in spam_chats:
                break
            
            # Skip bots
            if member.user.is_bot:
                continue
            
            member_count += 1
            user_mention = f"[{member.user.first_name}](tg://user?id={member.user.id})"
            message_text = f"{user_mention} {random.choice(TAGMES)}"
            
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                await asyncio.sleep(4)  # Delay between tags
            except Exception as e:
                print(f"Error tagging user: {e}")
                continue
            
    except Exception as e:
        print(f"Tag error: {e}")
    finally:
        if chat.id in spam_chats:
            spam_chats.remove(chat.id)
        await context.bot.send_message(chat_id=chat.id, text="✅ Good Night tagging completed!")

async def tag_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop tagging process"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.id not in spam_chats:
        await update.message.reply_text("ℹ️ No tagging process is currently running.")
        return
    
    # Check admin
    if not await is_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to stop tagging!")
        return
    
    spam_chats.remove(chat.id)
    await update.message.reply_text("🛑 Tagging process stopped successfully!")

async def tag_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help for tag commands"""
    help_text = """
🎯 **TAGGER PLUGIN COMMANDS:**

**For Admins Only:**
• `/tagall [text]` - Tag all members with custom text
• `/tagall` (reply to message) - Tag all with replied message
• `/gmtag` - Tag all with Good Morning messages
• `/gntag` - Tag all with Good Night messages
• `/tagstop` - Stop ongoing tagging process

**Examples:**
`/tagall Hello everyone!`
`/tagall` (reply to a message)
`/gmtag` - Sends GM to everyone
`/gntag` - Sends GN to everyone

⚠️ **Note:** Use responsibly! Tagging too frequently may cause rate limits.
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# ==================== REGISTER HANDLERS ====================
def register_handlers(app: Application):
    """Register all handlers for this plugin"""
    app.add_handler(CommandHandler("tagall", tag_all))
    app.add_handler(CommandHandler("gmtag", tag_all_gm))
    app.add_handler(CommandHandler("gntag", tag_all_gn))
    app.add_handler(CommandHandler("tagstop", tag_stop))
    app.add_handler(CommandHandler("taghelp", tag_help))
    app.add_handler(CommandHandler(["tagcancel", "cancletag"], tag_stop))
    
    print("✅ Tagger Plugin Loaded!")

# For direct testing
if __name__ == "__main__":
    print("🧪 Testing Tagger Plugin...")
    print(f"Commands available:")
    print("  /tagall [text]")
    print("  /gmtag")
    print("  /gntag")
    print("  /tagstop")
