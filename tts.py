import edge_tts
import os
import asyncio

# 🔥 VOICE CHANGE: "en-IN-NeerjaNeural"
# Ye Hinglish (Roman Hindi) ko sabse best bolti hai.
# Swara (Hindi) English text ko robotic padhti hai, isliye Neerja use kar rahe hain.
VOICE = "en-IN-NeerjaNeural"

async def generate_voice(text):
    """
    Generates voice using Microsoft Edge TTS (Free).
    Optimized for Hinglish & Cute Tone.
    """
    try:
        output_file = f"mimi_voice_{os.urandom(3).hex()}.mp3"
        
        # 🔥 EMOTION & SPEED SETTINGS
        # rate="+10%": Thoda tez bole (Young energy)
        # pitch="+5Hz": Awaaz thodi patli/cute lage
        communicate = edge_tts.Communicate(text, VOICE, rate="+10%", pitch="+5Hz")
        
        await communicate.save(output_file)
        return output_file

    except Exception as e:
        print(f"❌ EdgeTTS Error: {e}")
        return None
