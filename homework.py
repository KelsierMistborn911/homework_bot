"""Модуль для бота-ассистента Практикума."""

import os
import sys
import time
import logging
import requests
from dotenv import load_dotenv
import telebot
from telebot.apihelper import ApiTelegramException

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

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def get_api_answer(timestamp):
    """Делает запрос к API Практикума."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}
    try:
        response = requests.get(PRACTICUM_API_URL, headers=headers, params=params)
        if response.status_code != 200:
            logger.error(f'Эндпоинт недоступен. Код ответа: {response.status_code}')
            raise Exception(f'Ошибка API: {response.status_code}')
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f'Сбой при запросе к API: {e}')
        raise


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        logger.error('Ответ API не является словарем')
        raise TypeError('Ответ API не словарь')
    if 'homeworks' not in response:
        logger.error('В ответе API отсутствует ключ homeworks')
        raise KeyError('Нет ключа homeworks')
    if not isinstance(response['homeworks'], list):
        logger.error('homeworks не является списком')
        raise TypeError('homeworks не список')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        logger.error('Отсутствует ключ homework_name')
        raise KeyError('Нет ключа homework_name')
    if 'status' not in homework:
        logger.error('Отсутствует ключ status')
        raise KeyError('Нет ключа status')
    homework_name = homework['homework_name']
    status = homework['status']
    if status not in HOMEWORK_STATUSES:
        logger.error(f'Неожиданный статус домашней работы: {status}')
        raise ValueError(f'Неизвестный статус: {status}')
    verdict = HOMEWORK_STATUSES[status]
    return f'Изменился статус работы "{homework_name}". {verdict}'


def send_message(message):
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(f'Бот отправил сообщение: {message}')
    except ApiTelegramException as e:
        logger.error(f'Сбой при отправке сообщения: {e}')
        raise


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует обязательная переменная окружения')
        sys.exit(1)

    timestamp = 0
    last_error = None
    logger.info('Бот запущен')

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(message)
            else:
                logger.debug('Новых статусов нет')
            timestamp = response.get('current_date', timestamp)
            last_error = None
        except Exception as e:
            logger.error(f'Сбой в работе программы: {e}')
            if last_error != str(e):
                try:
                    send_message(f'Сбой в работе программы: {e}')
                    last_error = str(e)
                except Exception:
                    pass
        time.sleep(600)


if __name__ == '__main__':
    main()
