import logging
import pytz
import os
import asyncio
from datetime import datetime, time as dtime
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from tip_generator import generate_daily_tips, generate_tomorrow_tips

# Telegram bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Sofia timezone (UTC+3)
SOFIA_TZ = pytz.timezone("Europe/Sofia")

# 🔧 Clear webhook
async def clear_webhook():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("🔌 Webhook cleared before polling started.")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ SmartEdge Bot Connected\n\n"
        "Welcome! Daily betting tips will arrive at 08:00 Sofia time.\n\n"
        "Use /today to see today's tips or /tomorrow to preview tomorrow's tips."
    )
    chat_id = update.effective_chat.id
    # Remove any existing daily job for this chat to avoid duplicates.
    existing = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in existing:
        job.schedule_removal()
    # Schedule a new daily job at 08:00 Sofia time
    context.job_queue.run_daily(
        scheduled_tips_job,
        time=dtime(hour=8, minute=0, tzinfo=SOFIA_TZ),
        chat_id=chat_id,
        name=str(chat_id),
    )

# Daily scheduled job
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

# ✅ Main runner with explicit event loop for Python 3.13
def main() -> None:
    """
    Initialize and start the Telegram bot in polling mode with explicit event loop handling.
    """
    # Explicitly create and set a new event loop (Python 3.13 requires this)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Clear any existing webhook before switching to polling
    loop.run_until_complete(clear_webhook())

    # Build the application and register handlers
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", send_today_tips))
    app.add_handler(CommandHandler("tomorrow", send_tomorrow_tips))

    # Run polling inside the created loop
    loop.run_until_complete(app.run_polling())

# ✅ Start everything
if __name__ == "__main__":
    main()
