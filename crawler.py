import os
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

webpage_url = 'https://www.thegioididong.com/laptop' #'https://cellphones.com.vn/laptop.html'

def random_sleep():
    sleep(random.randint(2, 5))

def element_xpath_exists(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
        return True  # Element exists
    except NoSuchElementException:
        return False  # Element does not exist
    
def element_class_name_exists(driver, class_name):
    try:
        driver.find_element(By.CLASS_NAME, class_name)
        return True  # Element exists
    except NoSuchElementException:
        return False  # Element does not exist

# webcrawler functions
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

def crawl_brands(driver):
    brand_list = []
    
    driver.get(webpage_url)
    
    wait = WebDriverWait(driver, 10)
    
    brands = wait.until(EC.presence_of_all_elements_located((
        By.XPATH, '//*[@id="wrapper"]/div[2]/div[2]/div/a'
        #'//*[@id="layout-desktop"]/div[3]/div[2]/div/div[4]/div[1]/div/a'
    )))
    
    print(f"Found {len(brands)} brands")
    
    for brand in brands:
        try:
            # link to brand laptop
            brand_link = brand.get_attribute('href')
            
            # brand logo link
            img_tag = brand.find_element(By.TAG_NAME, 'img')
            brand_img_link = img_tag.get_attribute('src')
            
            # brand name
            brand_name = img_tag.get_attribute('alt')
            
            # append to list
            brand_list.append({
                'brand_name': brand_name, 
                'brand_link': brand_link, 
                'brand_img_link': brand_img_link
            })
        except Exception as e:
            print(f"Error processing brand: {e}")
            continue
        
    return brand_list

def crawl_brand_product_links(driver, brand_link, brand_name):
    product_link_list = []
    product_link = ''
    actual_price = ''
    discount_price = ''
    
    driver.get(brand_link)
    
    wait = WebDriverWait(driver, 10)
    
    # display full product page
    try_count = 0
    while(True):
        try:
            
            show_more_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="categoryPage"]/div[1]/div[2]/a'
                #'//*[@id="layout-desktop"]/div[3]/div[2]/div/div[4]/div[5]/div/div[2]/a'
            )))
            show_more_button.click()
            
            if try_count > 20:
                break
            
            try_count += 1
            random_sleep()
            
        except Exception as e:
            break
    
    # get all product containers
    product_container = wait.until(EC.presence_of_all_elements_located((
        By.XPATH, '//*[@id="categoryPage"]/div[1]/ul/li'

    )))

    for product in product_container:
        # get product link
        product_link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
        
        # get general image link
        img_item = product.find_element(By.CLASS_NAME, 'item-img')
        img_tag = img_item.find_elements(By.TAG_NAME, 'img')[0]
        product_general_img_link = img_tag.get_attribute('src')
        
        # get price
        actual_price = product.find_element(By.CLASS_NAME, 'price').text
        discount_price = actual_price
        
        if element_class_name_exists(product, 'price-old'):
            actual_price = product.find_element(By.CLASS_NAME, 'price-old').text
            
        product_link_list.append({
            'product_link': product_link,
            'actual_price': actual_price,
            'discount_price': discount_price,
            'product_general_img_link': product_general_img_link
        })
        
    return product_link_list

def crawl_cpu(driver, specification_box, wait):
    cpu = ''
    try:
        specification_box.click()
    
        ul = specification_box.find_element(By.TAG_NAME, 'ul')
        li_list = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_list:
            aside_tags = li.find_elements(By.TAG_NAME, 'aside')
            title = aside_tags[0].text
            detail = aside_tags[1].text
            cpu += f"{title}: {detail}\n"
        
    except Exception as e:
        print(f"Error getting CPU: {e}")
        
    return cpu

