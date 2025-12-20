import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import json
import random

# Imports
from config import TELEGRAM_TOKEN
from database import get_game_keys, update_wordseek_score, get_wordseek_leaderboard

# GAME STATE
active_games = {}

# --- 🔥 AUTO END JOB (5 Min Timeout) ---
async def auto_end_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    
    # Check agar game abhi bhi chal raha hai
    if chat_id in active_games:
        game = active_games[chat_id]
        target_word = game['target']
        
        # Game delete karo
        del active_games[chat_id]
        
        # Message bhejo
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ **Time's Up!**\n5 minute se koi nahi khel raha tha, isliye game end kar diya.\n\n📝 Correct Word: **{target_word}**",
            parse_mode=ParseMode.MARKDOWN
        )

# --- GEMINI HELPER ---
def get_word_from_gemini():
    """Gemini se 1 Target Word lata hai (Strictly 5 Letters)"""
    keys = get_game_keys()
    if not keys: return None

    # 🔥 UPDATED PROMPT: Strictly 5 Letters
    prompt = (
        "Generate 1 random common English word (STRICTLY 5 letters long). "
        "Provide the word, its phonetic transcription, and a clear hint (definition). "
        "Output strictly in JSON format: "
        '{"word": "VIDEO", "phonetic": "/ˈvɪd.i.əʊ/", "meaning": "To record using a video camera."}'
    )

    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text: text = text.replace("```json", "").replace("```", "")
            data = json.loads(text)
            
            # 🔥 DOUBLE CHECK: Agar galti se 5 letter nahi hua to skip karo
            if len(data['word']) != 5:
                continue
                
            return data
        except: continue
    return None

# --- HELPER: GENERATE GRID ---
def generate_grid_string(target, guesses):
    target = target.upper()
    grid_msg = ""

    for guess in guesses:
        guess = guess.upper()
        row_emoji = ""
        for i, char in enumerate(guess):
            if char == target[i]:
                row_emoji += "🟩"
            elif char in target:
                row_emoji += "🟨"
            else:
                row_emoji += "🟥"
        grid_msg += f"{row_emoji} **{guess}**\n"
    return grid_msg

# --- COMMANDS ---

async def start_wordseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in active_games:
        await update.message.reply_text("⚠️ Game pehle se chal raha hai! `/end` karo ya guess karo.")
        return

    msg = await update.message.reply_text("🔄 **Loading Word Challenge...** 🧠")
    
    word_data = get_word_from_gemini()
    if not word_data:
        await msg.edit_text("❌ No Game API Keys found! Ask Admin to add keys.")
        return

    # 🔥 5 MINUTE TIMER START (300 Seconds)
    timer_job = context.job_queue.run_once(auto_end_job, 300, data=chat_id)

    active_games[chat_id] = {
        "target": word_data['word'].upper(),
        "data": word_data,
        "guesses": [],
        "message_id": msg.message_id,
        "timer_job": timer_job # Job store kiya taaki reset kar sakein
    }
    
    length = len(word_data['word'])
    hint = word_data['meaning']

    text = (
        f"🔥 **WORD GRID CHALLENGE** 🔥\n\n"
        f"🔡 Word Length: **{length} Letters**\n"
        f"👇 *Guess the word below!*\n\n"
        f"> 💡 **Hint:** {hint}"
    )
    
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)

async def stop_wordseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_games:
        # Timer stop karo
        job = active_games[chat_id].get("timer_job")
        if job: job.schedule_removal()
        
        del active_games[chat_id]
        await update.message.reply_text("🛑 **Game Ended!**")
    else:
        await update.message.reply_text("❌ Koi game nahi chal raha.")

# --- GUESS HANDLER ---
async def handle_word_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.id not in active_games: return
    
    game = active_games[chat.id]
    target = game['target']
    user_guess = update.message.text.strip().upper()
    
    # Validation
    if len(user_guess) != len(target): return

    if user_guess in game['guesses']:
        await update.message.reply_text("Someone has already guessed your word. Please try another one!", quote=True)
        return

    # 🔥 RESET TIMER ON ACTIVITY
    # Agar koi guess karta hai to timer wapis 5 min ka ho jayega
    old_job = game.get("timer_job")
    if old_job: old_job.schedule_removal()
    new_job = context.job_queue.run_once(auto_end_job, 300, data=chat.id)
    game['timer_job'] = new_job

    game['guesses'].append(user_guess)
    
    # WIN SCENARIO
    if user_guess == target:
        user = update.effective_user
        points = 9
        update_wordseek_score(user.id, user.first_name, points, str(chat.id))
        
        # Stop Timer
        if new_job: new_job.schedule_removal()
        
        data = game['data']
        del active_games[chat.id]
        
        await update.message.reply_text(
            f"🚬 ~ ` {user.first_name} ` ~ 🍷\n"
            f"{user_guess.title()}\n\n"
            f"Congrats! You guessed it correctly.\n"
            f"Added {points} to the leaderboard.\n"
            f"Start with /new\n\n"
            f"> **Correct Word:** {data['word']}\n"
            f"> **{data['word']}** {data.get('phonetic', '')}\n"
            f"> **Meaning:** {data['meaning']}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # WRONG GUESS - UPDATE GRID
        try:
            grid_text = generate_grid_string(target, game['guesses'])
            hint = game['data']['meaning']
            
            new_text = (
                f"🔥 **WORD GRID CHALLENGE** 🔥\n\n"
                f"{grid_text}\n"
                f"> 💡 **Hint:** {hint}"
            )
            
            await context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=game['message_id'],
                text=new_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception: pass

# --- LEADERBOARD ---
async def wordseek_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🌍 Global Top", callback_data="wrank_global"), InlineKeyboardButton("👥 Group Top", callback_data="wrank_group")]]
    await update.message.reply_text("🏆 **WordSeek Leaderboard**\nSelect Category 👇", reply_markup=InlineKeyboardMarkup(kb))

async def wordseek_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    
    if data.startswith("wrank_"):
        mode = data.split("_")[1]
        group_id = str(update.effective_chat.id) if mode == "group" else None
        
        leaderboard = get_wordseek_leaderboard(group_id)
        title = "🌍 Global" if mode == "global" else "👥 Group"
        msg = f"🏆 **{title} Leaderboard** 🏆\n\n"
        
        if not leaderboard: msg += "❌ No Data Found!"
        else:
            for i, p in enumerate(leaderboard, 1):
                score = p.get('global_score', 0) if mode == "global" else p.get('group_scores', {}).get(group_id, 0)
                msg += f"{i}. {p['name']} - 💎 {score}\n"
        
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="close_wrank")]]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    if data == "close_wrank": await q.message.delete()
