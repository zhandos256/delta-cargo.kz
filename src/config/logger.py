import sys
import logging

from config.settings import settings


def setup_logger():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    common_params = {
        "level": logging.INFO,
        "format": log_format,
        "datefmt": datefmt,
    }
    if settings.DEBUG:
        common_params["stream"] = sys.stdout
    else:
        common_params["filename"] = settings.LOG_FILE
        common_params["filemode"] = "a"
    logging.basicConfig(**common_params)
    logging.getLogger("apscheduler").setLevel(logging.INFO)