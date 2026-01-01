from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import OWNER_ID
from tools.database import set_global_music

# Tumhara ID aur Owner ID
SUDO_USERS = [6356015122, int(OWNER_ID)]

async def music_switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id not in SUDO_USERS:
        return await update.message.reply_text("❌ **sɪʀꜰ ᴏᴡɴᴇʀ ʏᴇ ᴋᴀʀ sᴀᴋᴛᴀ ʜᴀɪ!**")

    if not context.args:
        return await update.message.reply_text("⚠️ **ᴜsᴀɢᴇ:** `/music on` ᴏʀ `/music off [reason]`")

    state = context.args[0].lower()
    
    if state == "off":
        # Check agar koi reason diya hai (e.g., /music off maintenance)
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else None
        
        await set_global_music(False, reason)
        
        if reason:
            await update.message.reply_text(f"🔴 **ᴍᴜsɪᴄ ᴅɪsᴀʙʟᴇᴅ!**\nʀᴇᴀsᴏɴ: `{reason}`")
        else:
            await update.message.reply_text("🔴 **ᴍᴜsɪᴄ ᴅɪsᴀʙʟᴇᴅ (sɪʟᴇɴᴛ ᴍᴏᴅᴇ)!**")
            
    elif state == "on":
        await set_global_music(True)
        await update.message.reply_text("🟢 **ᴍᴜsɪᴄ sʏsᴛᴇᴍ ᴇɴᴀʙʟᴇᴅ!**")
    else:
        await update.message.reply_text("⚠️ **ᴜsᴀɢᴇ:** `/music on` ᴏʀ `/music off`")

def register_handlers(app):
    app.add_handler(CommandHandler("music", music_switch))
    print("  ✅ Global Music Switch Loaded!")
  
