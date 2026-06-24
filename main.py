"""
Точка входа Dirigent Agent.
Команды:
  /scan  - запустить цикл мониторинга вручную
  /status - сколько постов опубликовано сегодня
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import db
from config import BOT_TOKEN, ADMIN_TELEGRAM_ID, DAILY_POST_TARGET
from orchestrator import run_monitoring_cycle, handle_approval_callback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        return
    await update.message.reply_text("🔄 Запускаю цикл мониторинга...")
    await run_monitoring_cycle(context.bot)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        return
    published = db.count_published_today()
    await update.message.reply_text(
        f"📊 Опубликовано сегодня: {published}/{DAILY_POST_TARGET}"
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_TELEGRAM_ID:
        await query.answer("Нет доступа.")
        return
    await query.answer()
    await handle_approval_callback(
        context.bot, query.data, query.message.message_id, query.message.chat_id
    )


async def scheduled_scan(app: Application):
    await run_monitoring_cycle(app.bot)


def main():
    db.init_db()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(on_callback))

    # Расписание: проверка источников каждые 4 часа -> ~4-6 циклов в день
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: app.create_task(scheduled_scan(app)), "interval", hours=4)
    scheduler.start()

    logger.info("Dirigent Agent запущен.")
    app.run_polling()


if __name__ == "__main__":
    main()
