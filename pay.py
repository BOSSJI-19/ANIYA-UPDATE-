import time
import random
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

# --- HELPER: REGISTER BUTTON ---
async def send_register_button(update):
    user = update.effective_user
    kb = [[InlineKeyboardButton("📝 Register Now", callback_data=f"reg_start_{user.id}")]]
    await update.message.reply_text(
        f"🛑 **{user.first_name}, Register First!**\nGame khelne ke liye register karna zaroori hai.",
        reply_markup=InlineKeyboardMarkup(kb),
        quote=True
    )

# --- 🔥 AUTO REVIVE JOB (Background Task) ---
async def auto_revive_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = context.job.data
        if is_dead(user_id):
            set_dead(user_id, False) 
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="✨ **Miracle!**\nTum automatically **Zinda** ho gaye ho! 🧘‍♂️",
                    parse_mode=ParseMode.MARKDOWN
                )
            except: pass
    except Exception as e:
        print(f"❌ Auto Revive Error: {e}")

# --- 1. PAY (Transfer Money) ---
async def pay_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return await update.message.reply_text("🔴 **Economy is OFF!**")
    sender = update.effective_user
    
    if not check_registered(sender.id):
        await send_register_button(update)
        return

    if is_dead(sender.id): 
        return await update.message.reply_text("👻 **Bhoot bank nahi ja sakte!** Pehle revive ho jao.")

    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ **Usage:** Reply to a user with `/pay 100`")
    
    receiver = update.message.reply_to_message.from_user
    if receiver.is_bot or sender.id == receiver.id:
        return await update.message.reply_text("❌ Galat bande ko paise bhej rahe ho!")

    if not check_registered(receiver.id):
        return await update.message.reply_text(f"❌ **Fail!** {receiver.first_name} registered nahi hai.")

    try: 
        amount = int(context.args[0])
        if amount <= 0: raise ValueError
    except: 
        return await update.message.reply_text("⚠️ **Usage:** `/pay 100` (Sahi amount likho)")
    
    if get_balance(sender.id) < amount: 
        return await update.message.reply_text("❌ Jeb khali hai teri!")
    
    update_balance(sender.id, -amount)
    update_balance(receiver.id, amount)
    
    await update.message.reply_text(f"💸 **Transfer Successful!**\n👤 {sender.first_name} sent ₹{amount} to {receiver.first_name}.")

# --- 2. PROTECT (Shield) ---
async def protect_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    user = update.effective_user
    
    if not check_registered(user.id):
        await send_register_button(update)
        return
    
    if is_dead(user.id): return await update.message.reply_text("👻 Dead body ko shield nahi milti.")

    if get_balance(user.id) < PROTECT_COST:
        return await update.message.reply_text(f"❌ Protection ke liye ₹{PROTECT_COST} chahiye!")
        
    if is_protected(user.id):
        return await update.message.reply_text("🛡️ Tu pehle se Protected hai!")
    
    update_balance(user.id, -PROTECT_COST)
    set_protection(user.id, 24) 
    await update.message.reply_text(f"🛡️ **Shield Activated!**\n₹{PROTECT_COST} kate. Ab koi Rob/Kill nahi kar payega.")

