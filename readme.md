# 📦 Cargo Tracker — трекер поступления товаров в ADK

Скрипт для автоматического парсинга сайта emir-cargo.kz, определения момента поступления товара в пункт "Рядом с ТРЦ «АДК»" и отправки уведомлений в Telegram.

## 🚀 Возможности

- Логин на сайт с помощью requests
- Поиск JSON в JavaScript (this.tracks = JSON.parse(...))
- Декодировка и парсинг треков
- Определение момента поступления в ADK
- Сохранение треков в SQLite-базу
- Отправка Telegram-уведомлений только при фактическом прибытии
