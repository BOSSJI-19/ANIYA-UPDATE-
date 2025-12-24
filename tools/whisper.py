import uuid
from telegram import (
    Update, 
    InlineQueryResultArticle, 
    InputTextMessageContent, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, InlineQueryHandler, CallbackQueryHandler
from telegram.error import BadRequest

# --- CONFIG ---
# In-Memory Database for Whispers
whisper_db = {}
IMG_URL = "https://te.legra.ph/file/3eec679156a393c6a1053.jpg"

# --- HELPER: GET USER ID ---
async def get_target_user(bot, query_str):
    """
    Username ya ID se User object nikalta hai.
    """
    try:
        # Agar ID hai (digits)
        if query_str.isdigit():
            chat = await bot.get_chat(int(query_str))
            return chat
        # Agar username hai
        elif query_str.startswith("@"):
            chat = await bot.get_chat(query_str)
            return chat
        else:
            return None
    except:
        return None

# --- INLINE QUERY HANDLER ---
async def inline_whisper_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    user = update.inline_query.from_user
    results = []
    
    # 1. Agar query empty ya choti hai (Usage dikhao)
    if not query or len(query.split()) < 2:
        bot_username = context.bot.username
        usage_text = f"💒 **Whisper Usage:**\n\n`@{bot_username} [USERNAME/ID] [MESSAGE]`"
        
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="💒 Whisper Mode",
                description="Format: @Bot user message",
                thumbnail_url=IMG_URL,
                input_message_content=InputTextMessageContent(usage_text, parse_mode=ParseMode.MARKDOWN),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💒 Try Whisper", switch_inline_query_current_chat="")
                ]])
            )
        )
    
    # 2. Agar query valid lag rahi hai
    else:
        try:
            parts = query.split(None, 1)
            target_input = parts[0]
            msg_text = parts[1]
            
            # Target User ko verify karo
            target = await get_target_user(context.bot, target_input)
            
            if not target:
                # Invalid User Error Article
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        title="❌ Invalid User",
                        description="User not found! Use valid ID or Username.",
                        thumbnail_url=IMG_URL,
                        input_message_content=InputTextMessageContent("❌ Invalid username or ID provided!"),
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("💒 Try Again", switch_inline_query_current_chat="")
                        ]])
                    )
                )
            else:
                # --- SUCCESS: WHISPER CREATE KARO ---
                sender_id = user.id
                receiver_id = target.id
                
                # Database me store karo (Key: SenderID_ReceiverID)
                # Note: UUID use kar rahe hain taaki har whisper unique ho
                whisper_id = str(uuid.uuid4())[:8] 
                db_key = f"{whisper_id}_{sender_id}_{receiver_id}"
                whisper_db[db_key] = msg_text
                
                # Buttons
                whisper_btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("💒 Whisper", callback_data=f"show_whisper_{db_key}")
                ]])
                
                onetime_btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔩 One-Time Whisper", callback_data=f"show_whisper_{db_key}_one")
                ]])
                
                # Result 1: Normal Whisper
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        title="💒 Send Whisper",
                        description=f"To: {target.first_name}",
                        thumbnail_url=IMG_URL,
                        input_message_content=InputTextMessageContent(
                            f"💒 **Whisper Message**\n\n👤 **From:** {user.first_name}\n🔒 **To:** {target.first_name}\n\nTap below to read 👇",
                            parse_mode=ParseMode.MARKDOWN
                        ),
                        reply_markup=whisper_btn
                    )
                )
                
                # Result 2: One-Time Whisper
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        title="🔩 One-Time Whisper",
                        description=f"Destructs after reading. To: {target.first_name}",
                        thumbnail_url=IMG_URL,
                        input_message_content=InputTextMessageContent(
                            f"🔩 **One-Time Whisper**\n\n👤 **From:** {user.first_name}\n🔒 **To:** {target.first_name}\n\n⚠️ *This message will disappear after reading.*",
                            parse_mode=ParseMode.MARKDOWN
                        ),
                        reply_markup=onetime_btn
                    )
                )

        except Exception as e:
            print(f"Whisper Error: {e}")

    # Results bhejo
    await update.inline_query.answer(results, cache_time=0, is_personal=True)


# --- CALLBACK HANDLER (View Whisper) ---
async def whisper_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")
    
    # Data Structure: show_whisper_{id}_{sender}_{receiver}_{optional:one}
    whisper_id = data[2]
    sender_id = int(data[3])
    receiver_id = int(data[4])
    is_one_time = len(data) > 5 and data[5] == "one"
    
    db_key = f"{whisper_id}_{sender_id}_{receiver_id}"
    clicker_id = query.from_user.id
    
    # 1. Verify User (Sirf Sender ya Receiver dekh sakta hai)
    if clicker_id not in [sender_id, receiver_id]:
        await query.answer("🚧 This whisper is not for you!", show_alert=True)
        # Optional: Sender ko notify karo
        if clicker_id != sender_id:
            try:
                # Rate limit se bachne ke liye try-except
                # await context.bot.send_message(sender_id, f"⚠️ {query.from_user.first_name} tried to open your whisper!")
                pass
            except:
                pass
        return

    # 2. Message Retrieve karo
    message = whisper_db.get(db_key)
    
    if not message:
        await query.answer("🚫 Error: Whisper expired or deleted from database!", show_alert=True)
        return

    # 3. Whisper Dikhao
    await query.answer(message, show_alert=True)
    
    # 4. Handle One-Time Whisper
    if is_one_time and clicker_id == receiver_id:
        # Database se delete karo
        if db_key in whisper_db:
            del whisper_db[db_key]
        
        # Message Edit karo
        switch_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("Go Inline 🪝", switch_inline_query_current_chat="")
        ]])
        
        try:
            await query.edit_message_text(
                "📬 **Whisper has been read!**\n\nIt was a one-time message.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=switch_btn
            )
        except BadRequest:
            pass # Message too old or content same

# --- REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(InlineQueryHandler(inline_whisper_handler))
    app.add_handler(CallbackQueryHandler(whisper_callback, pattern="^show_whisper_"))
              
