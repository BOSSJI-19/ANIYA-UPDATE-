import time
import random
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import (
    update_balance, get_balance, get_user, 
    set_protection, is_protected, get_economy_status, 
    update_kill_count # <-- Ye zaroori hai
)

# --- ECONOMY CONFIGS ---
PROTECT_COST = 5000   # 1 Day protection
KILL_COST = 20000     # Kill karne ka kharcha
ROB_FAIL_PENALTY = 500 # Chori pakde jaane par fine

# --- 1. PAY (Transfer Money) ---
async def pay_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return await update.message.reply_text("🔴 **Economy is OFF!**")
    
    sender = update.effective_user
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply karke likho: `/pay 100`")
    
    receiver = update.message.reply_to_message.from_user
    if sender.id == receiver.id: return await update.message.reply_text("❌ Khud ko nahi bhej sakte!")
    if receiver.is_bot: return await update.message.reply_text("❌ Bot ko paisa doge?")

    try: amount = int(context.args[0])
    except: return await update.message.reply_text("⚠️ Usage: `/pay 100`")
    
    if amount <= 0: return await update.message.reply_text("❌ Sahi amount daal!")
    if get_balance(sender.id) < amount: return await update.message.reply_text("❌ Paisa nahi hai tere paas!")
    
    update_balance(sender.id, -amount)
    update_balance(receiver.id, amount)
    
    await update.message.reply_text(f"💸 **Transfer Successful!**\n👤 {sender.first_name} sent ₹{amount} to {receiver.first_name}.")

# --- 2. PROTECT (Shield) ---
async def protect_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return await update.message.reply_text("🔴 Economy OFF.")
    user = update.effective_user
    
    if get_balance(user.id) < PROTECT_COST:
        return await update.message.reply_text(f"❌ Protection ke liye ₹{PROTECT_COST} chahiye!")
        
    if is_protected(user.id):
        return await update.message.reply_text("🛡️ Tu pehle se Protected hai!")
    
    update_balance(user.id, -PROTECT_COST)
    set_protection(user.id, 24) # 24 Hours
    
    await update.message.reply_text(f"🛡️ **Shield Activated!**\n₹{PROTECT_COST} kate. Ab 24 ghante tak koi Rob/Kill nahi kar payega.")

# --- 3. ROB (Chori) ---
async def rob_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return await update.message.reply_text("🔴 Economy OFF.")
    
    thief = update.effective_user
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Kisko lootna hai? Reply command on message.")
    
    victim = update.message.reply_to_message.from_user
    if thief.id == victim.id: return
    
    # Checks
    if is_protected(victim.id):
        return await update.message.reply_text(f"🛡️ **Fail!** {victim.first_name} ne Protection le rakhi hai!")
    
    victim_bal = get_balance(victim.id)
    if victim_bal < 100:
        return await update.message.reply_text("❌ Is bhikari ke paas kuch nahi hai!")

    # Luck System (40% Chance Pass)
    if random.random() < 0.4:
        # Success
        loot = int(victim_bal * random.uniform(0.1, 0.4)) # 10% se 40% loote ga
        update_balance(victim.id, -loot)
        update_balance(thief.id, loot)
        await update.message.reply_text(f"🔫 **ROBBERY SUCCESS!**\nTune {victim.first_name} ke ₹{loot} uda liye! 🏃‍♂️💨")
    else:
        # Fail & Penalty
        update_balance(thief.id, -ROB_FAIL_PENALTY)
        await update.message.reply_text(f"👮 **POLICE AA GAYI!**\nChori pakdi gayi. Fine: ₹{ROB_FAIL_PENALTY}")

# --- 4. KILL (Supari + Reward) ---
async def kill_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_economy_status(): return await update.message.reply_text("🔴 Economy OFF.")
    
    killer = update.effective_user
    if not update.message.reply_to_message: return await update.message.reply_text("⚠️ Reply karke `/kill` likho.")
    
    victim = update.message.reply_to_message.from_user
    if killer.id == victim.id: return await update.message.reply_text("❌ Khud ko kyu maar raha hai?")
    
    # 1. Cost Check
    if get_balance(killer.id) < KILL_COST:
        return await update.message.reply_text(f"❌ Supari dene ke liye ₹{KILL_COST} chahiye!")
        
    # 2. Protection Check
    if is_protected(victim.id):
        return await update.message.reply_text(f"🛡️ **Mission Fail!** {victim.first_name} protected hai.")

    # 3. Transaction Logic
    # Killer pays cost first
    update_balance(killer.id, -KILL_COST)
    
    # Victim loses 50%
    victim_bal = get_balance(victim.id)
    loss = int(victim_bal * 0.5) 
    update_balance(victim.id, -loss)
    
    # 🔥 REWARD: Killer gets 50% of the loot (Profit)
    bounty = int(loss * 0.5)
    update_balance(killer.id, bounty)
    
    # 🔥 UPDATE KILL COUNT (Leaderboard ke liye)
    update_kill_count(killer.id)
    
    await update.message.reply_text(
        f"💀 **KILL CONFIRMED!**\n"
        f"🔪 **Killer:** {killer.first_name}\n"
        f"🩸 **Victim:** {victim.first_name} (Lost ₹{loss})\n"
        f"💰 **Bounty Earned:** ₹{bounty}\n"
        f"📈 **Stats:** +1 Kill Added!"
    )

# --- 5. ALIVE / STATUS ---
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    status = "🛡️ **PROTECTED**" if is_protected(user.id) else "⚠️ **VULNERABLE**"
    bal = get_balance(user.id)
    await update.message.reply_text(f"👤 **STATUS REPORT:**\n\n💰 Money: ₹{bal}\n🔰 Shield: {status}", parse_mode=ParseMode.MARKDOWN)
