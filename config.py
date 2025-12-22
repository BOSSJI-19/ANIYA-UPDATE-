import os

# ⚙️ CONFIGURATION
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") 
MONGO_URL = os.getenv("MONGO_URL")
OWNER_ID = 6356015122  # Tumhara (Owner) Telegram ID

# 🔥 MUSIC BOT CONFIG (Assistant)
# Ye teeno .env file se aayenge
API_ID = int(os.getenv("API_ID", "0")) # Integer hona zaroori hai
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# 🤖 AI CHAT CONFIG
OWNER_NAME = "ᯓ𓂃❛ 𝐒 𝛖 𝐝 ֟፝ᥱ 𝛆 𝛒 </𝟑 𝁘ໍ𝀛𓂃🍷"  # Yuki tumhe is naam se bulayegi

# 🎮 GAME SETTINGS
GRID_SIZE = 4
MAX_LOAN = 5000
LOAN_INTEREST = 0.10
DELETE_TIMER = 17  # Result message kitne seconds baad delete hoga

# 🏆 RANKING IMAGE
DEFAULT_BANNER = "https://i.ibb.co/vzDpQx9/ranking-banner.jpg"
