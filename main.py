import requests
import logging
import time
import telegram
import os
from bot import get_bot_instanse
from tg_logs_handler import TgLogsHandler
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("Telegram Bot Logger")
logger.setLevel(logging.INFO)

try:
    os.environ["TG_LOGGER_BOT_TOKEN"]
    logger.addHandler(TgLogsHandler())
except KeyError:
    pass

DEVMAN_TOKEN = os.environ["DEVMAN_API_TOKEN"]
BASE_URL = 'https://dvmn.org'
BOT = get_bot_instanse()


def get_review_message(attempt):
    title = attempt['lesson_title']
    is_negative = attempt['is_negative']
    lesson_url = BASE_URL + attempt['lesson_url']
    message = ""

    message += 'У вас проверили работу "{}". {}\n'.format(title, lesson_url)

    if is_negative:
        message += 'К сожалению в работе нашлись ошибки'
    else:
        message += 'Можно приступать к следующему уроку'

    return message


def start_long_polling(url):
    headers = {"Authorization": "Token {}".format(DEVMAN_TOKEN)}
    timeout = None
    while True:
        params = {}

        if timeout:
            params['timeout'] = timeout

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            review = response.json()
            status = review['status']

            if status == 'found':
                logger.info('New review {}'.format(review))
                for attempt in review['new_attempts']:
                    message = get_review_message(attempt)
                    BOT.send_message(
                        chat_id=os.environ["TG_CHAT_ID"], text=message)
                timeout = review['last_attempt_timestamp']

            if status == 'timeout':
                logger.debug('long_polling timeout')
                timeout = review['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            time.sleep(5)
        except ConnectionError as error:
            logger.error('Бот упал с ошибкой:')
            logging.error(error)
            time.sleep(5)
        except Exception as error:
            logger.error('Бот упал с ошибкой:')
            logger.error(error)


def main():
    long_polling_url = BASE_URL + '/api/long_polling/'
    try:
        logger.info("Бот запущен")
        start_long_polling(long_polling_url)
    except requests.exceptions.HTTPError as error:
        logger.error('Бот упал с ошибкой:')
        logger.error(error)


if __name__ == '__main__':
    main()
