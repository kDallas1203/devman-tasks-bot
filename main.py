import requests
import logging
import time
import telegram
import os

logging.basicConfig(filename="sample.log", level=logging.INFO)

DEVMAN_TOKEN = os.environ["DEVMAN_API_TOKEN"]
TG_TOKEN = os.environ["TG_TOKEN"]
BASE_URL = 'https://dvmn.org'
BOT = telegram.Bot(token=TG_TOKEN)


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
        logging.info("Start long_polling")
        params = {}

        if timeout:
            params['timeout'] = timeout

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            review = response.json()
            status = review['status']

            if status == 'found':
                logging.info('New review {}'.format(review))
                for attempt in review['new_attempts']:
                    message = get_review_message(attempt)
                    BOT.send_message(
                        chat_id=os.environ["TG_CHAT_ID"], text=message)
                timeout = review['last_attempt_timestamp']

            if status == 'timeout':
                logging.debug('long_polling timeout')
                timeout = review['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            time.sleep(5)
        except ConnectionError:
            logging.error('Connection error. Attempt to connect...')
            time.sleep(5)


def main():
    long_polling_url = BASE_URL + '/api/long_polling/'
    try:
        start_long_polling(long_polling_url)
    except requests.exceptions.HTTPError as error:
        logging.error("Can't get data from server: %s" % error)


if __name__ == '__main__':
    main()
