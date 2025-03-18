from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
from bs4 import BeautifulSoup 

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

def get_all_products():
    webpage_url = 'https://www.thegioididong.com/dtdd'
    driver = initDriverProfile()
    driver.get(webpage_url)
    wait = WebDriverWait(driver, 10)

    while True:
        try:
            time.sleep(1)
            see_more_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "see-more-btn"))
            )
            time.sleep(2)
            see_more_button.click()

        except Exception as e:
            print("No more 'See More' button found or error:", e)
            break
        
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    product_list = []
    product_containers = soup.find('div', class_='container-productbox').find_all('li')

    for product in product_containers:
        link_tag = product.find('a')
        if link_tag and link_tag.get('href'):
            link = 'https://www.thegioididong.com' + link_tag.get('href') 
            product_list.append({'product_link': link})
            
    with open('product_links.txt', "w", encoding="utf-8") as file:
        for product in product_list:
            file.write(product["product_link"] + "\n")

    return product_list

def get_product_review_info(product_link):
    driver = initDriverProfile()
    driver.get(product_link)
    wait = WebDriverWait(driver, 10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_info = {
        'product_link': product_link,
        'product_name': soup.find('h1', class_='name').text,
    }
    
    comments_button = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "cmt-count"))
    )

    return product_info

all_products = get_all_products()