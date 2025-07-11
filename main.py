import logging
import pytz
import os
from datetime import datetime, time as dtime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    JobQueue,
)
from tip_generator import generate_daily_tips, generate_tomorrow_tips

# Telegram bot token and Render-hosted domain
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", "8443"))  # Default to 8443 if not set
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")  # Render provides this automatically

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

SOFIA_TZ = pytz.timezone("Europe/Sofia")

# /start command (also registers daily tip job)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ SmartEdge Bot Connected\n\n"
        "Welcome! Daily betting tips will arrive at 08:00 Sofia time.\n\n"
        "Use /today to see today's tips or /tomorrow to preview tomorrow's tips."
    )

    chat_id = update.effective_chat.id
    context.job_queue.run_daily(
        scheduled_tips_job,
        time=dtime(hour=8, minute=0, tzinfo=SOFIA_TZ),
        chat_id=chat_id,
        name=str(chat_id),
    )

# Daily tips job
async def scheduled_tips_job(context: ContextTypes.DEFAULT_TYPE):
    tips = generate_daily_tips()
    await context.bot.send_message(chat_id=context.job.chat_id, text=tips)

# /today command
async def send_today_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = generate_daily_tips()
    await update.message.reply_text(tips)

# /tomorrow command
async def send_tomorrow_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = generate_tomorrow_tips()
    await update.message.reply_text(tips)

# Main app
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", send_today_tips))
    app.add_handler(CommandHandler("tomorrow", send_tomorrow_tips))

    # 🧠 Use webhook mode instead of polling
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{HOSTNAME}/webhook"
    )
