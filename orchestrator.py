"""
Оркестратор: связывает мониторинг -> rewrite -> approval -> publish.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot

from config import ADMIN_TELEGRAM_ID, TARGET_CHANNEL, DAILY_POST_TARGET
from subagents.tg_monitor import fetch_recent_posts
from subagents.rewriter import rewrite_post
import db


def build_approval_keyboard(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Опубликовать", callback_data=f"approve:{post_id}"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"reject:{post_id}"),
        ]
    ])


async def run_monitoring_cycle(bot: Bot):
    """
    Запускается по расписанию или по команде /scan.
    Находит контент, переделывает, шлёт на одобрение админу.
    """
    if db.count_published_today() >= DAILY_POST_TARGET:
        return  # дневной лимит постов уже выполнен

    findings = fetch_recent_posts(hours_back=6)
    if not findings:
        await bot.send_message(ADMIN_TELEGRAM_ID, "🔍 За последние 6 часов в источниках ничего релевантного не найдено.")
        return

    top = findings[0]  # самый "залетевший" пост
    rewritten = rewrite_post(top["text"], top["channel"])
    post_id = db.add_post(top["channel"], top["text"], rewritten)

    text = (
        f"📝 <b>Черновик поста #{post_id}</b>\n"
        f"Источник: {top['channel']} ({top['views']} просмотров)\n\n"
        f"{rewritten}"
    )
    await bot.send_message(
        ADMIN_TELEGRAM_ID,
        text,
        parse_mode="HTML",
        reply_markup=build_approval_keyboard(post_id),
    )


async def handle_approval_callback(bot: Bot, callback_data: str, message_id: int, chat_id: int):
    action, post_id_str = callback_data.split(":")
    post_id = int(post_id_str)
    post = db.get_post(post_id)

    if not post:
        await bot.edit_message_text("⚠️ Пост не найден.", chat_id=chat_id, message_id=message_id)
        return

    rewritten_text = post[3]  # колонка rewritten_text

    if action == "approve":
        await bot.send_message(TARGET_CHANNEL, rewritten_text, parse_mode="HTML")
        db.update_status(post_id, "published")
        await bot.edit_message_text(
            f"✅ Пост #{post_id} опубликован в {TARGET_CHANNEL}",
            chat_id=chat_id,
            message_id=message_id,
        )
    elif action == "reject":
        db.update_status(post_id, "rejected")
        await bot.edit_message_text(
            f"❌ Пост #{post_id} отменён.",
            chat_id=chat_id,
            message_id=message_id,
        )
