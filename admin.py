from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import users_col, codes_col, update_balance

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    msg = " ".join(context.args)
    for u in users_col.find({}):
        try: await context.bot.send_message(u["_id"], f"📢 **NOTICE**\n{msg}", parse_mode=ParseMode.MARKDOWN)
        except: pass
    await update.message.reply_text("✅ Broadcast Sent")

async def create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        codes_col.insert_one({"code": context.args[0], "amount": int(context.args[1]), "limit": int(context.args[2]), "redeemed_by": []})
        await update.message.reply_text("✅ Code Created")
    except: pass

async def add_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: update_balance(int(context.args[0]), int(context.args[1])); await update.message.reply_text("✅ Added")
    except: pass

async def take_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: update_balance(int(context.args[0]), -int(context.args[1])); await update.message.reply_text("✅ Taken")
    except: pass
      
