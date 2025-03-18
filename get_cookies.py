import pickle
import os
import re
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
import pandas as pd
import time
import random
import requests
from time import sleep

def random_sleep(min_s, max_s):
    time.sleep(random.randint(min_s, max_s))
    
def initDriverProfile():
    # Đường dẫn đến thư mục chứa file python hiện tại
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Đường dẫn đến file chromedriver.exe
    CHROMEDRIVER_PATH = current_directory + "\chromedriver.exe"
    Service = webdriver.chrome.service.Service(CHROMEDRIVER_PATH)
    Options = webdriver.ChromeOptions()
    Options.add_argument('--no-sandbox')
    Options.add_argument("--disable-blink-features=AutomationControllered")
    Options.add_experimental_option('useAutomationExtension', False)
    prefs = {"profile.default_content_setting_values.notifications": 2}
    Options.add_experimental_option("prefs", prefs)
    Options.add_argument("--disable-dev-shm-usage")
    Options.add_experimental_option("excludeSwitches", ["enable-automation"])
    Options.add_argument("--ignore-certificate-errors")
    Options.add_argument("--disable-web-security")
    Options.add_argument("--allow-running-insecure-content")
    # Ẩn chrome
    Options.add_argument('--disable-headless')
    # không hiển thị thông báo đăng nhập chrome
    Options.add_argument("--disable-infobars")
    # Hiển thị lớn nhất trình duyệt
    Options.add_argument("--start-minimized")
    # không hiển thị thông báo extensions
    Options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(service=Service, options=Options,keep_alive=True)
    return driver

def login(driver, username, password):
    # driver.get("https://www.facebook.com/")
    driver.get("https://www.instagram.com")
    
    # cookies = pickle.load(open("my_insta_cookie.pkl","rb"))
    # for cookie in cookies:
    #     driver.add_cookie(cookie)

    # driver.get("https://www.instagram.com")
    random_sleep(2,3)

driver = initDriverProfile()
login(driver, userName, passWord)


sleep(300)

pickle.dump(driver.get_cookies(), open("my_fb_cookie.pkl","wb"))


driver.quit()