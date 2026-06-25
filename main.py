"""
Точка входа Dirigent Agent.
Команды:
  /scan  - запустить цикл мониторинга вручную
  /status - сколько постов опубликовано сегодня
"""
import base64
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import db
from config import BOT_TOKEN, ADMIN_TELEGRAM_ID, DAILY_POST_TARGET
from orchestrator import run_monitoring_cycle, handle_approval_callback


def restore_telethon_session():
    """
    На Railway нет интерактивного терминала для первой авторизации Telethon,
    поэтому сессия передаётся через переменные окружения (сгенерированную
    локально через auth_telethon_qr.py + split_session_b64.py) и
    восстанавливается в файл при каждом старте сервиса.

    Railway ограничивает значение одной переменной до 32768 символов,
    поэтому сессия может быть разбита на TG_SESSION_B64_PART1 и _PART2.
    Если переменная TG_SESSION_B64 целиком помещается - используется она.
    """
    session_b64 = os.getenv("TG_SESSION_B64")
    if not session_b64:
        part1 = os.getenv("TG_SESSION_B64_PART1", "")
        part2 = os.getenv("TG_SESSION_B64_PART2", "")
        session_b64 = part1 + part2

    if not session_b64:
        logging.warning(
            "TG_SESSION_B64 (или PART1/PART2) не задана - мониторинг конкурентов "
            "не будет работать. Запусти auth_telethon_qr.py локально."
        )
        return
    session_path = "monitor_session.session"
    if not os.path.exists(session_path):
        with open(session_path, "wb") as f:
            f.write(base64.b64decode(session_b64))
        logging.info("Telethon-сессия восстановлена из переменных окружения.")

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
    restore_telethon_session()
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
