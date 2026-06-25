"""
Одноразовый скрипт: конвертирует сессию Telegram Desktop (tdata) в формат
Telethon, БЕЗ запроса кода подтверждения - используется существующий
залогиненный сеанс твоего Telegram Desktop приложения.

Запускать ЛОКАЛЬНО, на том же компьютере, где установлен и залогинен
Telegram Desktop.

Использование:
1. pip install opentele
2. Узнай путь к папке tdata твоего Telegram Desktop. Обычно это:
   C:\\Users\\<имя_пользователя>\\AppData\\Roaming\\Telegram Desktop\\tdata
   (Win+R -> %appdata%\\Telegram Desktop -> там должна быть папка tdata)
3. Впиши путь ниже в TDATA_PATH
4. python convert_tdata_session.py
5. Появится файл monitor_session.session и его base64 для Railway
"""
import asyncio
import base64
import os

from opentele.td import TDesktop
from opentele.api import UseCurrentSession

# !!! ВПИШИ СВОЙ ПУТЬ К tdata ЗДЕСЬ !!!
TDATA_PATH = r"C:\Users\Андрей\AppData\Roaming\Telegram Desktop\tdata"

SESSION_NAME = "monitor_session"


async def main():
    if not os.path.exists(TDATA_PATH):
        print(f"Ошибка: папка не найдена по пути {TDATA_PATH}")
        print("Проверь правильность пути - Win+R -> %appdata%\\Telegram Desktop")
        return

    tdesk = TDesktop(TDATA_PATH)
    if not tdesk.isLoaded():
        print("Ошибка: не удалось прочитать tdata. Убедись, что Telegram Desktop закрыт.")
        return

    client = await tdesk.ToTelethon(session=f"{SESSION_NAME}.session", flag=UseCurrentSession)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Успешно! Авторизован как: {me.first_name} (@{me.username})")
    else:
        print("Не удалось авторизоваться через tdata.")
        return

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
