import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import get_top_chatters, get_total_messages

# --- PROGRESS BAR GENERATOR ---
def make_bar(count, max_count):
    if max_count == 0: return "▱▱▱▱▱▱▱▱▱▱"
    percentage = count / max_count
    filled = int(percentage * 10) 
    if filled > 10: filled = 10
    empty = 10 - filled
    return "▰" * filled + "▱" * empty

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        chat_id = update.effective_chat.id
    else:
        chat_id = update.effective_chat.id

    mode = "overall"
    if context.args and context.args[0] in ["today", "week"]:
        mode = context.args[0]

    await send_rank_message(chat_id, mode, update, context)

async def send_rank_message(chat_id, mode, update, context):
    data = get_top_chatters(chat_id, mode)
    total = get_total_messages(chat_id)
    
    title_map = {
        "overall": "☁️ OVERALL LEADERBOARD",
        "today": "☀️ TODAY'S TOP CHATTERS",
        "week": "🗓 WEEKLY TOP CHATTERS"
    }

    # 1. HEADER (Title Block)
    text = f"<blockquote><b>📈 {title_map[mode]}</b></blockquote>\n\n"
    
    # 2. BODY (List Block)
    body_text = ""
    if not data:
        body_text += "❌ <b>No data found yet!</b>\nStart chatting to appear here."
    else:
        max_count = data[0].get(mode, 1)
        for i, user in enumerate(data, 1):
            # Name ko safe karo (HTML tags issue na karein)
            name = html.escape(user.get("name", "Unknown"))
            count = user.get(mode, 0)
            bar = make_bar(count, max_count)
            
            if i == 1: icon = "🥇"
            elif i == 2: icon = "🥈"
            elif i == 3: icon = "🥉"
            else: icon = f"{i}."
            
            # HTML Formatting
            body_text += f"{icon} 👤 <b>{name}</b>\n"
            body_text += f"   └ {bar} • <code>{count}</code>\n\n"
    
    # Body ko Blockquote me daalo
    text += f"<blockquote>{body_text}</blockquote>\n"
    
    # 3. FOOTER
    text += f"📨 <b>Total Group Messages:</b> <code>{total}</code>"
    
    kb = [
        [
            InlineKeyboardButton("Overall", callback_data="rank_overall"),
            InlineKeyboardButton("Today", callback_data="rank_today"),
            InlineKeyboardButton("Week", callback_data="rank_week")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="hide_rank")]
    ]
    
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.HTML  # 🔥 HTML Mode Zaroori Hai
            )
        except: pass 
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML  # 🔥 HTML Mode Zaroori Hai
        )

# --- CALLBACK HANDLER ---
async def rank_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    
    if data == "hide_rank":
        try:
            await q.answer("Closing...")
            await q.message.delete()
        except: pass
        return

    if data.startswith("rank_"):
        try: await q.answer()
        except: pass
        mode = data.split("_")[1]
        await send_rank_message(update.effective_chat.id, mode, update, context)
