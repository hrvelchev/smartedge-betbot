import logging
import pytz
from datetime import datetime, time as dtime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    JobQueue,
)
import os
from tip_generator import generate_daily_tips

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Timezone for Sofia (UTC+3)
SOFIA_TZ = pytz.timezone("Europe/Sofia")

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ SmartEdge Bot Connected\n\n"
        "Welcome! Daily betting tips will arrive at 08:00 Sofia time."
    )

# /today command handler
async def send_today_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = generate_daily_tips()
    await update.message.reply_text(tips)

# Job that sends daily tips at 08:00 Sofia time
async def scheduled_tips_job(context: ContextTypes.DEFAULT_TYPE):
    tips = generate_daily_tips()
    await context.bot.send_message(chat_id=context.job.chat_id, text=tips)

# Registers the daily job after /start
async def register_daily_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job_queue: JobQueue = context.job_queue
    chat_id = update.effective_chat.id
    job_queue.run_daily(
        scheduled_tips_job,
        time=dtime(hour=8, minute=0, tzinfo=SOFIA_TZ),
        chat_id=chat_id,
        name=str(chat_id),
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start", register_daily_job))
    app.add_handler(CommandHandler("today", send_today_tips))

    app.run_polling()
