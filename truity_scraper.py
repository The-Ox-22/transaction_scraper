from selenium import webdriver 
from selenium.webdriver.common.by import By
from datetime import datetime
import os
from dotenv import load_dotenv
import csv 


def init_headless_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.accept_insecure_certs = False 
    options.headless = True # doesnt seem to actually work.. maybe try some of the below?
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless=new") # for Chrome >= 109
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    return webdriver.Chrome(options=options)


def login_to_truity(driver: webdriver.Chrome, username: str, passcode: str):
    driver.set_window_size(1280, 972)
    driver.get("https://secure.truitycu.org/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.TAG_NAME, "jha-button").submit()

    driver.find_element(By.CLASS, 'password-container').find_element(By.TAG_NAME, 'input').send_keys(passcode)

    # driver.find_element(By.TAG_NAME, 'bannoweb-login').find_element(By.TAG_NAME, 'bannoweb-login-steps')
    # driver.find_element(By.ID, "password").send_keys(passcode)
    # driver.find_element(By.TAG_NAME, "jha-button").submit()

if __name__ == '__main__':
    load_dotenv()
    driver = init_headless_driver()
    login_to_truity(driver, os.environ.get('TRUITY_USER'), os.environ.get('TRUITY_PASSWORD'))
