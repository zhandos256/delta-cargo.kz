import logging

import requests

from config.const import BOT_TOKEN


def send_notification(msg: str, chat_id: int = 6970529864):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': msg,
        'parse_mode': 'HTML',  # можно использовать HTML или Markdown для форматирования
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status()  # выбросит ошибку, если статус не 200
        logging.info("📨 Уведомление успешно отправлено")
    except Exception as e:
        logging.exception("❌ Ошибка при отправке уведомления в Telegram")