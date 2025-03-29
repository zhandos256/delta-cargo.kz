import sys
import logging
import logging.handlers
from pathlib import Path

from config.settings import settings


class CustomFormatter(logging.Formatter):
    """Кастомный форматтер для логов с цветным выводом в консоль."""
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey,
        logging.INFO: grey,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red
    }
    
    def format(self, record):
        if settings.DEBUG and hasattr(record, 'color'):
            color = self.FORMATS.get(record.levelno, self.grey)
            record.msg = f"{color}{record.msg}{self.reset}"
        return super().format(record)


class DuplicateFilter(logging.Filter):
    """Фильтр для предотвращения дублирования логов."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.last_log = {}
    
    def filter(self, record):
        current_log = (record.module, record.levelno, record.msg)
        if current_log != self.last_log.get(record.name):
            self.last_log[record.name] = current_log
            return True
        return False


def setup_logger() -> None:
    """Настраивает логгер с ротацией файлов и форматированием."""
    # Создаем директорию для логов если её нет
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Базовый формат логов
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    
    # Создаем форматтер
    formatter = CustomFormatter(log_format, datefmt)
    
    # Создаем основной логгер
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Добавляем фильтр дубликатов
    duplicate_filter = DuplicateFilter()
    logger.addFilter(duplicate_filter)
    
    if settings.DEBUG:
        # Консольный обработчик для режима отладки
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        # Файловый обработчик с ротацией
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Настраиваем уровень логирования для сторонних библиотек
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    logger.info("Логгер успешно инициализирован")