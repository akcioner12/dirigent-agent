"""
Авторизация Telethon через QR-код - без запроса кода вообще.
Аналог "Привязать устройство" в настройках Telegram.

Использование:
1. python auth_telethon_qr.py
2. В консоли появится ссылка вида tg://login?token=...
   ИЛИ сразу ASCII QR-код (если установлен qrcode[pil])
3. На ТЕЛЕФОНЕ: Telegram -> Настройки -> Устройства -> Подключить устройство
   -> Сканировать QR-код (либо открыть ссылку tg://login?token=... прямо на
   телефоне, если показывается просто текст, а не картинка)
4. Подтвердить на телефоне
5. Появится base64-строка для Railway
"""
import asyncio
import base64
import os

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
SESSION_NAME = "monitor_session"


async def main():
    if not TG_API_ID or not TG_API_HASH:
        print("Ошибка: TG_API_ID и TG_API_HASH не найдены в .env")
        return

    client = TelegramClient(SESSION_NAME, TG_API_ID, TG_API_HASH)
    await client.connect()

    qr_login = await client.qr_login()

    async def show_qr(qr):
        try:
            import qrcode
            img = qrcode.make(qr.url)
            img.save("login_qr.png")
            os.startfile("login_qr.png")
        except ImportError:
            pass
        print(f"\n[Новый QR] Сканируй сейчас: {qr.url}")

    await show_qr(qr_login)
    print("\n" + "=" * 60)
    print("СРАЗУ сканируй QR-код с экрана камерой телефона:")
    print("Telegram -> Настройки -> Устройства -> Сканировать QR")
    print("QR обновляется автоматически каждые ~25 секунд, если не успел.")
    print("=" * 60 + "\n")

    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            await qr_login.wait(timeout=25)
            break  # успешный вход
        except asyncio.TimeoutError:
            print(f"Попытка {attempt + 1}/{max_attempts}: не успел, обновляю QR...")
            await qr_login.recreate()
            await show_qr(qr_login)
        except Exception as e:
            if "Two-steps verification" in str(e) or "password is required" in str(e):
                print("\nВключена двухфакторная аутентификация (2FA).")
                password = input("Введи пароль облака (Cloud Password): ").strip()
                await client.sign_in(password=password)
                break
            raise
    else:
        print("Не удалось войти за все попытки. Запусти скрипт снова.")
        await client.disconnect()
        return

    me = await client.get_me()
    print(f"Готово! Авторизован как: {me.first_name} (@{me.username})")

    await client.disconnect()

    with open(f"{SESSION_NAME}.session", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    print("\n" + "=" * 60)
    print("Скопируй строку ниже и добавь в Railway Variables как TG_SESSION_B64:")
    print("=" * 60)
    print(encoded)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
