import os
from dotenv import load_dotenv

load_dotenv()

print("Проверка переменных окружения:")
print(f"PRACTICUM_TOKEN: {'✅ Есть' if os.getenv('PRACTICUM_TOKEN') else '❌ Нет'}")
print(f"TELEGRAM_TOKEN: {'✅ Есть' if os.getenv('TELEGRAM_TOKEN') else '❌ Нет'}")
print(f"TELEGRAM_CHAT_ID: {'✅ Есть' if os.getenv('TELEGRAM_CHAT_ID') else '❌ Нет'}")