def crawl_ram_and_storage(driver, specification_box, wait):
    ram = ''
    storage = ''
    try:
        specification_box.click()
    
        ul = specification_box.find_element(By.TAG_NAME, 'ul')
        li_list = ul.find_elements(By.TAG_NAME, 'li')
        # the last li is storage
        storage_li = li_list[-1]
        storage_aside_tags = storage_li.find_elements(By.TAG_NAME, 'aside')
        storage += f"{storage_aside_tags[0].text}: {storage_aside_tags[1].text}\n"
        
        for li in li_list[:-1]:
            aside_tags = li.find_elements(By.TAG_NAME, 'aside')
            title = aside_tags[0].text
            detail = aside_tags[1].text
            ram += f"{title}: {detail}\n"
        
    except Exception as e:
        print(f"Error getting RAM and Storage: {e}")
        
    return ram, storage

def crawl_graphic_card(driver, specification_box, wait):
    graphic_card = ''
    try:
        specification_box.click()
    
        ul = specification_box.find_element(By.TAG_NAME, 'ul')
        li_list = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_list:
            aside_tags = li.find_elements(By.TAG_NAME, 'aside')
            if aside_tags[0].text == 'Card màn hình:':
                graphic_card += aside_tags[1].text
        
    except Exception as e:
        print(f"Error getting graphic card: {e}")
        
    return graphic_card

def crawl_display_size_and_resolution(driver, specification_box, wait):
    display_size = ''
    resolution = ''
    try:
        specification_box.click()
    
        ul = specification_box.find_element(By.TAG_NAME, 'ul')
        li_list = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_list:
            aside_tags = li.find_elements(By.TAG_NAME, 'aside')
            if aside_tags[0].text == 'Màn hình:':
                display_size += aside_tags[1].text
                
            if aside_tags[0].text == 'Độ phân giải:':
                resolution += aside_tags[1].text
    except Exception as e:
        print(f"Error getting display size and resolution: {e}")
    
    return display_size, resolution

def crawl_ports(driver, specification_box, wait):
    ports = ''
    try:
        specification_box.click()
    
        ul = specification_box.find_element(By.TAG_NAME, 'ul')
        li_list = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_list:
            aside_tags = li.find_elements(By.TAG_NAME, 'aside')
            if aside_tags[0].text == 'Cổng giao tiếp:':
                ports += aside_tags[1].text
    except Exception as e:
        print(f"Error getting ports: {e}")
        
    return ports

def crawl_battery_and_os(driver, specification_box, wait):
    battery = ''
    operating_system = ''
    try:
        specification_box.click()
    
        ul = specification_box.find_element(By.TAG_NAME, 'ul')
        li_list = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_list:
            aside_tags = li.find_elements(By.TAG_NAME, 'aside')
            if aside_tags[0].text == 'Thông tin Pin:':
                battery += aside_tags[1].text
                
            if aside_tags[0].text == 'Hệ điều hành:':
                operating_system += aside_tags[1].text
                
    except Exception as e:
        print(f"Error getting battery and OS: {e}")
    
    return battery, operating_system

def crawl_weight(driver, specification_box, wait):
    weight = ''
    try:
        specification_box.click()
    
        ul = specification_box.find_element(By.TAG_NAME, 'ul')
        li_list = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_list:
            aside_tags = li.find_elements(By.TAG_NAME, 'aside')
            if aside_tags[0].text == 'Khối lượng tịnh:':
                weight += aside_tags[1].text
                
    except Exception as e:
        print(f"Error getting weight: {e}")
        
    return weight

def crawl_product_description(driver, product_link):
    # description
    driver.get(product_link)
    wait = WebDriverWait(driver, 20)
    
    product_description = ''
    try:
        xpath = '//*[@id="tab-spec"]/h2[2]'
        button_desc_click = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button_desc_click.click()
        
        xpath = '//*[@id="tab-2"]/div/a/span'
        see_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        see_more_button.click()
        
        class_name = 'text-detail.expand'
        description_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        h3_tags = description_container.find_elements(By.TAG_NAME, 'h3')
        
        for h3 in h3_tags:
            h3_text = h3.text
            # print(f"H3 Text: {h3_text}")
            product_description += f"Title: {h3_text}\n"
            
            # get the next sibling of h3 stop if it is a h3 tag
            next_element = h3
            while True:
                try:
                    next_element = next_element.find_element(By.XPATH, 'following-sibling::*')
                    if next_element.tag_name == 'h3':
                        break
                    product_description += f"Detail: {next_element.text}\n"
                except Exception as e:
                    break
    except Exception as e:
        print(f"Error getting description: {e}")
        
    # print(product_description)
    return product_description

