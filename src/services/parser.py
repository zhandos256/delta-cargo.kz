import re
import json
import sqlite3
import logging
import textwrap
from typing import Optional

import requests

from config.const import DB_FILE_PATH

LOGIN = "87770153025"
PASSWORD = "123124124g"
LOGIN_URL = "https://emir-cargo.kz/login"
BOT_TOKEN = "your_bot_token"
CHAT_ID = 6970529864


def send_notification(msg: str):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    try:
        requests.post(url, data={'chat_id': CHAT_ID, 'text': msg})
    except Exception as e:
        logging.exception("❌ Ошибка при отправке в Telegram:", e)


def init_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track TEXT UNIQUE,
            title TEXT,
            added_at TEXT,
            arrived_at TEXT
        )
    ''')
    conn.commit()
    return conn, cursor


def data_handler(data: Optional[list], cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    if not data:
        return

    for item in data:
        track_code = item["barcode"]
        title = item["title"]
        added_at = item["added_at"]

        # Пытаемся найти warehouse с "ТРЦ «АДК»" и датой
        adk_entry = next(
            (h for h in item["history"]
             if "ТРЦ «АДК»" in h["warehouse"] and h["date"]),
            None
        )

        arrived_at = adk_entry["date"] if adk_entry else None

        # Проверяем, есть ли трек в базе
        cursor.execute('SELECT arrived_at FROM Items WHERE track = ?', (track_code,))
        result = cursor.fetchone()

        if result:
            # Если уже в БД, но еще не было arrived_at → обновим и пушнем
            if not result[0] and arrived_at:
                cursor.execute(
                    'UPDATE Items SET arrived_at = ? WHERE track = ?',
                    (arrived_at, track_code)
                )
                conn.commit()

                msg = textwrap.dedent(f"""
                    📦 Товар поступил в ADK
                    Трек-код: {track_code}
                    Название: {title}
                    Дата: {arrived_at}
                """)
                send_notification(msg.strip())
        else:
            # Вставим даже если arrived_at пока None — БЕЗ пуша
            cursor.execute(
                'INSERT INTO Items(track, title, added_at, arrived_at) VALUES(?, ?, ?, ?)',
                (track_code, title, added_at, arrived_at)
            )
            conn.commit()

            # Если товар уже в ADK — пушнем
            if arrived_at:
                msg = textwrap.dedent(f"""
                    📦 Новый товар в ADK
                    Трек-код: {track_code}
                    Название: {title}
                    Дата: {arrived_at}
                """)
                send_notification(msg.strip())


def main_func():
    session = requests.Session()

    # 2. Логинимся
    payload = {
        'login': LOGIN,
        'password': PASSWORD,
    }

    resp = session.post(LOGIN_URL, data=payload)

    if "logout" not in resp.text:
        logging.info("❌ Ошибка входа")
        return

    # 3. Парсим JSON из this.tracks
    match = re.search(r"this\.tracks\s*=\s*JSON\.parse\('(.+?)'\)", resp.text)
    if not match:
        logging.info("❌ Не найден JSON с треками")
        return

    raw = match.group(1)
    decoded = raw.encode('utf-8').decode('unicode_escape')
    data = json.loads(decoded)

    # 4. Работа с БД
    conn, cursor = init_db()
    data_handler(data, cursor, conn)
    conn.close()
