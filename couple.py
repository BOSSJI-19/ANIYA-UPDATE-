import os
import random
import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import users_col

# --- CONFIGURATION (ADJUST THESE) ---
BG_IMAGE = "ccpic.png"  # Aapka Background Image Name
FONT_PATH = "arial.ttf" # Koi bhi font file (optional)

# Coordinates (X, Y) - Isko image ke hisab se adjust karein
# (Left Circle ka Top-Left Corner, Right Circle ka Top-Left Corner)
POS_1 = (77, 205)   
POS_2 = (567, 205)
CIRCLE_SIZE = 300   # Circle kitna bada katna hai

def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- IMAGE GENERATOR ---
async def make_couple_img(user1, user2, app):
    # 1. Load Background
    try:
        bg = Image.open(BG_IMAGE).convert("RGBA")
    except:
        return None # Agar image nahi mili

    # 2. Function to fetch & circle crop PFP
    async def get_pfp(u_id):
        try:
            # Telegram se photo nikalo
            photos = await app.bot.get_profile_photos(u_id, limit=1)
            if photos.total_count > 0:
                file = await app.bot.get_file(photos.photos[0][-1].file_id)
                f_data = await file.download_as_bytearray()
                img = Image.open(io.BytesIO(f_data)).convert("RGBA")
            else:
                # No PFP? Create dummy
                img = Image.new('RGBA', (300, 300), (200, 200, 200))
            
            # Crop to Circle
            mask = Image.new('L', (CIRCLE_SIZE, CIRCLE_SIZE), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, CIRCLE_SIZE, CIRCLE_SIZE), fill=255)
            
            img = ImageOps.fit(img, (CIRCLE_SIZE, CIRCLE_SIZE), centering=(0.5, 0.5))
            img.putalpha(mask)
            return img
        except:
            return Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (100, 100, 100))

    # 3. Process Both Images
    pfp1 = await get_pfp(user1['id'])
    pfp2 = await get_pfp(user2['id'])

    # 4. Paste on Background
    bg.paste(pfp1, POS_1, pfp1)
    bg.paste(pfp2, POS_2, pfp2)

    # 5. Add Text (Names in Blue)
    draw = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype(FONT_PATH, 40)
    except:
        font = ImageFont.load_default()

    # Calculate Text Positions (Center below circle)
    # Name 1
    name1 = user1['first_name'][:12] # Limit name length
    bbox1 = draw.textbbox((0, 0), name1, font=font)
    w1 = bbox1[2] - bbox1[0]
    x1 = POS_1[0] + (CIRCLE_SIZE - w1) // 2
    y1 = POS_1[1] + CIRCLE_SIZE + 20
    draw.text((x1, y1), name1, font=font, fill=(0, 123, 255)) # Blue Color

    # Name 2
    name2 = user2['first_name'][:12]
    bbox2 = draw.textbbox((0, 0), name2, font=font)
    w2 = bbox2[2] - bbox2[0]
    x2 = POS_2[0] + (CIRCLE_SIZE - w2) // 2
    y2 = POS_2[1] + CIRCLE_SIZE + 20
    draw.text((x2, y2), name2, font=font, fill=(0, 123, 255)) # Blue Color

    # 6. Save to Bytes
    bio = io.BytesIO()
    bio.name = "couple.png"
    bg.save(bio, "PNG")
    bio.seek(0)
    return bio

# --- COUPLE COMMAND ---
async def couple_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    # 1. Fetch 2 Random Users from DB
    try:
        pipeline = [{"$sample": {"size": 2}}]
        random_users = list(users_col.aggregate(pipeline))
        
        if len(random_users) < 2:
            return await update.message.reply_text("❌ Not enough users in database to pick a couple!")
            
        u1 = random_users[0]
        u2 = random_users[1]
        
        # Prepare Data for Image
        user1_data = {'id': u1['_id'], 'first_name': u1.get('name', 'User 1')}
        user2_data = {'id': u2['_id'], 'first_name': u2.get('name', 'User 2')}
        
    except Exception as e:
        print(e)
        return await update.message.reply_text("❌ Error picking users.")

    msg = await update.message.reply_text("🔍 **Finding a perfect match...**", parse_mode=ParseMode.MARKDOWN)

    # 2. Generate Image
    photo = await make_couple_img(user1_data, user2_data, context.application)
    
    if not photo:
        await msg.edit_text("❌ Error: `ccpic.png` not found! Check bot logs.")
        return

    # 3. Send Message
    caption = f"""
<blockquote><b>💘 {to_fancy("TODAY'S COUPLE")}</b></blockquote>

<blockquote>
<b>🤵 ʙᴏʏ :</b> {user1_data['first_name']}
<b>👰 ɢɪʀʟ :</b> {user2_data['first_name']}
</blockquote>

<blockquote>
<b>✨ ᴍᴀᴛᴄʜ :</b> 100% ❤️
<b>📅 ᴅᴀᴛᴇ :</b> {to_fancy("FOREVER")}
</blockquote>
"""
    # Support Button
    kb = [[InlineKeyboardButton("👨‍💻 Support", url="https://t.me/YOUR_SUPPORT_CHANNEL")]] # Apna Link Dalena
    
    await update.message.reply_photo(
        photo=photo,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML
    )
    await msg.delete()
