"""
Авторизация Telethon с явным запросом кода по SMS (force_sms=True),
на случай если доставка кода через само приложение Telegram не работает.
"""
import os
import asyncio
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

asyncio.set_event_loop(asyncio.new_event_loop())

TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
SESSION_NAME = "monitor_session"

if not TG_API_ID or not TG_API_HASH:
    print("Ошибка: TG_API_ID и TG_API_HASH не найдены в .env")
    exit(1)

phone = input("Введи номер телефона (+380...): ").strip()

client = TelegramClient(SESSION_NAME, TG_API_ID, TG_API_HASH)
client.connect()

if not client.is_user_authorized():
    sent = client.send_code_request(phone, force_sms=True)
    print(f"\nКод запрошен через SMS (type={sent.type}). Проверь SMS на телефоне.")
    code = input("Введи код из SMS: ").strip()
    try:
        client.sign_in(phone, code)
    except Exception as e:
        print(f"Ошибка входа: {e}")
        password = input("Если включена 2FA, введи пароль облака: ").strip()
        client.sign_in(password=password)

me = client.get_me()
print(f"\nГотово! Авторизован как: {me.first_name} (@{me.username})")

client.disconnect()

import base64

with open(f"{SESSION_NAME}.session", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print("\n" + "=" * 60)
print("Скопируй строку ниже и добавь в Railway Variables как TG_SESSION_B64:")
print("=" * 60)
print(encoded)
print("=" * 60)
