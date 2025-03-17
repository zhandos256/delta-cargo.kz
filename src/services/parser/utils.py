import logging

import requests

from config.const import BOT_TOKEN

def send_notification(msg: str):
    chat_id = 6970529864
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={msg}'
    try:
        resp = requests.post(url=url)
    except Exception as e:
        logging.exception(e)