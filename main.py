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
from tip_generator import generate_daily_tips, generate_tomorrow_tips  # ✅ Already added

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Timezone for Sofia (UTC+3)
SOFIA_TZ = pytz.timezone("Europe/Sofia")

# ✅ Combined /start + job registration in one handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ SmartEdge Bot Connected\n\n"
        "Welcome! Daily betting tips will arrive at 08:00 Sofia time.\n\n"
        "Use /today to see today's tips or /tomorrow to preview tomorrow's tips."
    )

    # Register the scheduled daily tips job
    job_queue: JobQueue = context.job_queue
    chat_id = update.effective_chat.id
    job_queue.run_daily(
        scheduled_tips_job,
        time=dtime(hour=8, minute=0, tzinfo=SOFIA_TZ),
        chat_id=chat_id,
        name=str(chat_id),
    )

# /today command handler
async def send_today_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = generate_daily_tips()
    await update.message.reply_text(tips)

# /tomorrow command handler
async def send_tomorrow_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = generate_tomorrow_tips()
    await update.message.reply_text(tips)

# Scheduled job for daily tips
async def scheduled_tips_job(context: ContextTypes.DEFAULT_TYPE):
    tips = generate_daily_tips()
    await context.bot.send_message(chat_id=context.job.chat_id, text=tips)

# ✅ Main app launch
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", send_today_tips))
    app.add_handler(CommandHandler("tomorrow", send_tomorrow_tips))

    app.run_polling()
