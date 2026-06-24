"""
Одноразовый скрипт для авторизации Telethon-сессии.
Запускается ЛОКАЛЬНО (не на Railway!), один раз.

Зачем: чтобы читать чужие публичные каналы, нужен доступ через твой личный
Telegram-аккаунт (не через бота). При первой авторизации Telegram пришлёт
тебе код подтверждения в самом Telegram - его нужно ввести в консоли.

После успешного запуска появится файл monitor_session.session -
его нужно будет включить в деплой (закоммитить в репозиторий ВРЕМЕННО
для первого деплоя, либо загрузить через Railway CLI) чтобы Railway
не пытался авторизоваться сам (там нет интерактивного терминала).

Использование:
1. pip install telethon python-dotenv
2. Создай .env с TG_API_ID и TG_API_HASH (см. .env.example)
3. python auth_telethon.py
4. Введи номер телефона (формат +380...)
5. Введи код, который придёт в Telegram
6. Если включена 2FA - введи пароль облака
7. Готово - появится monitor_session.session
"""
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
SESSION_NAME = "monitor_session"

if not TG_API_ID or not TG_API_HASH:
    print("Ошибка: TG_API_ID и TG_API_HASH не найдены в .env")
    exit(1)

print("Запускаю авторизацию Telethon...")
print("Сейчас Telegram пришлёт код подтверждения в само приложение Telegram.")

with TelegramClient(SESSION_NAME, TG_API_ID, TG_API_HASH) as client:
    me = client.get_me()
    print(f"\nГотово! Авторизован как: {me.first_name} (@{me.username})")
    print(f"Файл сессии создан: {SESSION_NAME}.session")

import base64

with open(f"{SESSION_NAME}.session", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print("\n" + "=" * 60)
print("ВАЖНО: НЕ коммить .session файл в git (репозиторий публичный).")
print("Вместо этого скопируй строку ниже целиком и добавь в Railway")
print("Variables как TG_SESSION_B64:")
print("=" * 60)
print(encoded)
print("=" * 60)
