import os
import telegram 

def get_bot_instanse():
    TG_TOKEN = os.environ["TG_TOKEN"]
    return telegram.Bot(token=TG_TOKEN)