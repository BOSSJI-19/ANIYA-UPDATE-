import pymongo
import time
from config import MONGO_URL

# --- DATABASE CONNECTION ---
try:
    client = pymongo.MongoClient(MONGO_URL)
    db = client["CasinoBot"]
    
    # Collections
    users_col = db["users"]
    groups_col = db["groups"]
    investments_col = db["investments"]
    codes_col = db["codes"]
    keys_col = db["api_keys"]
    settings_col = db["settings"]  # <-- NEW: Economy Settings
    
    print("✅ Database Connected!")
except Exception as e:
    print(f"❌ DB Error: {e}")

# --- USER FUNCTIONS ---

def check_registered(user_id):
    """Check if user exists"""
    return users_col.find_one({"_id": user_id}) is not None

def register_user(user_id, name):
    """Register new user with Bonus & Stats"""
    if check_registered(user_id): return False
    user = {
        "_id": user_id, 
        "name": name, 
        "balance": 500,  # Bonus
        "loan": 0,
        "titles": [],
        "kills": 0,      # <-- Kill Count Start
        "protection": 0  # <-- Protection Timer
    } 
    users_col.insert_one(user)
    return True

def get_user(user_id):
    """Get full user object"""
    return users_col.find_one({"_id": user_id})

def update_balance(user_id, amount):
    """Add or subtract money"""
    users_col.update_one({"_id": user_id}, {"$inc": {"balance": amount}}, upsert=True)

def get_balance(user_id):
    """Get current balance"""
    user = users_col.find_one({"_id": user_id})
    return user["balance"] if user else 0

# --- 🔥 NEW: KILL & CRIME STATS ---

def update_kill_count(user_id):
    """Kill count badhayega"""
    users_col.update_one({"_id": user_id}, {"$inc": {"kills": 1}}, upsert=True)

# --- 🔥 NEW: PROTECTION SYSTEM ---

def set_protection(user_id, duration_hours):
    """User ko shield dega"""
    expiry = time.time() + (duration_hours * 3600)
    users_col.update_one({"_id": user_id}, {"$set": {"protection": expiry}}, upsert=True)

def is_protected(user_id):
    """Check karega shield active hai ya nahi"""
    user = users_col.find_one({"_id": user_id})
    if not user or "protection" not in user: return False
    # Agar current time expiry se kam hai, toh protected hai
    return time.time() < user["protection"]

# --- 🔥 NEW: ECONOMY & RESET ---

def get_economy_status():
    """Economy ON hai ya OFF check karega"""
    status = settings_col.find_one({"_id": "economy_status"})
    if not status: return True # Default ON
    return status["active"]

def set_economy_status(status: bool):
    """Economy ON/OFF switch"""
    settings_col.update_one({"_id": "economy_status"}, {"$set": {"active": status}}, upsert=True)

def wipe_database():
    """⚠️ DANGER: Sab delete kar dega (Reset)"""
    users_col.delete_many({})
    investments_col.delete_many({})
    # Groups, Keys aur Settings delete nahi karenge taaki setup safe rahe
    return True

# --- GROUP & MARKET FUNCTIONS ---

def update_group_activity(group_id, group_name):
    """Increase group activity score"""
    groups_col.update_one(
        {"_id": group_id},
        {"$set": {"name": group_name}, "$inc": {"activity": 1}},
        upsert=True
    )

def get_group_price(group_id):
    """Calculate Share Price based on Activity"""
    grp = groups_col.find_one({"_id": group_id})
    if not grp: return 10.0
    # Formula: Base 10 + (Score * 0.5)
    return round(10 + (grp.get("activity", 0) * 0.5), 2)

# --- API KEY MANAGEMENT FUNCTIONS ---

def add_api_key(api_key):
    """Admin se Key lekar DB me save karega"""
    if keys_col.find_one({"key": api_key}):
        return False 
    keys_col.insert_one({"key": api_key})
    return True

def remove_api_key(api_key):
    """Key delete karega"""
    result = keys_col.delete_one({"key": api_key})
    return result.deleted_count > 0

def get_all_keys():
    """Saari keys ki list return karega AI Chat ke liye"""
    keys = list(keys_col.find({}, {"_id": 0, "key": 1}))
    return [k["key"] for k in keys]
    
