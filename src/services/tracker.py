import re
import json
import sqlite3
import logging
from typing import Optional, List, Dict, Tuple, Union
from contextlib import closing
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings

logger = logging.getLogger(__name__)

# Типизация данных для ясности
TrackData = Dict[str, Union[str, List[Dict[str, str]]]]

# Настройка повторных попыток для сетевых запросов
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

def send_notification(msg: str) -> None:
    """Отправляет уведомление в Telegram."""
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.CHAT_ID, "text": msg}
    
    try:
        response = session.post(url, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")

def init_db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Инициализирует SQLite базу данных и создаёт таблицу Items."""
    conn = sqlite3.connect(settings.DB_FILE_PATH)
    cursor = conn.cursor()
    
    # Включаем WAL режим для лучшей производительности
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # Создаем таблицу с индексами
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track TEXT UNIQUE,
            title TEXT,
            added_at TEXT,
            arrived_at TEXT
        )
    """)
    
    # Создаем индексы для часто используемых полей
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_track ON Items(track)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrived_at ON Items(arrived_at)")
    
    conn.commit()
    return conn, cursor

def data_handler(data: Optional[List[TrackData]], cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """Обрабатывает данные о треках и обновляет базу."""
    if not data:
        logger.info("Нет данных для обработки")
        return

    # Начинаем транзакцию
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        for item in data:
            track_code = item.get("barcode")
            title = item.get("title")
            added_at = item.get("added_at")
            
            if not all([track_code, title, added_at]):
                logger.warning(f"Пропущена запись с неполными данными: {item}")
                continue

            # Поиск записи с "ТРЦ «АДК»" в истории
            arrived_at = next(
                (h["date"] for h in item.get("history", []) 
                 if "ТРЦ «АДК»" in h.get("warehouse", "") and h.get("date")),
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

                # Уведомление только если товар уже в ADK
                if arrived_at:
                    send_notification(
                        f"📦 Новый товар в ADK\n"
                        f"Трек-код: {track_code}\n"
                        f"Название: {title}\n"
                        f"Дата: {arrived_at}"
                    )
        
        # Подтверждаем транзакцию
        conn.commit()
        
    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        conn.rollback()
        logger.error(f"Ошибка при обработке данных: {e}")
        raise

def main_func() -> None:
    """Основная функция: логинится, парсит треки и обновляет базу."""
    try:
        # Логинимся
        payload = {"login": settings.LOGIN, "password": settings.PASSWORD}
        resp = session.post(settings.LOGIN_URL, data=payload, timeout=10)
        resp.raise_for_status()

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
            decoded = raw.encode().decode("unicode_escape")
            data = json.loads(decoded)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return

        # Обрабатываем данные с базой
        with closing(sqlite3.connect(settings.DB_FILE_PATH)) as conn:
            with conn:
                cursor = conn.cursor()
                init_db()
                data_handler(data, cursor, conn)
                
    except requests.RequestException as e:
        logger.error(f"Ошибка сетевого запроса: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)

if __name__ == "__main__":
    main_func()