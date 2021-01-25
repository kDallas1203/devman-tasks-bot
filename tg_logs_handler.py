import logging
import os
import telegram

class TgLogsHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TG_TOKEN = os.environ["TG_LOGGER_BOT_TOKEN"]
        self.bot = telegram.Bot(token=TG_TOKEN)

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.bot.send_message(chat_id=os.environ["TG_CHAT_ID"], text=log_entry)
        except Exception as error:
            print('Logger bot send message error:', error)
    

