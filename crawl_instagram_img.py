import os
import re
import sys
import time
import shutil
import pickle
import random
import requests
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

target_classes = "x78zum5 xdt5ytf xwrv7xz x1n2onr6 xph46j xfcsdxf xsybdxg x1bzgcud"
instagram_url = "https://www.instagram.com"
instagram_url_with_hashtag = "https://www.instagram.com/explore/search/keyword/?q=%23streetwearfashion"
scroll_limit = 500
today = datetime.now().strftime("%Y-%m-%d")

def random_sleep(min_s, max_s):
    time.sleep(random.randint(min_s, max_s))
    
def initDriverProfile():
    try:
        print("Inititating driver...")
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
        
        print("Driver initiated.")
    except Exception as e:
        print("Error initiating driver: ", e)
        return driver
    
    return driver

def login(driver):
    try:
        print("Loading cookies...")
        driver.get(instagram_url)
        random_sleep(1,2)
        
        cookies = pickle.load(open("my_insta_cookie.pkl","rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.get(instagram_url_with_hashtag)
        random_sleep(3,4)
        
        # Load page again to get rid of pop up
        driver.get(instagram_url_with_hashtag)
        random_sleep(1,2)
        print("Cookies loaded.")
        
    except Exception as e:
        print("Error loading cookies: ", e)
        return driver
    
    return driver

def crawling_html(driver, image_urls):
    # print("Crawling HTML...")
    
    # previous_height = 0
    try:
        for i in range(scroll_limit):
            # Scroll down to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new data to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'img'))
            )
            random_sleep(3,4)
            
            if i % 3 == 0:
                html = driver.page_source
                image_urls = get_images_from_html(html, image_urls)
                print(f"Scrolled {i} times.")
                print(f"Found {len(image_urls)} image URLs...")
            
            # Get the new height
            # new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Break if the height doesn't change
            # if new_height == previous_height:
            #     break
            
            # previous_height = new_height
    except Exception as e:
        print("Error crawling HTML: ", e)
            
    return image_urls

def get_images_from_html(html_content, image_urls):
    if html_content is None:
        print("No HTML content found.")
        return image_urls

    print("Handling HTML content...")

    try:
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        div_element = soup.find('div', class_=target_classes)

        # Find all images within the div and its nested divs
        if div_element:
            images = div_element.find_all('img')
            
            for img in images:
                if 'srcset' in img.attrs:
                    srcset = img['srcset']
                    cleaned_srcset = srcset.replace('&amp;', '&') # Clean up the `srcset` attribute
                    urls = [url.split(' ')[0] for url in cleaned_srcset.split(', ')] # Extract URLs
                    
                    for url in urls:
                        image_urls.add(url)
                elif 'src' in img.attrs:
                    cleaned_src = img['src'].replace('&amp;', '&') # Clean up the `src` attribute
                    image_urls.add(cleaned_src)
                else:
                    print("No image...")
        else:
            print("Target div not found.")
    except Exception as e:
        print("Error handling HTML content: ", e)
    
    return image_urls

if '__main__' == __name__:
    driver = initDriverProfile()
    driver = login(driver)

    # sleep(300)
    random_sleep(3,4)
    
    # Container for the image URLs
    image_urls = set()
    image_urls = crawling_html(driver, image_urls)

    driver.quit()
    
    # Create a DataFrame from the list of URLs
    df = pd.DataFrame(list(image_urls), columns=['image_urls'])
    
    # Remove duplicate URLs
    df = df.drop_duplicates()
    
    print(f"{len(df)} image URLs extracted.")

    # save the DataFrame to a CSV file
    df.to_csv(f"image_urls_{today}.csv", index=False)
    print("Image URLs saved to CSV.")

