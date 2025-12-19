import os

# ⚙️ CONFIGURATION
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") 
MONGO_URL = os.getenv("MONGO_URL")
OWNER_ID = 6356015122  # Apna ID daal

# Game Settings
GRID_SIZE = 4
MAX_LOAN = 5000
LOAN_INTEREST = 0.10
DELETE_TIMER = 30  # Auto-delete seconds

# Image for Group Ranking Default
DEFAULT_BANNER = "https://i.ibb.co/vzDpQx9/ranking-banner.jpg"
