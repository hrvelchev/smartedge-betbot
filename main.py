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
    # Schedule a new daily job at 08:00 Sofia time. The job’s name is set to the
    # chat ID so it can be uniquely identified and managed.
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

# ✅ Main runner
def main() -> None:
    """Initialize and start the Telegram bot in polling mode.

    This function clears any existing webhook to ensure polling works correctly,
    builds the application, registers command handlers, and starts the
    bot using long polling. It does not need to be asynchronous because
    ``application.run_polling()`` blocks and manages its own event loop.
    """
    # Clear any existing webhook before switching to polling. We execute this
    # coroutine before building the app so that Telegram doesn’t send updates via
    # webhook while our bot is polling. If the token is invalid or the network
    # is unavailable, the exception will surface and prevent startup.
    asyncio.run(clear_webhook())

    # Build the application and register handlers. Using ``ApplicationBuilder``
    # ensures compatibility with python-telegram-bot v20+.
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", send_today_tips))
    app.add_handler(CommandHandler("tomorrow", send_tomorrow_tips))

    # Start the bot using long polling. This call is blocking and will run
    # until the process is terminated. No await is necessary here because the
    # method manages the asyncio event loop internally.
    app.run_polling()

# ✅ Start everything
if __name__ == "__main__":
    main()