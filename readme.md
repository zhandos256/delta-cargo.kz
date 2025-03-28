# 📦 Cargo Tracker — Трекер поступления товаров в ADK

Скрипт для автоматического мониторинга сайта ```emir-cargo.kz```, отслеживания поступления товаров в пункт "Рядом с ТРЦ «АДК»" и отправки уведомлений в Telegram.

## 🚀 Возможности

- 🔐 Авторизация на сайте через ```requests``` с использованием логина и пароля.
- 🔎 Парсинг JSON-данных о треках из ```<script>this.tracks = JSON.parse(...)</script>.```
- 🔁 Декодирование строк с ```unicode_escape``` для корректной обработки данных.
- 📍 Определение прибытия товара в пункт "Рядом с ТРЦ «АДК»" на основе поля ```warehouse```.
- 💾 Хранение данных о треках в SQLite базе (```cargo.db```) с учётом истории.
- 📲 Отправка уведомлений в Telegram только при подтверждённом прибытии товара.
- ⏰ Планирование задач через ```APScheduler``` для автоматического периодического запуска.

## 📦 Структура проекта

```text
├── jobs.db              # База данных для хранения заданий APScheduler (SQLite)
├── cargo.db             # База данных для треков товаров (SQLite)
├── logs/                # Директория для логов (файлы вида YYYY-MM-DD.log)
├── README.md            # Документация проекта
├── requirements.txt     # Зависимости проекта (Python-пакеты)
├── run.sh               # Bash-скрипт для запуска приложения
└── src/
    ├── bot.py           # Точка входа: запуск бота и планировщика
    ├── config/
    │   ├── logger.py    # Настройка логирования (консоль/файл с ротацией)
    │   ├── scheduler.py # Конфигурация APScheduler (асинхронный планировщик)
    │   └── settings.py  # Настройки проекта (переменные окружения из .env)
    ├── handlers/
    │   └── start.py     # Обработчик команды /start для Telegram-бота
    └── services/
        └── tracker.py   # Логика парсинга сайта и обработки данных
```

## ⚙️ Установка

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/yourusername/cargo-tracker.git
    cd cargo-tracker
    ```

2. Создайте виртуальное окружение:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Настройте переменные окружения: Создайте файл ```.env``` в корне проекта со следующим содержимым:

    ```text
    LOGIN=your_login
    PASSWORD=your_password
    BOT_TOKEN=your_telegram_bot_token
    CHAT_ID=your_telegram_chat_id
    DEBUG=False  # Установите True для вывода логов в консоль
    ```

## 🚀 Запуск

1. Через Bash-скрипт: Убедитесь, что ```run.sh``` исполняемый:

    ```bash
    chmod +x run.sh
    ./run.sh
    ```

    Пример ```run.sh```:

    ```bash
    #!/bin/bash

    source venv/bin/activate
    python src/bot.py
    ```

2. Напрямую:

    ```bas
    python src/bot.py
    ```

    Скрипт автоматически запускает планировщик, который проверяет сайт каждые 5 минут (настраивается в ```src/bot.py```).

## 📋 Пример работы

- Скрипт логинится на emir-cargo.kz.
- Парсит треки из JSON в HTML.
- Сохраняет данные в ```cargo.db```
- Если товар прибыл в "ТРЦ «АДК»", отправляет сообщение в Telegram:

    ```text
    📦 Товар поступил в ADK
    Трек-код: ABC123456789
    Название: Смартфон XYZ
    Дата: 2025-03-27 14:30:00
    ```

## 📦 Зависимости

Содержимое ```requirements.txt:```

```text
requests==2.31.0
pydantic==2.6.4
pydantic-settings==2.2.1
aiogram==3.4.1
apscheduler==3.10.4
sqlalchemy==2.0.28
```
