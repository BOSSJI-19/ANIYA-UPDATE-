from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import users_col

async def user_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Top 10 Ameer Log
    top_users = users_col.find().sort("balance", -1).limit(10)
    
    msg = "🏆 **GLOBAL RICH LIST** 🏆\n\n"
    rank = 1
    
    for user in top_users:
        name = user.get("name", "Unknown")
        bal = user.get("balance", 0)
        titles = user.get("titles", [])
        
        # Decoration Logic
        icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
        
        if titles:
            # 💎 PREMIUM USER (Jiske paas Title hai)
            # Ye Blockquote (> ) use karega
            main_title = titles[0] # Pehla title dikhayenge
            msg += f"> {icon} {name} [{main_title}]\n> 💰 Balance: ₹{bal}\n\n"
        else:
            # 👤 NORMAL USER
            msg += f"{icon} {name} — ₹{bal}\n"
            
        rank += 1
        
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
  
