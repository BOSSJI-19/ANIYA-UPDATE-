import os
import random
import io
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageOps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
# 🔥 Import Users Collection
from database import users_col

# --- CONFIGURATION ---
BG_IMAGE = "ccpic.png" 
FONT_PATH = "arial.ttf" 

# Coordinates (Left & Right Circles)
POS_1 = (165, 205)   
POS_2 = (660, 205)
CIRCLE_SIZE = 360    

def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- IMAGE GENERATOR ---
async def make_couple_img(user1, user2, context):
    print("🎨 Generating Image...") # Debug Log
    try:
        bg = Image.open(BG_IMAGE).convert("RGBA")
    except Exception as e:
        print(f"❌ Error Opening ccpic.png: {e}")
        return None 

    # Helper: Circular PFP
    async def get_pfp(u_id, name):
        try:
            # 1. Try Fetching PFP from Telegram
            photos = await context.bot.get_profile_photos(u_id, limit=1)
            
            if photos.total_count > 0:
                file = await context.bot.get_file(photos.photos[0][-1].file_id)
                f_data = await file.download_as_bytearray()
                img = Image.open(io.BytesIO(f_data)).convert("RGBA")
            else:
                raise Exception("No PFP Found") # Force Fallback

            # Resize High Quality
            img = ImageOps.fit(img, (CIRCLE_SIZE, CIRCLE_SIZE), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

            # Mask Logic
            mask = Image.new('L', (CIRCLE_SIZE, CIRCLE_SIZE), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, CIRCLE_SIZE, CIRCLE_SIZE), fill=255)

            result = Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (0, 0, 0, 0))
            result.paste(img, (0, 0), mask=mask)
            return result
            
        except Exception as e:
            # 2. Fallback (Agar Photo na mile to Initials wala Circle banayega)
            print(f"⚠️ PFP Failed for {u_id}: {e}")
            img = Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
            draw = ImageDraw.Draw(img)
            
            # Draw First Letter of Name
            try:
                # Basic font agar arial na mile
                fnt = ImageFont.truetype(FONT_PATH, 150)
            except:
                fnt = ImageFont.load_default()
                
            text = name[0].upper() if name else "?"
            
            # Center Text Logic (Updated for Pillow 10+)
            bbox = draw.textbbox((0, 0), text, font=fnt)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(((CIRCLE_SIZE - w) / 2, (CIRCLE_SIZE - h) / 2 - 20), text, font=fnt, fill="white")
            
            # Mask Apply (Circle banane ke liye)
            mask = Image.new('L', (CIRCLE_SIZE, CIRCLE_SIZE), 0)
            d_mask = ImageDraw.Draw(mask)
            d_mask.ellipse((0, 0, CIRCLE_SIZE, CIRCLE_SIZE), fill=255)
            
            result = Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (0, 0, 0, 0))
            result.paste(img, (0, 0), mask=mask)
            return result

    # 1. Generate PFPs
    pfp1 = await get_pfp(user1['id'], user1['first_name'])
    pfp2 = await get_pfp(user2['id'], user2['first_name'])

    # 2. Paste
    bg.paste(pfp1, POS_1, pfp1)
    bg.paste(pfp2, POS_2, pfp2)

    # 3. Add Names
    draw = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype(FONT_PATH, 35) 
    except:
        font = ImageFont.load_default()

    # Name 1
    name1 = user1['first_name'][:15]
    bbox1 = draw.textbbox((0, 0), name1, font=font)
    w1 = bbox1[2] - bbox1[0]
    draw.text((POS_1[0] + (CIRCLE_SIZE - w1) // 2, POS_1[1] + CIRCLE_SIZE + 40), name1, font=font, fill="white")

    # Name 2
    name2 = user2['first_name'][:15]
    bbox2 = draw.textbbox((0, 0), name2, font=font)
    w2 = bbox2[2] - bbox2[0]
    draw.text((POS_2[0] + (CIRCLE_SIZE - w2) // 2, POS_2[1] + CIRCLE_SIZE + 40), name2, font=font, fill="white")

    # 4. Save
    bio = io.BytesIO()
    bio.name = "couple.png"
    bg.save(bio, "PNG")
    bio.seek(0)
    return bio

# --- COUPLE COMMAND ---
async def couple_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    bot_id = context.bot.id if context.bot.id else 0
    
    msg = await update.message.reply_text("🔍 **Finding a perfect match...**", parse_mode=ParseMode.MARKDOWN)

    try:
        # Check if DB is connected
        if users_col is None:
            await msg.edit_text("❌ Database Error: `users_col` not found!")
            return

        # 🔥 FIX: Fetch Users Safely
        pipeline = [
            {"$match": {"_id": {"$ne": bot_id}}}, 
            {"$sample": {"size": 2}}
        ]
        
        # Async IO se bachne ke liye list()
        random_users = list(users_col.aggregate(pipeline))
        
        if len(random_users) < 2:
            # Fallback for Testing
            u1 = {'_id': update.effective_user.id, 'name': update.effective_user.first_name}
            u2 = {'_id': 0, 'name': 'Herobrine'} 
        else:
            u1 = random_users[0]
            u2 = random_users[1]
        
        user1_data = {'id': u1['_id'], 'first_name': u1.get('name', 'Lover 1')}
        user2_data = {'id': u2['_id'], 'first_name': u2.get('name', 'Lover 2')}
        
    except Exception as e:
        print(f"❌ DB Error in Couple: {e}")
        return await msg.edit_text(f"❌ Database Error: {e}")

    # Generate Image
    photo = await make_couple_img(user1_data, user2_data, context)
    
    if not photo:
        await msg.edit_text("❌ Error: `ccpic.png` missing or corrupt!")
        return

    # Caption
    caption = f"""
<blockquote><b>💘 {to_fancy("TODAY'S COUPLE")}</b></blockquote>

<blockquote>
<b>🦁 ʙᴏʏ :</b> {html.escape(user1_data['first_name'])}
<b>🐰 ɢɪʀʟ :</b> {html.escape(user2_data['first_name'])}
</blockquote>

<blockquote>
<b>✨ ᴍᴀᴛᴄʜ :</b> 100% ❤️
<b>📅 ᴅᴀᴛᴇ :</b> {to_fancy("FOREVER")}
</blockquote>
"""
    kb = [[InlineKeyboardButton("👨‍💻 Support", url="https://t.me/Dev_Digan")]] 
    
    try:
        await update.message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML
        )
        await msg.delete()
    except Exception as e:
        print(f"❌ Sending Error: {e}")
        await msg.edit_text("❌ Error sending photo!")
