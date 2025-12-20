from telegram import Update, ChatPermissions
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes
from database import add_warning, remove_warning, reset_warnings
from config import OWNER_ID

# --- HELPER: CHECK USER ADMIN ---
async def is_admin(update: Update):
    """Check karega ki command chalane wala Admin hai ya nahi"""
    user = update.effective_user
    chat = update.effective_chat
    
    # 1. Private Chat me Admin check fail hoga (Logic)
    if chat.type == "private":
        return False

    # 2. Owner Check
    if user.id == int(OWNER_ID): 
        return True
    
    # 3. Group Admin Check
    try:
        member = await chat.get_member(user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
    except Exception as e:
        print(f"❌ Admin Check Error: {e}")
    
    return False

# --- HELPER: CHECK BOT PERMISSIONS ---
async def bot_can_restrict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check karega ki Bot khud Admin hai ya nahi"""
    chat = update.effective_chat
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.status == ChatMemberStatus.ADMINISTRATOR
    except:
        return False

# --- COMMANDS ---

async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        return await update.message.reply_text("❌ Ye command sirf Group me chalegi.")

    # Auto Delete Command
    try: await update.message.delete()
    except: pass

    # Permission Check
    if not await is_admin(update): return

    if not update.message.reply_to_message:
        return await chat.send_message(f"⚠️ **{update.effective_user.first_name}**, kisi user ko reply karke command do.", parse_mode=ParseMode.MARKDOWN)

    target = update.message.reply_to_message.from_user
    
    # Self/Bot Check
    if target.id == int(OWNER_ID) or target.is_bot:
        return await chat.send_message("❌ Owner ya Bot ko warn nahi kar sakte!")

    # Database call
    count = add_warning(chat.id, target.id)
    
    if count >= 3:
        # Ban logic
        try:
            await chat.ban_member(target.id)
            reset_warnings(chat.id, target.id)
            await chat.send_message(f"🚫 **Banned!** {target.first_name} reached 3 warnings.")
        except Exception as e:
            await chat.send_message(f"❌ **Error:** Main {target.first_name} ko ban nahi kar pa raha.\nMujhe Admin banao! ({e})")
    else:
        await chat.send_message(f"⚠️ **Warning!** {target.first_name} has {count}/3 warnings.")

async def unwarn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat
    
    count = remove_warning(chat.id, target.id)
    await chat.send_message(f"✅ **Unwarned!** {target.first_name} now has {count} warnings.")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat
    
    try:
        await chat.restrict_member(target.id, permissions=ChatPermissions(can_send_messages=False))
        await chat.send_message(f"🔇 **Muted!** {target.first_name}")
    except Exception as e:
        await chat.send_message(f"❌ Error: Mujhe Admin rights chahiye. ({e})")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    chat = update.effective_chat
    
    try:
        # Restore permissions
        await chat.restrict_member(
            target.id, 
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_send_polls=True
            )
        )
        await chat.send_message(f"🔊 **Unmuted!** {target.first_name}")
    except Exception as e:
        await chat.send_message(f"❌ Error: {e}")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.ban_member(target.id)
        await update.effective_chat.send_message(f"🚫 **Banned!** {target.first_name}")
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.unban_member(target.id)
        await update.effective_chat.send_message(f"✅ **Unbanned!** {target.first_name}")
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.ban_member(target.id)
        await update.effective_chat.unban_member(target.id)
        await update.effective_chat.send_message(f"🦵 **Kicked!** {target.first_name}")
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    
    can_change_info = False
    can_delete = True
    can_invite = True
    can_pin = False
    
    if context.args:
        level = context.args[0]
        if level == "2":
            can_pin = True
            can_change_info = True
        elif level == "3":
            can_pin = True
            can_change_info = True
            
    try:
        await update.effective_chat.promote_member(
            user_id=target.id,
            can_delete_messages=can_delete,
            can_invite_users=can_invite,
            can_pin_messages=can_pin,
            can_change_info=can_change_info,
            is_anonymous=False
        )
        await update.effective_chat.send_message(f"👮‍♂️ **Promoted!** {target.first_name}")
    except Exception as e:
        await update.effective_chat.send_message(f"❌ Error: {e}")

async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.promote_member(
            user_id=target.id,
            can_delete_messages=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_change_info=False,
            is_anonymous=False
        )
        await update.effective_chat.send_message(f"⬇️ **Demoted!** {target.first_name}")
    except:
        await update.effective_chat.send_message("❌ Failed. Check my permissions.")

async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    if not context.args: return
    title = " ".join(context.args)
    target = update.message.reply_to_message.from_user
    
    try:
        await update.effective_chat.set_administrator_custom_title(target.id, title)
        await update.effective_chat.send_message(f"🏷 **Title Set:** {title}")
    except:
        await update.effective_chat.send_message("❌ Error. Needs 'Can Promote' rights.")

async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    try:
        await update.message.reply_to_message.pin()
    except: pass

async def unpin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    if not await is_admin(update): return
    try:
        await update.effective_chat.unpin_all_messages() 
    except: pass

async def delete_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bot Command delete karo
    try: await update.message.delete()
    except: pass
    
    # Check Admin
    if not await is_admin(update): return

    # Target Message delete karo
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
        except:
            # Agar fail hua (e.g. msg too old), ignore karo
            pass

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.delete()
    except: pass
    
    text = (
        "🛡️ **Admin Commands** (Works with . or /)\n\n"
        "🔸 `.warn` - Warn user (3 = Ban)\n"
        "🔸 `.unwarn` - Remove warning\n"
        "🔸 `.mute` - Mute user\n"
        "🔸 `.unmute` - Unmute user\n"
        "🔸 `.ban` - Ban user\n"
        "🔸 `.unban` - Unban user\n"
        "🔸 `.kick` - Kick user\n"
        "🔸 `.promote` - Promote (Use 1, 2, 3 for levels)\n"
        "🔸 `.demote` - Demote admin\n"
        "🔸 `.title [text]` - Set admin title\n"
        "🔸 `.pin` - Pin message\n"
        "🔸 `.d` - Delete replied message"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
