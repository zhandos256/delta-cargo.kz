from config.const import HEADLESS
from services.parser.other import data_handler, get_data, get_driver, login


def run_parser():
    driver = get_driver(headless=HEADLESS)
    try:
        login(driver=driver)
        data = get_data(driver=driver)
        data_handler(data)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()
