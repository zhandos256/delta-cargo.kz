from datetime import datetime
from pathlib import Path
from sys import argv

CURRENT_DATE = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

DEBUG = bool(int(argv[1][-1]))
HEADLESS = bool(int(argv[2][-1]))

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'db.sqlite'
LOGS_DIR = BASE_DIR / 'logs'
LOG_FILE = LOGS_DIR / CURRENT_DATE

MAIN_URL_LOGIN = 'https://emir-cargo.kz/login/'
LOGIN = '87770153025'
PASSWORD = '123124124g'

PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'
PUSHOVEOR_USER_TOKEN = 'u3me4f5hqx9f1r5k3sgforqukxf757'
PUSHOVER_TOKEN = 'a8kjkpyuj1pv3k7wjaj46xgjdiij54'
MAGIC = 'magic'

START_MSG = 'Script started...'
END_MSG = 'Script ended...'
