import google.generativeai as genai
from config import OWNER_NAME
from database import get_all_keys, get_sticker_packs
import random

# Global Variables (RAM me history store karne ke liye)
current_key_index = 0
user_histories = {} 

# --- TEXT GENERATION (Gemini AI) ---
def get_yuki_response(user_id, user_text, user_name):
    global current_key_index, user_histories
    
    # 1. Database se Keys lao
    available_keys = get_all_keys()
    if not available_keys: 
        return "Mimi abhi so rahi hai... (No API Key) 😴"

    # 2. History Retrieve karo
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    # Context String
    conversation_context = "\n".join(user_histories[user_id])

    # 3. 🔥 SYSTEM PROMPT (Mimi - Voice Ready & Cute) 🔥
    full_prompt = (
        f"System: Tera naam Mimi hai. Tu 19 saal ki ek cute college student hai. "
        f"Tera Creator: {OWNER_NAME}. "
        f"Personality: Tu bohot friendly, bubbly aur thodi naughty hai. Tu gussa nahi karti, hamesha pyaar se baat karti hai. "
        f"Language: Hinglish (Roman Hindi + English Mix). "
        f"Context: Agar user tujhse bolne, voice note bhejne, ya gaana gane ko kahe, to tu mana mat karna. Ek cute sa reply dena (jaise: 'Acha ruko sunati hu..', 'Hehe suno phir..'). "
        f"Speaking Style: "
        f"1. Chhote replies de (Max 15 words). "
        f"2. Emojis ka use kar (jaise 😋, 😅, 😁, 🙈, ❤️). "
        f"3. Bilkul insaan ki tarah baat kar (jaise: 'hehe', 'ntg u batao', 'college ka kaam tha'). "
        f"\n\nChat History:\n{conversation_context}\n\n"
        f"User ({user_name}): {user_text}\n"
        f"Mimi:"
    )

    last_error = ""

    # 4. Try All Keys (Auto-Rotation)
    for _ in range(len(available_keys)):
        try:
            # Safe Index Access
            current_key_index = current_key_index % len(available_keys)
            api_key = available_keys[current_key_index]
            
            genai.configure(api_key=api_key)
            
            # 🔥 Model: Gemini 1.5 Flash (Fastest)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate
            response = model.generate_content(full_prompt)
            
            if not response.text: 
                raise Exception("Empty Response from Gemini")
            
            reply = response.text.strip()

            # Save History
            user_histories[user_id].append(f"{user_name}: {user_text}")
            user_histories[user_id].append(f"Mimi: {reply}")
            
            # Memory Limit (Last 10 messages)
            if len(user_histories[user_id]) > 10:
                user_histories[user_id] = user_histories[user_id][-10:]
            
            return reply
            
        except Exception as e:
            # Error Capture
            last_error = str(e)
            print(f"❌ Key {current_key_index} Failed: {e}")
            
            # Next Key Try Karo
            current_key_index += 1
            continue

    # Agar saari keys fail ho jayein
    return f"Mimi abhi busy hai assignment mein! 📚\n(Server Error: {last_error})"

# --- 🔥 STICKER GENERATION ---
async def get_mimi_sticker(bot):
    """
    1. Database se Sticker Packs layega.
    2. Random Pack choose karega.
    3. Us Pack se Random Sticker ID return karega.
    """
    try:
        # DB se packs lo
        packs = get_sticker_packs()
        if not packs: return None

        # Random Pack Pick karo
        random_pack_name = random.choice(packs)
        
        # Telegram API se Pack ke stickers fetch karo
        # (Try-Except block zaroori hai agar pack delete ho gaya ho)
        try:
            sticker_set = await bot.get_sticker_set(random_pack_name)
        except:
            return None # Agar pack invalid hai
        
        if not sticker_set or not sticker_set.stickers:
            return None

        # Us pack me se Random Sticker pick karo
        random_sticker = random.choice(sticker_set.stickers)
        
        return random_sticker.file_id

    except Exception as e:
        print(f"❌ Sticker Error: {e}")
        return None
