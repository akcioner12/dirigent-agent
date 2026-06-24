"""
Конфигурация Dirigent Agent.
Список каналов-источников и основные настройки.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "@Crypto_AI_Forex")

# Список TG-каналов конкурентов для мониторинга.
# Заполни username-ами каналов (без @, как требует Telethon, например "some_channel").
SOURCE_CHANNELS = [
    # "channel_username_1",
    # "channel_username_2",
]

# Сколько постов в день готовим (целевой темп MVP)
DAILY_POST_TARGET = 4

# Путь к SQLite базе (на Railway — Volume, смонтированный на /data)
DB_PATH = os.getenv("DB_PATH", "/data/dirigent.db")
