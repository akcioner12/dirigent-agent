"""
Railway ограничивает значение переменной до 32768 символов.
Наша base64-сессия больше, поэтому делим на 2 части.
Запускать локально, в той же папке, где лежит monitor_session.session
(после успешного запуска auth_telethon_qr.py).
"""
import base64

with open("monitor_session.session", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

mid = len(encoded) // 2 + 1

part1 = encoded[:mid]
part2 = encoded[mid:]

print(f"Длина полной строки: {len(encoded)}")
print(f"Часть 1: {len(part1)} символов")
print(f"Часть 2: {len(part2)} символов")

print("\n" + "=" * 60)
print("TG_SESSION_B64_PART1 =")
print("=" * 60)
print(part1)

print("\n" + "=" * 60)
print("TG_SESSION_B64_PART2 =")
print("=" * 60)
print(part2)
