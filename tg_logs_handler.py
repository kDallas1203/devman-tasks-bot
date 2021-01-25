import logging
import os
from bot import get_bot_instanse

class TgLogsHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = get_bot_instanse()


    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=os.environ["TG_CHAT_ID"], text=log_entry)
    

