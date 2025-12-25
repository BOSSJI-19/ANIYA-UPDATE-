from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode
from config import BOT_NAME, OWNER_USERNAME, SUPPORT_CHAT

# --- MAIN HELP COMMAND (/help) ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        # Agar callback se aaya hai (Back button)
        query = update.callback_query
        await query.answer()
        msg_func = query.edit_message_text
    else:
        # Agar command se aaya hai
        msg_func = update.message.reply_text

    # Fancy Text
    text = f"""
✨ <b>Welcome to {BOT_NAME} Help Menu</b> ✨

<blockquote><b>🤖 I am a Super Smart Group Manager & Music Bot.
Choose a category below to see commands!</b></blockquote>

🔘 <b>Click buttons below for details:</b>
"""

    # Buttons Layout
    buttons = [
        [
            InlineKeyboardButton("🎸 Music", callback_data="help_music"),
            InlineKeyboardButton("🎮 Games", callback_data="help_games"),
        ],
        [
            InlineKeyboardButton("👮 Admin", callback_data="help_admin"),
            InlineKeyboardButton("🛠 Tools", callback_data="help_tools"),
        ],
        [
            InlineKeyboardButton("🏦 Economy", callback_data="help_eco"),
            InlineKeyboardButton("👑 Owner", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}"),
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close_help"),
        ]
    ]

    await msg_func(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

# --- CALLBACK HANDLER (Buttons Logic) ---
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "close_help":
        await query.message.delete()
        return

    if data == "back_help":
        await help_command(update, context)
        return

    text = ""
    
    # --- MUSIC HELP ---
    if data == "help_music":
        text = """
🎸 <b>MUSIC COMMANDS</b>

<blockquote>
<b>/play</b> [Song Name] - Play song or video
<b>/stop</b> - Stop streaming
<b>/pause</b> - Pause stream
<b>/resume</b> - Resume stream
<b>/skip</b> - Skip to next song
<b>/queue</b> - Check playlist
</blockquote>
"""

    # --- GAMES HELP ---
    elif data == "help_games":
        text = """
🎮 <b>GAME CENTER</b>

<blockquote>
<b>/bet</b> [Amount] - Play Bomb Game
<b>/ttt</b> - Play Tic Tac Toe
<b>/wordseek</b> - Word Search Game
<b>/wordgrid</b> - Word Grid Puzzle
<b>/couple</b> - Check Couple of the day
<b>/love</b> - Love Calculator
</blockquote>
"""

    # --- ADMIN HELP ---
    elif data == "help_admin":
        text = """
👮 <b>ADMIN TOOLS</b>

<blockquote>
<b>/ban</b> - Ban a user
<b>/unban</b> - Unban a user
<b>/mute</b> - Mute a user
<b>/unmute</b> - Unmute a user
<b>/kick</b> - Kick a user
<b>/pin</b> - Pin a message
<b>/purge</b> - Delete messages
</blockquote>
"""

    # --- TOOLS HELP ---
    elif data == "help_tools":
        text = """
🛠 <b>UTILITIES</b>

<blockquote>
<b>/info</b> - Get User Info
<b>/id</b> - Get Chat ID
<b>/ping</b> - Check Bot Speed
<b>/stats</b> - Check Bot Stats
<b>/top</b> - Check Leaderboard
<b>/ranking</b> - Check Group Rank
</blockquote>
"""

    # --- ECONOMY HELP ---
    elif data == "help_eco":
        text = """
💰 <b>BANK & ECONOMY</b>

<blockquote>
<b>/bal</b> - Check Balance
<b>/pay</b> - Pay someone
<b>/rob</b> - Rob a user
<b>/bank</b> - Check Bank
<b>/deposit</b> - Deposit Money
<b>/withdraw</b> - Withdraw Money
<b>/shop</b> - Buy VIP Titles
</blockquote>
"""

    # Back Button
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="back_help")]]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

# --- REGISTER HANDLER (AUTO LOAD) ---
def register_handlers(app):
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_.*"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^back_help$"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^close_help$"))
    print("  ✅ Help Module Loaded with Fancy UI!")
