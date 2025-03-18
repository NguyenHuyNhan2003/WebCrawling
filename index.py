import re
import time
import shutil
import random
import requests
from time import sleep

from csv_function import save_brands_to_csv, save_product_links_to_csv, save_product_info_to_csv
from csv_function import read_brand_links_from_csv, read_product_links_from_csv
from csv_function import update_csv_with_product_links, update_product_info_csv
from crawler import crawl_brands, crawl_brand_product_links, crawl_product_info
from crawler import initDriverProfile
from crawler import random_sleep

# main functions
def get_brands(driver):
    brand_list = crawl_brands(driver)
    print(f"Got a total of {len(brand_list)} brands")
    
    save_brands_to_csv(brand_list)
    
def get_brand_product_links(driver):
    brand_list = read_brand_links_from_csv()
    total = 0
    
    for brand in brand_list:
        brand_link = brand['brand_link']
        brand_name = brand['brand_name']
            
        # get products of each brand
        print(f"Getting products of {brand_name}")
        product_link_list = crawl_brand_product_links(driver, brand_link, brand_name)
        print(f"Got a total of {len(product_link_list)} product links from {brand_name}")
        total += len(product_link_list)
        
        # save products to CSV
        save_product_links_to_csv(product_link_list, brand_name)
        
        # update_csv_with_product_links(product_link_list, brand_name)
        
        random_sleep()
        
    print(f"Got a total of {total} products")

def process_product_link(driver, brand_name, links):
    product_info_list = []
    counter = 0
    for link in links:
        counter += 1
        print(f"Processing link for {brand_name} ({counter}/{len(links)}): {link['product_link']}")

        product_info = crawl_product_info(driver, link['product_link'])
        product_info['actual_price'] = link['actual_price']
        product_info['discount_price'] = link['discount_price']
        product_info['product_general_img_link'] = link['product_general_img_link']
        
        product_info_list.append(product_info)
        
        random_sleep()
        
    save_product_info_to_csv(product_info_list, brand_name)
    # update_product_info_csv(product_info_list, brand_name)

def process_each_brand_links(driver, product_link):
    for brand_name, links in product_link.items():
        print(f"{brand_name}: {len(links)}")
        
        process_product_link(driver, brand_name, links)
       
def get_product_info(driver):
    product_links = read_product_links_from_csv()
    
    for product_link in product_links:
        process_each_brand_links(driver, product_link)

def test():
    driver = initDriverProfile()
    product_link =[
    'https://www.thegioididong.com/laptop/asus-vivobook-go-15-e1504fa-r5-nj776w?utm_flashsale=1',
    'https://www.thegioididong.com/laptop/dell-inspiron-15-3520-i5-n5i5052w1',
    'https://www.thegioididong.com/laptop/hp-15-fd0234tu-i5-9q969pa'   
    ] 
    
    info = crawl_product_info(driver, product_link[2])
    
    driver.quit()
    
    print(info)

def start(option):
    driver = initDriverProfile()
    
    match option:
        case 1: # get brands
            get_brands(driver)
        case 2: # get products per brand
            get_brand_product_links(driver)
        case 3:# get product info
            get_product_info(driver)   
        case _:
            print("Invalid option")
    
    driver.quit()

if __name__ == "__main__":
    start(1)
    # test()
    
# py index.py   .venv/Scripts/activate