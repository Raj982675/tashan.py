from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction   # ← Yeh line sahi hai
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ContextTypes,
    CommandHandler
)
from telegram.error import TelegramError
import asyncio
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ========================= CONFIG =========================
BOT_TOKEN = "8955096072:AAGJei1jbydABNx_aTqpXMhLs6jWxtMJXEk"  
YOUR_TELEGRAM_ID = 6213657026
USERS_FILE = "users.txt"

# File Paths
VIDEO_PATH = "IMG_4587.mp4"
APK_PATH = "9𝐗 𝑷𝑹𝑶𝑭𝑰𝑻.apk"
VOICE_PATH = "tashan voice.ogg"
# =========================================================

def save_user(user_id: int, username: str = None):
    try:
        Path(USERS_FILE).parent.mkdir(parents=True, exist_ok=True)
        users = set()
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = {line.strip() for line in f if line.strip()}
        entry = str(user_id)
        if username:
            entry = f"{user_id} | @{username}"
        if entry not in users and str(user_id) not in users:
            with open(USERS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{entry}\n")
            print(f"✅ New user saved: {user_id}")
    except:
        pass

def get_all_users():
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

@asynccontextmanager
async def get_file(path: str):
    file = None
    try:
        file = open(path, "rb")
        yield file
    finally:
        if file:
            file.close()

async def send_with_retry(bot, chat_id, func, max_retries=3):
    for attempt in range(max_retries):
        try:
            await func()
            return True, None
        except TelegramError as e:
            if "Too Many Requests" in str(e) or "Flood" in str(e):
                await asyncio.sleep(1 + attempt)
                continue
            return False, str(e)
        except Exception as e:
            return False, str(e)
    return False, "Max retries exceeded"

# ====================== JOIN REQUEST ======================
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    user_id = req.from_user.id
    username = req.from_user.username or None
    chat_id = req.chat.id
    print(f"🔄 New Join Request from: {user_id} (@{username})")
    
    try:
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        print(f"✅ Join Request Auto Approved for: {user_id}")
    except Exception as e:
        print(f"❌ Failed to approve: {e}")

    save_user(user_id, username)

    try:
        # 1. VIDEO
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_VIDEO)
        if os.path.exists(VIDEO_PATH):
            async with get_file(VIDEO_PATH) as video:
                await send_with_retry(context.bot, user_id, lambda: context.bot.send_video(
                    chat_id=user_id,
                    video=video,
                    caption="<b>💯 POWER OFF 😮😕😕😄 HACK SURE SHOT WINING 💯</b>\n\n"
                            "Ragistration Link 🔗 👇\n"
                            "https://www.tswinbb.cc/#/register?invitationCode=638222300137\n\n"
                            "DEPOSIT KARKE SCREENSHOT BHEJ DO VIP GROUP ME JOIN KAR DUNGA TUMHE ✅",
                    parse_mode='HTML',
                    supports_streaming=True
                ))
        await asyncio.sleep(0.6)

        # 2. APK
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_DOCUMENT)
        if os.path.exists(APK_PATH):
            async with get_file(APK_PATH) as apk:
                await send_with_retry(context.bot, user_id, lambda: context.bot.send_document(
                    chat_id=user_id,
                    document=apk,
                    caption="<b>✅ NUMBER HACK ✅</b>",
                    parse_mode='HTML'
                ))
        await asyncio.sleep(0.6)

        # 3. VOICE
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
        if os.path.exists(VOICE_PATH):
            async with get_file(VOICE_PATH) as voice:
                await send_with_retry(context.bot, user_id, lambda: context.bot.send_voice(
                    chat_id=user_id,
                    voice=voice,
                    caption="<b>HACK का Use कैसे करें 👆🏻👆🏻👆🏻👆🏻</b>",
                    parse_mode='HTML'
                ))
        await asyncio.sleep(0.5)

        # 4. START BUTTON
        keyboard = [[InlineKeyboardButton("🚀 START BOT", url="https://t.me/Primiumnumberhackbot?start=welcome")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_with_retry(context.bot, user_id, lambda: context.bot.send_message(
            chat_id=user_id,
            text="<b>✅ Deposit karke Screenshot Sand karo 😄</b>",
            parse_mode='HTML',
            reply_markup=reply_markup
        ))

        print(f"✅ Full sequence completed for: {user_id}")

    except Exception as e:
        print(f"Error sending messages to {user_id}: {e}")

# ====================== BROADCAST ======================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        await update.message.reply_text("❌ Permission Denied!")
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("❌ No users found.")
        return
    await update.message.reply_text(f"🔄 Broadcasting to {len(users)} users...")
    success = []
    failed = []
    delay = 0.2
    for user_line in users:
        try:
            if '|' in user_line:
                parts = user_line.split('|')
                user_id = int(parts[0].strip())
                username = parts[1].strip() if len(parts) > 1 else "Unknown"
            else:
                user_id = int(user_line)
                username = "No Username"
            if update.message.reply_to_message:
                msg = update.message.reply_to_message
                if msg.text:
                    ok, err = await send_with_retry(context.bot, user_id,
                        lambda: context.bot.send_message(chat_id=user_id,
                                                         text=f"<b>{msg.text}</b>",
                                                         parse_mode='HTML'))
                elif msg.photo:
                    ok, err = await send_with_retry(context.bot, user_id,
                        lambda: context.bot.send_photo(chat_id=user_id,
                                                       photo=msg.photo[-1].file_id,
                                                       caption=f"<b>{msg.caption or ''}</b>",
                                                       parse_mode='HTML'))
                else:
                    ok, err = False, "Unsupported type"
            else:
                text = ' '.join(context.args) if context.args else "Broadcast Message"
                ok, err = await send_with_retry(context.bot, user_id,
                    lambda: context.bot.send_message(chat_id=user_id,
                                                     text=f"<b>{text}</b>",
                                                     parse_mode='HTML'))
            if ok:
                success.append(f"{user_id} (@{username})")
            else:
                failed.append(f"{user_id} (@{username}) - {err[:50]}")
        except Exception as e:
            failed.append(f"{user_id} - Error: {str(e)[:50]}")
        await asyncio.sleep(delay)
    report = f"✅ Broadcast Completed!\n\n"
    report += f"✅ Success: {len(success)} / {len(users)}\n"
    report += f"❌ Failed: {len(failed)}\n\n"
    if success:
        report += "✅ Successful Users:\n"
        report += "\n".join(success[:30])
        if len(success) > 30:
            report += f"\n...and {len(success)-30} more\n\n"
    if failed:
        report += "❌ Failed Users:\n"
        report += "\n".join(failed[:30])
        if len(failed) > 30:
            report += f"\n...and {len(failed)-30} more"
    await update.message.reply_text(report)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
   
    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(CommandHandler("broadcast", broadcast))
    print("🤖 Bot Started Successfully")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
