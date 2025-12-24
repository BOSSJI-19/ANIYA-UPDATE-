import os

# ⚙️ TELEGRAM CONFIG
# Ye values Render ke "Environment" tab se aayengi
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") 
MONGO_URL = os.getenv("MONGO_URL")

# 👑 OWNERS
# Owner ID ko bhi .env se le sakte ho ya yahan hardcode kar sakte ho
OWNER_ID = int(os.getenv("OWNER_ID", "7453179290")) 
OWNER_IDS = [7453179290, 6356015122]  

# 📝 LOGGING
LOGGER_ID = -1003639584506 

# 🤖 BOT INFO
BOT_NAME = "ㅤ𝚲𝛈𝛊𝛄𝛂me "
OWNER_USERNAME = "@THE_BOSS_JI"
OWNER_NAME = "BOSS JI"

# 🔥 MUSIC BOT CONFIG (From Environment)
# int() lagaya hai kyunki API_ID number hona chahiye
API_ID = int(os.getenv("API_ID", "0")) 
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

# 🎮 GAME SETTINGS
GRID_SIZE = 4
MAX_LOAN = 5000
LOAN_INTEREST = 0.10
DELETE_TIMER = 17 

# 🏆 IMAGES
DEFAULT_BANNER = "https://i.ibb.co/vzDpQx9/ranking-banner.jpg"

