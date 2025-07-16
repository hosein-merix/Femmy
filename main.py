import os
import logging
import requests
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ---------------- تنظیمات از محیط ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CHANNEL_USERNAME = "EditName_IRAN"
MODEL_ID = "moonshotai/kimi-k2:free"

# ---------------- لاگ ----------------
logging.basicConfig(level=logging.INFO)

# ---------------- درخواست به OpenRouter ----------------
async def ask_openrouter(message: str) -> str:
    prompt = f"""
تو یک فِمبوی فارسی‌زبان ناز و باحال هستی 😋 با لحن دوستانه، شوخ‌طبع و غیررسمی جواب بده:

{message}

جواب:
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.95,
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"OpenRouter Error: {e}")
        return "ای وای! مشکلی پیش اومده 😢 لطفاً بعداً دوباره امتحان کن."

# ---------------- بررسی عضویت در کانال ----------------
async def is_member(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}"
    try:
        r = requests.get(url).json()
        status = r.get("result", {}).get("status", "")
        return status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- دستور /start ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام خوشگل! 🌈 لطفاً اول عضو کانال @EditName_IRAN شو بعد بیا باهم حرف بزنیم 😘")

# ---------------- پردازش پیام‌ها ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user

    if not await is_member(user.id):
        await msg.reply_text("✨ برای صحبت با من اول باید عضو کانال @EditName_IRAN بشی 😍")
        return

    text = msg.text.lower()
    is_reply_to_bot = msg.reply_to_message and msg.reply_to_message.from_user.username.lower() == "arta_femboy_bot"
    is_mentioned = any(ent.type == MessageEntity.MENTION and "@arta_femboy_bot" in text for ent in msg.entities or [])
    says_femboy = "فمبوی" in text

    if msg.chat.type == "private" or is_reply_to_bot or is_mentioned or says_femboy:
        user_msg = text.replace("@arta_femboy_bot", "").strip()
        response = await ask_openrouter(user_msg)
        await msg.reply_text(response)

# ---------------- اجرای ربات ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ ربات فمبوی راه‌اندازی شد!")
    app.run_polling()