def crawl_product_info(driver, product_link):
    driver.get(product_link)
    wait = WebDriverWait(driver, 20)
    
    # initialize variables
    # name
    product_name = ''
    actual_price = ''
    discount_price = ''
    # description
    product_description = ''
    # specifications
    product_processor = ''
    product_ram = ''
    product_storage = ''
    product_graphic_card = ''
    product_display_size = ''
    product_battery = ''
    product_resolution = ''
    product_ports = ''
    product_operating_system = ''
    product_weight = ''
    # image link
    product_image_link = ''
    product_general_img_link = ''

    # product name
    try:
        product_name = wait.until(EC.presence_of_element_located((
            By.XPATH, '/html/body/section/div[1]/h1'
        ))).text
    except Exception as e:
        print(f"Error getting product name: {e}")
    
    # print(product_name)
    
    # image link
    try:
        click_image_slider = driver.find_element(By.CLASS_NAME, 'owl-dot.dotnumber2.img')
        click_image_slider.click()
        
        owl_items = driver.find_elements(By.XPATH, '//*[@id="slider-default"]/div[1]/div/div')
        for item in owl_items:
            image_src = item.find_element(By.TAG_NAME, 'img').get_attribute('src')
            product_image_link += f"{image_src} và\n"
            try:
                next_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="slider-default"]/div[2]/button[2]'
                )))
                next_button.click()
                
            except Exception as e:
                print('')
            
    except Exception as e:
        print(f"Error getting image link: {e}")
    
    # specifications
    try:
        # navigate to specifications tab
        class_name = 'specification-item'
        specification_tab = driver.find_element(By.CLASS_NAME, class_name)
        specification_boxes = specification_tab.find_elements(By.CLASS_NAME, 'box-specifi')
        # print(f"Found {len(specification_boxes)} specification boxes") 
        
        # cpu
        product_processor = crawl_cpu(driver, specification_boxes[0], wait)
        
        # ram & storage
        product_ram, product_storage = crawl_ram_and_storage(driver, specification_boxes[1], wait)
        
        # graphic card
        product_graphic_card = crawl_graphic_card(driver, specification_boxes[3], wait)
        
        # display size & resolution
        product_display_size, product_resolution = crawl_display_size_and_resolution(driver, specification_boxes[2], wait)
        
        # ports
        product_ports = crawl_ports(driver, specification_boxes[4], wait)
        
        # weight
        product_weight = crawl_weight(driver, specification_boxes[5], wait)
        
        # battery & operating system
        product_battery, product_operating_system = crawl_battery_and_os(driver, specification_boxes[6], wait)

    except Exception as e:
        print(f"Error getting specifications: {e}")
        
    product_description = crawl_product_description(driver, product_link)
    
    return {
        'product_name': product_name,
        'actual_price': actual_price,
        'discount_price': discount_price,
        'description': product_description,
        'processor': product_processor, # CPU 
        'ram': product_ram, # Dung lượng RAM 
        'storage': product_storage, # Ổ cứng 
        'graphic_card': product_graphic_card, # Loại card đồ họa 
        'display_size': product_display_size, # Kích thước màn hình 
        'battery': product_battery, # Pin
        'resolution': product_resolution, # Độ phân giải màn hình 
        'ports': product_ports, # Cổng giao tiếp 
        'weight': product_weight, # Khối lượng
        'operating_system': product_operating_system, # Hệ điều hành
        'image_link': product_image_link,
        'product_link': product_link,
        'product_general_img_link': product_general_img_link
    }