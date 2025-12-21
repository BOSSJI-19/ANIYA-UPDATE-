import time
import random
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import (
    update_balance, get_balance, get_user, 
    set_protection, is_protected, get_economy_status, 
    update_kill_count, set_dead, is_dead,
    check_registered, register_user
)

# --- ECONOMY CONFIGS ---
PROTECT_COST = 5000   
HOSPITAL_FEE = 5000   
ROB_FAIL_PENALTY = 500 
KILL_REWARD = 900     
AUTO_REVIVE_TIME = 1800 

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- HELPER: REGISTER BUTTON ---
async def send_register_button(update):
    user = update.effective_user
    kb = [[InlineKeyboardButton("📝 Register Now", callback_data=f"reg_start_{user.id}")]]
    await update.message.reply_text(
        f"🛑 <b>{user.first_name}, Register First!</b>\nRegistration is required to play the game.",
        reply_markup=InlineKeyboardMarkup(kb),
        quote=True,
        parse_mode=ParseMode.HTML
    )

# --- 🔥 AUTO REVIVE JOB ---
async def auto_revive_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = context.job.data
        if is_dead(user_id):
            set_dead(user_id, False) 
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="✨ <b>Miracle!</b>\nYou have been automatically <b>Revived</b>! 🧘‍♂️",
                    parse_mode=ParseMode.HTML
                )
            except: pass
    except Exception as e:
        print(f"❌ Auto Revive Error: {e}")

# --- 1. PAY (Transfer Money) ---
async def pay_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return await update.message.reply_text("🔴 <b>Economy is OFF!</b>", parse_mode=ParseMode.HTML)
    sender = update.effective_user
    
    if not check_registered(sender.id):
        await send_register_button(update)
        return

    if is_dead(sender.id): 
        return await update.message.reply_text("👻 <b>Ghosts cannot use the bank!</b> Revive first.", parse_mode=ParseMode.HTML)

    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ <b>Usage:</b> Reply to a user with <code>/pay 100</code>", parse_mode=ParseMode.HTML)
    
    receiver = update.message.reply_to_message.from_user
    if receiver.is_bot or sender.id == receiver.id:
        return await update.message.reply_text("❌ Invalid transaction target!")

    if not check_registered(receiver.id):
        return await update.message.reply_text(f"❌ <b>Fail!</b> {receiver.first_name} is not registered.", parse_mode=ParseMode.HTML)

    try: 
        amount = int(context.args[0])
        if amount <= 0: raise ValueError
    except: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/pay 100</code>", parse_mode=ParseMode.HTML)
    
    if get_balance(sender.id) < amount: 
        return await update.message.reply_text("❌ Insufficient funds!")
    
    update_balance(sender.id, -amount)
    update_balance(receiver.id, amount)
    
    msg = f"""
<blockquote><b>💸 {to_fancy("TRANSFER SUCCESS")}</b></blockquote>
<blockquote>
<b>👤 From:</b> {html.escape(sender.first_name)}
<b>👤 To:</b> {html.escape(receiver.first_name)}
<b>💰 Amount:</b> ₹{amount}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. PROTECT (Shield) ---
async def protect_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    user = update.effective_user
    
    if not check_registered(user.id):
        await send_register_button(update)
        return
    
    if is_dead(user.id): return await update.message.reply_text("👻 Dead bodies cannot buy protection.")

    if get_balance(user.id) < PROTECT_COST:
        return await update.message.reply_text(f"❌ You need ₹{PROTECT_COST} for protection!")
        
    if is_protected(user.id):
        return await update.message.reply_text("🛡️ You are already Protected!")
    
    update_balance(user.id, -PROTECT_COST)
    set_protection(user.id, 24) 
    
    msg = f"""
