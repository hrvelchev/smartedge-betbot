import logging
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ SmartEdge Bot Connected\n\n"
        "Welcome! Daily betting tips will arrive at 08:00 Sofia time."
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Here are today’s betting tips:\n\n1. Team A vs Team B — Over 2.5\n2. Team C to Win\n3. Draw @ 3.60\n\n(GENERATED TIPS PLACEHOLDER)")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.run_polling()
