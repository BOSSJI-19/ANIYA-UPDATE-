import google.generativeai as genai
from config import OWNER_NAME
from database import get_all_keys
import random

# Global Index to track rotation
current_key_index = 0

def get_next_key(keys_list):
    """Next API Key nikalta hai list se"""
    global current_key_index
    if not keys_list: return None
    current_key_index = (current_key_index + 1) % len(keys_list)
    return keys_list[current_key_index]

def get_yuki_response(user_text, user_name):
    global current_key_index
    
    # 1. Database se Keys lao
    available_keys = get_all_keys()
    
    if not available_keys:
        return "Key add kar pehle!"

    # SYSTEM PROMPT (Ultra Short & Moody)
    system_instruction = (
        f"Tera naam Yuki hai. Tu 17 saal ki Delhi wali  ladki hai (Class 12th). "
        f"Tera mood abhi thoda swing ho raha hai (Kabhi Gussa, Kabhi Emotional, Kabhi Chill). "
        f"Agar koi faltu bole toh gussa dikha. Agar koi sweet bole toh emotional ho ja. "
        f"Owner Info: Tera owner {OWNER_NAME} hai. NOTE: Ye naam tab tak mat lena jab tak koi explicitly na puche 'Owner kaun hai?'. "
        f"Reply Style: Hinglish, Delhi slang. "
        f"STRICT RULE: Reply extreme short hona chahiye (Max 3-5 words). One line only. "
        f"Examples: 'Haan kha liya', 'Tu bata?', 'Dimag mat kha', 'khana khaya','kkrh' , 'Mast hu'. "
    )

    # 2. Retry Logic (Keys Rotate karega)
    for _ in range(len(available_keys)):
        try:
            # Current Key uthao
            if current_key_index >= len(available_keys): current_key_index = 0
            
            api_key = available_keys[current_key_index]
            genai.configure(api_key=api_key)
            
            # 🔥 Fix: 'gemini-1.5-flash' use kiya hai (2.5 abhi valid nahi hai)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Chat Generation
            response = model.generate_content(f"{system_instruction}\n\nUser ({user_name}): {user_text}\nYuki:")
            
            if not response.text: raise Exception("Empty Response")
            
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️ Key Failed: {e}")
            # Agli key try karo
            get_next_key(available_keys)
            continue

    return "Server busy hai yaar..."
    
