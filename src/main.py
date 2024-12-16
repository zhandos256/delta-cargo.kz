import logging

from const import DEBUG, END_MSG, HEADLESS, LOG_FILE, START_MSG
from other import data_handler, get_data, get_driver, login


def main():
    logging.info(START_MSG)
    driver = get_driver(headless=HEADLESS)
    try:
        login(driver=driver)
        data = get_data(driver=driver)
        data_handler(data)
    except KeyboardInterrupt:
        pass
    finally:
        logging.info(END_MSG)
        driver.quit()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO if not DEBUG else logging.DEBUG,
        filename=LOG_FILE,
        filemode='a'
    )
    main()