# --- 3. ROB (Chori) ---
async def rob_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    thief = update.effective_user
    
    if not check_registered(thief.id):
        await send_register_button(update)
        return

    if is_dead(thief.id): return await update.message.reply_text("👻 Bhoot chori nahi kar sakte!")

    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply karke `/rob` likho.")
    
    victim = update.message.reply_to_message.from_user
    if not victim or victim.is_bot or thief.id == victim.id:
        return await update.message.reply_text("👮 **Invalid Target!**")
    
    if not check_registered(victim.id):
        return await update.message.reply_text(f"⚠️ {victim.first_name} registered nahi hai.")

    if is_dead(victim.id): return await update.message.reply_text("☠️ Laash se kya lootega?")
    if is_protected(victim.id): return await update.message.reply_text("🛡️ Target Protected hai!")
    
    victim_bal = get_balance(victim.id)
    if victim_bal < 100: return await update.message.reply_text("❌ Iske paas kuch nahi hai.")

    if random.random() < 0.4:
        loot = int(victim_bal * random.uniform(0.1, 0.4)) 
        update_balance(victim.id, -loot)
        update_balance(thief.id, loot)
        await update.message.reply_text(f"🔫 **SUCCESS!** Tune ₹{loot} uda liye! 🏃‍♂️💨")
    else:
        update_balance(thief.id, -ROB_FAIL_PENALTY)
        await update.message.reply_text(f"👮 **CAUGHT!** Chori pakdi gayi. Fine: ₹{ROB_FAIL_PENALTY}")

# --- 4. KILL (Murder) ---
async def kill_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return
    killer = update.effective_user
    
    if not check_registered(killer.id):
        await send_register_button(update)
        return

    if is_dead(killer.id): return await update.message.reply_text("👻 **Tu khud dead hai!**")
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply karke `/kill` likho.")
    
    victim = update.message.reply_to_message.from_user
    if not victim or victim.is_bot or killer.id == victim.id:
        return await update.message.reply_text("❌ System Amar hai!")
    
    if not check_registered(victim.id):
        register_user(victim.id, victim.first_name)
    
    if is_dead(victim.id): return await update.message.reply_text("☠️ Already Dead!")
    if is_protected(victim.id): return await update.message.reply_text("🛡️ Protected hai.")

    # Kill Logic
    try:
        victim_bal = get_balance(victim.id)
        if victim_bal > 0:
            loss = int(victim_bal * 0.5)
            update_balance(victim.id, -loss)
        
        update_balance(killer.id, KILL_REWARD)
        set_dead(victim.id, True)
        update_kill_count(killer.id)
        
        # 🔥 JobQueue Timer
        if context.job_queue:
            context.job_queue.run_once(auto_revive_job, AUTO_REVIVE_TIME, data=victim.id)
        
        kb = [[InlineKeyboardButton(f"🏥 Instant Revive (₹{HOSPITAL_FEE})", callback_data=f"revive_{victim.id}")]]
        await update.message.reply_text(
            f"💀 **MURDER!**\n🔪 **Killer:** {killer.first_name}\n🩸 **Victim:** {victim.first_name} (DEAD)\n💰 Reward: ₹{KILL_REWARD}",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    except Exception as e:
        print(f"❌ Kill Error: {e}")

# --- 5. REVIVE HANDLER ---
async def revive_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = q.from_user
    target_id = int(q.data.split("_")[1])
    
    if user.id != target_id:
        return await q.answer("Ye tumhari laash nahi hai!", show_alert=True)
        
    if not is_dead(user.id): return await q.answer("Zinda ho bhai!", show_alert=True)
        
    if get_balance(user.id) < HOSPITAL_FEE:
        return await q.answer(f"❌ Fees: ₹{HOSPITAL_FEE}", show_alert=True)
        
    update_balance(user.id, -HOSPITAL_FEE)
    set_dead(user.id, False)
    await q.edit_message_text(f"🏥 **REVIVED!** {user.first_name} zinda ho gaya! 💸 Paid: ₹{HOSPITAL_FEE}")

# --- 6. ALIVE / STATUS ---
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not check_registered(user.id): return
    
    status = "☠️ **DEAD**" if is_dead(user.id) else ("🛡️ **PROTECTED**" if is_protected(user.id) else "⚠️ **VULNERABLE**")
    user_data = get_user(user.id)
    kills = user_data.get("kills", 0)
    
    await update.message.reply_text(f"👤 **{user.first_name} Status:**\n\n❤️ Condition: {status}\n💰 Money: ₹{get_balance(user.id)}\n🎯 Kills: {kills}", parse_mode=ParseMode.MARKDOWN)
