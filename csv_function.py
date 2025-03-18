import os
import re
import csv
import pandas as pd

# csv functions
def save_brands_to_csv(brand_list):
    csv_file = 'brands.csv'
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['brand_name', 'brand_link', 'brand_img_link'])
        writer.writeheader()
        
        for brand in brand_list:
            # write each brand's information to the CSV
            writer.writerow({
                'brand_name': brand['brand_name'],
                'brand_link': brand['brand_link'],
                'brand_img_link': brand['brand_img_link']
            })

    print(f"Data saved to {csv_file}")
    
def save_product_links_to_csv(product_link_list, brand_name):
    csv_file = f"./brand_product_links/{brand_name}_link.csv"
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'actual_price',
            'discount_price',
            'product_link',
            'product_general_img_link'
        ])
        
        writer.writeheader()
        
        # write each product link into the CSV
        for link in product_link_list:
            writer.writerow({
                'actual_price': link['actual_price'],
                'discount_price': link['discount_price'],
                'product_link': link['product_link'],
                'product_general_img_link': link['product_general_img_link']
            })
            
    print(f"Data saved to {csv_file}")
    
def save_product_info_to_csv(product_info_list, brand_name):
    csv_file = f"./brand_product_info/{brand_name}.csv"
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:    
        writer = csv.DictWriter(file, fieldnames=[
            'product_name',
            'actual_price',
            'discount_price',
            'description',
            'processor',
            'ram',
            'storage',
            'graphic_card',
            'display_size',
            'battery',
            'resolution',
            'ports',
            'weight',
            'operating_system',
            'image_link',
            'product_link',
            'product_general_img_link'
        ])
        
        writer.writeheader()
        
        for product in product_info_list:
            # write each product's information to the CSV
            writer.writerow({
                'product_name': product['product_name'],
                'actual_price': product['actual_price'],
                'discount_price': product['discount_price'],
                'description': product['description'],
                'processor': product['processor'],
                'ram': product['ram'],
                'storage': product['storage'],
                'graphic_card': product['graphic_card'],
                'display_size': product['display_size'],
                'battery': product['battery'],
                'resolution': product['resolution'],
                'ports': product['ports'],
                'weight': product['weight'],
                'operating_system': product['operating_system'],
                'image_link': product['image_link'],
                'product_link': product['product_link'],
                'product_general_img_link': product['product_general_img_link']
            })
            
    print(f"Data saved to {csv_file}")
    
def read_brand_links_from_csv():
    csv_file = 'brands.csv'
    brand_list = []
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file) 

        for row in reader:
            brand_list.append({
                'brand_name': row['brand_name'],
                'brand_link': row['brand_link'],
            })
    
    return brand_list

def read_product_links_from_csv():
    product_links = []
    folder_path = './brand_product_links/'
    
    # go through each CSV file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            csv_file_path = os.path.join(folder_path, filename)
            
            # get the brand name from the filename
            brand_name = filename.split('_')[0]
            
            # open each CSV file and read the links
            with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                # skip the header
                next(reader)
                
                # get all links in the file
                file_info = [
                    {
                        'actual_price': row[0],
                        'discount_price': row[1],
                        'product_link': row[2],
                        'product_general_img_link': row[3]
                    }
                    for row in reader if row
                ]
                product_links.append({brand_name: file_info})
                
    return product_links

def update_csv_with_product_links(product_link_list, brand_name):
    csv_file = f"./brand_product_links/{brand_name}_link.csv"
    existing_data = {}

    # Load existing data if the file exists
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_data[row['product_link']] = row

    # Update actual_price and discount_price for existing product
    for product in product_link_list:
        if product['product_link'] in existing_data:
            # Update the prices for existing product
            existing_data[product['product_link']]['actual_price'] = product['actual_price']
            existing_data[product['product_link']]['discount_price'] = product['discount_price']

    # Write updated data back to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'actual_price',
            'discount_price',
            'product_link',
            'product_general_img_link'
        ])
        writer.writeheader()
        writer.writerows(existing_data.values())
    
    print(f"Updated data saved to {csv_file}")
    
def update_product_info_csv(product_info_list, brand_name):
    csv_file = f"./brand_product_info/{brand_name}.csv"
    existing_data = {}

    # Load existing data if the file exists
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_data[row['product_link']] = row

    # Update or add product information
    for product in product_info_list:
        if product['product_link'] in existing_data:
            # Update fields for existing product
            existing_data[product['product_link']]['actual_price'] = product['actual_price']
            existing_data[product['product_link']]['discount_price'] = product['discount_price']
            existing_data[product['product_link']]['product_general_img_link'] = product['product_general_img_link']

    # Write updated data back to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'product_name',
            'actual_price',
            'discount_price',
            'description',
            'processor',
            'ram',
            'storage',
            'graphic_card',
            'display_size',
            'battery',
            'resolution',
            'ports',
            'weight',
            'operating_system',
            'image_link',
            'product_link',
            'product_general_img_link'
        ])
        
        writer.writeheader()
        writer.writerows(existing_data.values())
    
    print(f"Updated data saved to {csv_file}")