<blockquote><b>🛡️ {to_fancy("SHIELD ACTIVATED")}</b></blockquote>
<blockquote>
<b>👤 User:</b> {html.escape(user.first_name)}
<b>⏳ Time:</b> 24 Hours
<b>💸 Cost:</b> ₹{PROTECT_COST}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 3. ROB (Chori) ---
async def rob_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    thief = update.effective_user
    
    if not check_registered(thief.id):
        await send_register_button(update)
        return

    if is_dead(thief.id): return await update.message.reply_text("👻 Ghosts cannot rob!")

    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply with <code>/rob</code>.", parse_mode=ParseMode.HTML)
    
    victim = update.message.reply_to_message.from_user
    if not victim or victim.is_bot or thief.id == victim.id:
        return await update.message.reply_text("👮 <b>Invalid Target!</b>", parse_mode=ParseMode.HTML)
    
    if not check_registered(victim.id):
        return await update.message.reply_text(f"⚠️ {victim.first_name} is not registered.")

    if is_dead(victim.id): return await update.message.reply_text("☠️ Cannot loot a dead body!")
    if is_protected(victim.id): return await update.message.reply_text("🛡️ Target is Protected!")
    
    victim_bal = get_balance(victim.id)
    if victim_bal < 100: return await update.message.reply_text("❌ Target has nothing to steal.")

    if random.random() < 0.4:
        loot = int(victim_bal * random.uniform(0.1, 0.4)) 
        update_balance(victim.id, -loot)
        update_balance(thief.id, loot)
        
        msg = f"""
<blockquote><b>🔫 {to_fancy("ROBBERY SUCCESS")}</b></blockquote>
<blockquote>
<b>🦹 Robber:</b> {html.escape(thief.first_name)}
<b>🤕 Victim:</b> {html.escape(victim.first_name)}
<b>💰 Stolen:</b> ₹{loot}
</blockquote>
"""
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    else:
        update_balance(thief.id, -ROB_FAIL_PENALTY)
        msg = f"""
<blockquote><b>👮 {to_fancy("CAUGHT BY POLICE")}</b></blockquote>
<blockquote>
<b>🦹 Robber:</b> {html.escape(thief.first_name)}
<b>🚫 Status:</b> Failed
<b>💸 Fine:</b> ₹{ROB_FAIL_PENALTY}
</blockquote>
"""
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 4. KILL (Murder) ---
async def kill_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    killer = update.effective_user
    
    if not check_registered(killer.id):
        await send_register_button(update)
        return

    if is_dead(killer.id): return await update.message.reply_text("👻 <b>You are dead!</b>", parse_mode=ParseMode.HTML)
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply with <code>/kill</code>.", parse_mode=ParseMode.HTML)
    
    victim = update.message.reply_to_message.from_user
    if not victim or victim.is_bot or killer.id == victim.id:
        return await update.message.reply_text("❌ Invalid Target!")
    
    if not check_registered(victim.id):
        register_user(victim.id, victim.first_name)
    
    if is_dead(victim.id): return await update.message.reply_text("☠️ Already Dead!")
    if is_protected(victim.id): return await update.message.reply_text("🛡️ Target is Protected.")

    try:
        victim_bal = get_balance(victim.id)
        if victim_bal > 0:
            loss = int(victim_bal * 0.5)
            update_balance(victim.id, -loss)
        
        update_balance(killer.id, KILL_REWARD)
        set_dead(victim.id, True)
        update_kill_count(killer.id)
        
        if context.job_queue:
            context.job_queue.run_once(auto_revive_job, AUTO_REVIVE_TIME, data=victim.id)
        
        kb = [[InlineKeyboardButton(f"🏥 Instant Revive (₹{HOSPITAL_FEE})", callback_data=f"revive_{victim.id}")]]
        
        msg = f"""
<blockquote><b>💀 {to_fancy("MURDER ALERT")}</b></blockquote>
<blockquote>
<b>🔪 Killer:</b> {html.escape(killer.first_name)}
<b>🩸 Victim:</b> {html.escape(victim.first_name)} (DEAD)
<b>💰 Reward:</b> ₹{KILL_REWARD}
</blockquote>
"""
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"❌ Kill Error: {e}")

# --- 5. REVIVE HANDLER ---
async def revive_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = q.from_user
    target_id = int(q.data.split("_")[1])
    
    if user.id != target_id:
        return await q.answer("This is not your body!", show_alert=True)
        
    if not is_dead(user.id): return await q.answer("You are already alive!", show_alert=True)
        
    if get_balance(user.id) < HOSPITAL_FEE:
        return await q.answer(f"❌ Fee: ₹{HOSPITAL_FEE}", show_alert=True)
        
    update_balance(user.id, -HOSPITAL_FEE)
    set_dead(user.id, False)
    await q.edit_message_text(f"🏥 <b>REVIVED!</b> {user.first_name} is back to life! 💸 Paid: ₹{HOSPITAL_FEE}", parse_mode=ParseMode.HTML)

# --- 6. ALIVE / STATUS ---
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not check_registered(user.id): return
    
    status = "☠️ <b>DEAD</b>" if is_dead(user.id) else ("🛡️ <b>PROTECTED</b>" if is_protected(user.id) else "⚠️ <b>VULNERABLE</b>")
    user_data = get_user(user.id)
    kills = user_data.get("kills", 0)
    
    msg = f"""
<blockquote><b>👤 {to_fancy("PLAYER STATUS")}</b></blockquote>
<blockquote>
<b>❤️ Condition:</b> {status}
<b>💰 Money:</b> ₹{get_balance(user.id)}
<b>🎯 Kills:</b> {kills}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
