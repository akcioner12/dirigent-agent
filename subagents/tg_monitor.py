"""
Sub-агент: мониторинг TG-каналов конкурентов.

ВАЖНО: бот (BotFather token) не может читать сообщения из чужих публичных
каналов, если он не админ там. Поэтому мониторинг идёт через Telethon
(user-аккаунт), а публикация в твой канал — через обычного бота.
Это две разные сущности с разными токенами.
"""
from telethon.sync import TelegramClient
from datetime import datetime, timedelta

from config import TG_API_ID, TG_API_HASH, SOURCE_CHANNELS

SESSION_NAME = "monitor_session"


def fetch_recent_posts(hours_back: int = 6, min_views: int = 0):
    """
    Забирает последние посты из SOURCE_CHANNELS за hours_back часов.
    Возвращает список dict: {channel, text, views, date}
    """
    results = []
    since = datetime.utcnow() - timedelta(hours=hours_back)

    with TelegramClient(SESSION_NAME, TG_API_ID, TG_API_HASH) as client:
        for channel in SOURCE_CHANNELS:
            try:
                for message in client.iter_messages(channel, limit=50):
                    if message.date.replace(tzinfo=None) < since:
                        break
                    if not message.text:
                        continue
                    views = message.views or 0
                    if views < min_views:
                        continue
                    results.append({
                        "channel": channel,
                        "text": message.text,
                        "views": views,
                        "date": message.date.isoformat(),
                    })
            except Exception as e:
                print(f"[tg_monitor] Ошибка при чтении {channel}: {e}")

    # Сортировка по просмотрам — сначала самое "залетевшее"
    results.sort(key=lambda x: x["views"], reverse=True)
    return results
