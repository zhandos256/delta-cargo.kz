import logging
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from const import LOGIN, MAIN_URL_LOGIN, PASSWORD
from db import TinyDB
from utils import send_notification


def get_driver(headless: bool = False):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--disable-blink-features")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(options=opts)


def login(driver: WebDriver):
    try:
        driver.get(url=MAIN_URL_LOGIN)
        login_input = driver.find_element(
            by=By.XPATH, value='//*[@id="login"]')
        if login_input:
            login_input.send_keys(LOGIN)
        password_input = driver.find_element(
            by=By.XPATH, value='//*[@id="password"]')
        if password_input:
            password_input.send_keys(PASSWORD)
        sign_button = driver.find_element(
            by=By.XPATH, value='/html/body/div/main/div/form/button')
        if sign_button:
            sign_button.click()
    except Exception as e:
        logging.debug(e)


def get_data(driver: WebDriver) -> Optional[list[list[str]]]:
    data = []
    card = None
    try:
        card = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[7]/div[1]')))
    except TimeoutException as e:
        logging.exception(e)
        return
    if card:
        for i in range(1, 100):
            try:
                el = driver.find_element(
                    by=By.XPATH, value=f'//*[@id="app"]/div[7]/div[{i}]')
                data.append([el.text.split('\n')])
            except NoSuchElementException as e:
                logging.debug(e)
                break
    logging.info(f'Founded {len(data)} tracks')
    return data if len(data) > 0 else None


def data_handler(data: Optional[list[list[str]]]):
    if not data:
        return
    else:
        db = TinyDB()
        for j in data:
            db.cursor.execute(
                'SELECT TRACK FROM Items WHERE track = ?', (j[0][0],))
            track = db.cursor.fetchone()
            if track is None and j[0][7] != 'нет данных':
                db.cursor.execute(
                    'INSERT INTO Items(track) VALUES(?)', (j[0][0],))
                db.conn.commit()
                import textwrap
                msg = textwrap.dedent(f"""
            Товар поступил на склад Алматы
            Трэк-код: {j[0][0]}
            Товар: {j[0][1]}
            Дата: {j[0][7]}
          """)
                send_notification(msg=msg)
