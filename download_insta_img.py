import os
import pandas as pd
import requests
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
from datetime import datetime

csv_file = "image_urls_3_9_2025.csv"
today = datetime.now().strftime("%Y-%m-%d")

# Create a folder to store images
folder_name = f"instagram img {today}"
os.makedirs(folder_name, exist_ok=True)

# Read CSV file
df = pd.read_csv(csv_file)

# Initialize the HOG descriptor for people detection
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect_human(image_path):
    """Detect humans in the image using HOG+SVM."""
    image = cv2.imread(image_path)
    if image is None:
        return False  # If image can't be loaded, return False
    
    image = cv2.resize(image, (640, 480))  # Resize for faster processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect people in the image
    rects, _ = hog.detectMultiScale(gray, winStride=(4, 4), padding=(8, 8), scale=1.05)

    return len(rects) > 0  # Return True if people are detected

# Loop through each URL and download the image
for index, row in df.iterrows():
    image_url = row['image_urls']  # Adjust column name if needed

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # Get file extension from URL
            parsed_url = urlparse(image_url)
            file_ext = os.path.splitext(parsed_url.path)[-1].lower()

            # If no extension in URL, check Content-Type
            content_type = response.headers.get('Content-Type', '')
            if not file_ext or file_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                if 'jpeg' in content_type:
                    file_ext = '.jpg'
                elif 'png' in content_type:
                    file_ext = '.png'
                elif 'webp' in content_type:
                    file_ext = '.webp'
                else:
                    file_ext = '.jpg'  # Default to .jpg if unknown

            # Generate filename
            original_image_name = f"{folder_name}/image_{index}{file_ext}"
            jpg_image_name = f"{folder_name}/image_{index}.jpg"

            # Read image content into memory
            image = Image.open(BytesIO(response.content))

            # Convert to JPG if necessary
            if file_ext in ['.png', '.webp']:
                image = image.convert("RGB")
                image.save(jpg_image_name, "JPEG", quality=95)
                image_path = jpg_image_name
                print(f"Converted & Saved: {jpg_image_name}")
            else:
                # Save original image
                with open(original_image_name, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                image_path = original_image_name
                print(f"Downloaded: {original_image_name}")

            # Check if the image contains a human
            if detect_human(image_path):
                print(f"Human detected in {image_path}")
            else:
                print(f"No human detected in {image_path}")

        else:
            print(f"Failed to download {image_url}")

    except Exception as e:
        print(f"Error downloading {image_url}: {e}")
