import os
import pandas as pd
import requests
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
from datetime import datetime
import shutil
import sys

root_csv_path = "./CSV Folder/"
root_img_path = "./Image Folder/" 
csv_file = f"{root_csv_path}image_urls_3_9_2025.csv"
today = datetime.now().strftime("%Y-%m-%d")

# Create a folder to store images
folder_name = f"{root_img_path}instagram img {today}"
os.makedirs(folder_name, exist_ok=True)

# Create sub-folders for human and no human images
human_folder = os.path.join(folder_name, "human")
no_human_folder = os.path.join(folder_name, "no_human")
os.makedirs(human_folder, exist_ok=True)
os.makedirs(no_human_folder, exist_ok=True)

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

# Function to truncate long text
def truncate_text(text, max_length=50):
    """Truncate text to a maximum length and add ellipsis if necessary."""
    return (text[:max_length] + "...") if len(text) > max_length else text

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
                status = f"Converted & Saved: {os.path.basename(jpg_image_name)}"
            else:
                # Save original image
                with open(original_image_name, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                image_path = original_image_name
                status = f"Downloaded: {os.path.basename(original_image_name)}"

            # Check if the image contains a human
            if detect_human(image_path):
                status += " | Human detected"
                # Move image to 'human' folder
                shutil.move(image_path, os.path.join(human_folder, os.path.basename(image_path)))
            else:
                status += " | No human detected"
                # Move image to 'no_human' folder
                shutil.move(image_path, os.path.join(no_human_folder, os.path.basename(image_path)))

        else:
            status = f"Failed to download {truncate_text(image_url)}"

    except Exception as e:
        status = f"Error downloading {truncate_text(image_url)}: {e}"
    
    # Print the status on the same line
    sys.stdout.write(f"\r{status.ljust(80)}")
    sys.stdout.flush()

# Print a newline at the end to avoid overwriting the final status
print()