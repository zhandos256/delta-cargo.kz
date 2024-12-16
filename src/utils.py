import requests

from const import MAGIC, PUSHOVEOR_USER_TOKEN, PUSHOVER_TOKEN, PUSHOVER_URL


def send_notification(msg: str) -> bool:
    payload = {
        'token': PUSHOVER_TOKEN,
        'user': PUSHOVEOR_USER_TOKEN,
        'message': msg,
        'sound': MAGIC
    }
    resp = requests.post(url=PUSHOVER_URL, data=payload)
    return resp.status_code
