import requests
import logging
import time
import telegram
import os
from tg_logs_handler import TgLogsHandler

logger = logging.getLogger("telegram_bot")

DEVMAN_TOKEN = os.environ["DEVMAN_API_TOKEN"]
BASE_URL = 'https://dvmn.org'
TG_TOKEN = os.environ["TG_BOT_TOKEN"]
BOT = telegram.Bot(token=TG_TOKEN)


def serialize_attempt(attempt):
    return {
        "title": attempt['lesson_title'],
        "is_negative": attempt['is_negative'],
        "lesson_url": BASE_URL + attempt['lesson_url']
    }

def get_review_message(attempt):
    attempt = serialize_attempt(attempt)
    message = ""

    message += 'У вас проверили работу "{}". {}\n'.format(attempt['title'], attempt['lesson_url'])

    if attempt['is_negative']:
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
        except requests.exceptions.Timeout:
            pass
        except ConnectionError as error:
            logger.error('Bot has error:')
            logging.error(error)
            time.sleep(5)


def main():
    long_polling_url = BASE_URL + '/api/long_polling/'

    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh_formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
    sh.setFormatter(sh_formatter)
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)

    try:
        os.environ["TG_LOGGER_BOT_TOKEN"]
        logger.addHandler(TgLogsHandler())
    except KeyError:
        pass

    try:
        logger.info("Bot started")
        start_long_polling(long_polling_url)
    except requests.exceptions.HTTPError as error:
        logger.error('Bot has error:')
        logger.error(error)


if __name__ == '__main__':
    main()
