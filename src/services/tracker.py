import re
import json
import sqlite3
import logging
from typing import Optional, List, Dict, Tuple, Union

# Тип данных для треков
from contextlib import closing

import requests
from requests import Session

from config.settings import settings

logger = logging.getLogger(__name__)

# Типизация данных для ясности
TrackData = Dict[str, Union[str, List[Dict[str, str]]]]


def send_notification(msg: str) -> None:
    """Отправляет уведомление в Telegram."""
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.CHAT_ID, "text": msg}
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()  # Проверяем статус ответа
    except requests.RequestException as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")


def init_db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Инициализирует SQLite базу данных и создаёт таблицу Items."""
    conn = sqlite3.connect(settings.DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track TEXT UNIQUE,
            title TEXT,
            added_at TEXT,
            arrived_at TEXT
        )
    """)
    conn.commit()
    return conn, cursor


def data_handler(data: Optional[List[TrackData]], cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """Обрабатывает данные о треках и обновляет базу."""
    if not data:
        logger.info("Нет данных для обработки")
        return

    for item in data:
        track_code = item["barcode"]
        title = item["title"]
        added_at = item["added_at"]

        # Поиск записи с "ТРЦ «АДК»" в истории
        arrived_at = next(
            (h["date"] for h in item["history"] if "ТРЦ «АДК»" in h["warehouse"] and h["date"]),
            None,
        )

        # Проверка наличия трека в базе
        cursor.execute("SELECT arrived_at FROM Items WHERE track = ?", (track_code,))
        result = cursor.fetchone()

        if result:
            # Обновляем, если arrived_at появился
            if not result[0] and arrived_at:
                cursor.execute(
                    "UPDATE Items SET arrived_at = ? WHERE track = ?",
                    (arrived_at, track_code),
                )
                conn.commit()
                send_notification(
                    f"📦 Товар поступил в ADK\n"
                    f"Трек-код: {track_code}\n"
                    f"Название: {title}\n"
                    f"Дата: {arrived_at}"
                )
        else:
            # Добавляем новую запись
            cursor.execute(
                "INSERT OR IGNORE INTO Items (track, title, added_at, arrived_at) VALUES (?, ?, ?, ?)",
                (track_code, title, added_at, arrived_at),
            )
            conn.commit()

            # Уведомление только если товар уже в ADK
            if arrived_at:
                send_notification(
                    f"📦 Новый товар в ADK\n"
                    f"Трек-код: {track_code}\n"
                    f"Название: {title}\n"
                    f"Дата: {arrived_at}"
                )


def main_func() -> None:
    """Основная функция: логинится, парсит треки и обновляет базу."""
    with Session() as session:
        # Логинимся
        payload = {"login": settings.LOGIN, "password": settings.PASSWORD}
        try:
            resp = session.post(settings.LOGIN_URL, data=payload, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Ошибка входа: {e}")
            return

        if "logout" not in resp.text:
            logger.error("Не удалось войти: 'logout' не найден в ответе")
            return

        # Парсим JSON
        match = re.search(r"this\.tracks\s*=\s*JSON\.parse\('(.+?)'\)", resp.text)
        if not match:
            logger.error("JSON с треками не найден")
            return

        raw = match.group(1)
        try:
            decoded = raw.encode().decode("unicode_escape")  # Упрощаем обработку escape-последовательностей
            data = json.loads(decoded)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return

        # Обрабатываем данные с базой
        with closing(sqlite3.connect(settings.DB_FILE_PATH)) as conn:
            with conn:  # Автоматический commit/rollback
                cursor = conn.cursor()
                init_db()  # Убедимся, что таблица есть
                data_handler(data, cursor, conn)


if __name__ == "__main__":
    main_func()