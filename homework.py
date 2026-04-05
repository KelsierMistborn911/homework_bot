import os
import sys
import time
import logging
import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

PRACTICUM_API_URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def get_api_answer(timestamp):
    """Делает запрос к API Практикума."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}
    response = requests.get(PRACTICUM_API_URL, headers=headers, params=params)
    return response.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не словарь')
    if 'homeworks' not in response:
        raise KeyError('Нет ключа homeworks')
    if not isinstance(response['homeworks'], list):
        raise TypeError('homeworks не список')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус домашней работы."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(status)
    return f'Изменился статус работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует переменная окружения')
        sys.exit(1)
    
    bot = Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    
    while True:
        response = get_api_answer(timestamp)
        homeworks = check_response(response)
        for homework in homeworks:
            message = parse_status(homework)
            send_message(bot, message)
        timestamp = response.get('current_date', timestamp)
        time.sleep(600)


if __name__ == '__main__':
    main()
