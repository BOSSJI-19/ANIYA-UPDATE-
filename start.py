from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import check_registered

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not check_registered(user.id):
        kb = [[InlineKeyboardButton("📝 Click to Register", callback_data=f"reg_start_{user.id}")]]
        await update.message.reply_text(f"🛑 **Hi {user.first_name}!**\nRegister first to play.\n💰 Bonus: ₹500", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"👋 **Welcome Back!**\nUse `/help` for commands.", parse_mode=ParseMode.MARKDOWN)
        
