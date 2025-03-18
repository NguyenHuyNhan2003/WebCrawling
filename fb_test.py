import os
import re
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
# from pymongo import MongoClient 
import pandas as pd
import time
import random
import requests
from time import sleep
# from tkinter import *

pageNumber = 3 # number of pages to crawl
today = datetime.now().strftime("%Y-%m-%d")

# def save_csv_to_mongoDB(path):
#     try:
#         # connect to mongodb
#         client = MongoClient(mongoURI)
#         db = client[DATABASE_NAME]
#         collection = db['posts']
#         if client.server_info():
#             print("Connected to MongoDB!")
#         # read excel file
#         df = pd.read_csv(path)
#         data = df.to_dict('records')
#         # insert data to mongodb
#         collection.delete_many({}) #delete old posts
#         collection.insert_many(data)
#         print("Inserted ", len(data), " posts to MongoDB!")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client.close()
#         print("Connection closed!")

def save_to_csv(post_list, filename, folderPath):
    path = folderPath + filename
    if os.path.exists(path):
        # load the existing data from the file
        post_df_full = pd.read_csv(path)
    else:
        # create a new DataFrame if the file doesn't exist
        post_df_full = pd.DataFrame(columns=[])
        
    for post in post_list:
        post_entry = post
        fb_post_df = pd.DataFrame.from_dict(post_entry, orient='index')
        fb_post_df = fb_post_df.transpose()
        post_df_full = pd.concat([post_df_full, fb_post_df], ignore_index=True)

    post_df_full.to_csv(path, index=False)    
    print("Saved ", len(post_list))
    # save_csv_to_mongoDB(path)

def writeFileTxt(fileName, content):
    with open(fileName, 'a') as f1:
        f1.write(content + '\n')

def readData(fileName):
    f = open(fileName, 'r', encoding='utf-8')
    data = []
    for i, line in enumerate(f):
        try:
            line = repr(line)
            line = line[1:len(line) - 3]
            data.append(line)
        except:
            print("err")
    return data

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

def convert_time(t):
    date = t
    try:
        if(len(t) > 10):
            if "yesterday" in t.lower():
                yesterday_date = datetime.now() - timedelta(days=1)
                return yesterday_date.strftime("%d %B %Y at %H:%M:%S")
        
        elif 'h' in t.lower() or "hr" in t.lower() or "hrs" in t.lower():
            hours_to_subract = re.sub(r"\D", '', t)
            date = datetime.today() - timedelta(hours=int(hours_to_subract))
            return date.strftime("%d %B %Y at %H:%M:%S")

        elif 'm' in t.lower() or "min" in t.lower() or "mins" in t.lower():
            minutes_to_subtract = re.sub(r"\D", '', t)
            date = datetime.now() - timedelta(minutes=int(minutes_to_subtract))
            return date.strftime("%d %B %Y at %H:%M:%S")

        elif 's' in t.lower():
            seconds_to_subtract = re.sub(r"\D", '', t)
            date = datetime.now() - timedelta(seconds=int(seconds_to_subtract))
            return date.strftime("%d %B %Y at %H:%M:%S")

        elif 'd' in t.lower() or "ds" in t.lower():
            days_to_subtract = re.sub(r"\D", '', t)
            date = datetime.today() - timedelta(days=int(days_to_subtract))
            return date.strftime("%d %B %Y at %H:%M:%S")

        return date
    except:
        return date

def checkLiveClone(driver):
    try:
        driver.get("https://mbasic.facebook.com/")
        time.sleep(2)
        driver.get("https://mbasic.facebook.com/")
        time.sleep(1)
        elementLive = driver.find_elements(by='name', value="view_post")
        if (len(elementLive) > 0):
            print("Live")
            return True

        return False
    except:
        print("view fb err")
        
def random_sleep(min_s, max_s):
    time.sleep(random.randint(min_s, max_s))

def loginFB(driver, username, password):
    driver.get("https://mbasic.facebook.com/login/?next&ref=dbl&fl&refid=8")
    random_sleep(10,12)
    userNameElement = driver.find_element(By.CSS_SELECTOR,"#email")
    userNameElement.send_keys(username)
    random_sleep(2,3)
    passwordElement = driver.find_element(By.CSS_SELECTOR,"#pass")
    passwordElement.send_keys(password)
    random_sleep(2,3)
    btnSubmit = driver.find_element(By.CSS_SELECTOR,"#loginbutton")
    btnSubmit.click()
    random_sleep(2,3)
    # not_now = driver.find_element(By.CSS_SELECTOR, "#root > table > tbody > tr > td > div > div:nth-child(5) > a")
    # not_now.click()
    print("login success")
    random_sleep(1,2)
    # end login


def getPostsID(driver, idGroup, numberId):
    try:
        fileIds = idGroup + '_ids.csv'
        driver.get('https://mbasic.facebook.com/groups/' + str(idGroup))
        file_exists = os.path.exists(fileIds)
        if (not file_exists):
            writeFileTxt(fileIds, '')

        sumLinks = readData(fileIds)
        while (len(sumLinks) < numberId):
            likeBtn = driver.find_elements(By.XPATH,'//*[contains(@id, "like_")]')
            if len(likeBtn):
                for id in likeBtn:
                    idPost = id.get_attribute('id').replace("like_", "")
                    if (idPost not in sumLinks):
                        sumLinks.append(idPost)
                        writeFileTxt(fileIds, idPost)
                        print(idPost)
            nextBtn = driver.find_elements(By.XPATH,'//a[contains(@href, "?bacr")]')
            if (len(nextBtn)):
                random_sleep(5,7)
                nextBtn[0].click()
            else:
                print('Next btn does not exist !')
                break
    except:
        print('Error')

def clonePostContent(driver, postId, groupname):
    try:
        postData = {"id": postId, "text" : "", "time": "", "post_url": "https://www.facebook.com/groups/" + groupname + "/posts/" + str(postId)}

        driver.get("https://mbasic.facebook.com/groups/" + groupname + "/posts/" + str(postId))

        contentElement = driver.find_elements(By.XPATH,"//div[@data-gt='{\"tn\":\"*s\"}']")
        if (len(contentElement) == 0):
            contentElement = driver.find_elements(By.XPATH,"//div[@data-ft='{\"tn\":\"*s\"}']")
              
        if (len(contentElement)):
            content = contentElement[0].text
            postData["text"] = content
            print("ok text " + postId)  
        else:
            print("No text")
            return False
        posted_time = driver.find_element(By.TAG_NAME, 'abbr').text
        print("ok time " + postId)
        if(len(posted_time)):
            postDate = convert_time(posted_time)
            print(posted_time + ' -> ' +postDate)
            postData["time"] = postDate

        
        return postData
    except:
        print("Fail clone Post" + postId)
        return False
        
def get_ID_List(driver, idGroup):
    try:
        page = 0
        idList = []
        fileIds = idGroup + '_ids.csv'
        driver.get('https://mbasic.facebook.com/groups/' + str(idGroup))
        file_exists = os.path.exists(fileIds)
        if (not file_exists):
            writeFileTxt(fileIds, '')

        sumLinks = readData(fileIds)
        
        while(page < pageNumber):
            likeBtn = driver.find_elements(By.XPATH,'//*[contains(@id, "like_")]')
            if len(likeBtn):
                for id in likeBtn:
                    idPost = id.get_attribute('id').replace("like_", "")
                    if (idPost not in sumLinks):
                        sumLinks.append(idPost)
                        idList.append(idPost)
                        writeFileTxt(fileIds, idPost)
                        print(idPost)
            page += 1
            nextBtn = driver.find_elements(By.XPATH,'//a[contains(@href, "?bacr")]')
            if (len(nextBtn)):
                random_sleep(5,7)
                nextBtn[0].click()
            else:
                print('Next btn does not exist !')
                break
        return idList
    except:
        print("Crawling failed")
        return False
    
def crawlPostData(driver, postIds, group):
    postList = []
    for id in postIds:
        try:
            random_sleep(3,4)
            dataPost = clonePostContent(driver, id, group)
            if (dataPost != False ):
                postList.append(dataPost)   
        except:
            print("Crawling failed")
            return False
    return postList

def is_non_empty_string(input_str):
    # Kiểm tra xem chuỗi có rỗng và không chỉ chứa ký tự trắng hay không
    if input_str and not input_str.isspace():
        return True
    else:
        return False

def crawler(group):
    driver = initDriverProfile()
    isLogin = checkLiveClone(driver)
    print(isLogin)
    
    if(isLogin == False):
        loginFB(driver, userName, passWord)
        
    filename = group + "_" + today + "_posts.csv"
    folderPath = "./result/"
    
    idList = get_ID_List(driver, group)
    postList = crawlPostData(driver, idList, group)
    if(postList != False):
        save_to_csv(postList, filename, folderPath)
        driver.close()
        print('Done!')
        return True
    else:
        driver.close()
        print("Crawling failed")
        return False
        
# def crawl_Button_click(entry, label2):
#     group = entry.get()
#     check_crawl = False
#     if(is_non_empty_string(entry.get())):
#         label2.config(text="Crawling " + group + " ...")
#         check_crawl = crawler(group)
#         if(check_crawl == True):
#             label2.config(text="Crawled " + group + " successfully!")
#         else:
#             label2.config(text="Crawling " + group + " failed!")
#     else:
#         label2.config(text="Please enter a group ID!")

# def Form(win):
#     win.title("Facebook Crawler")
#     win.geometry("500x250")
#     win.configure(bg="white")
#     win.resizable(False, False)
    
#     label = Label(win, text="Facebook Crawler", font=("Arial Bold", 20), bg="white", fg="royalblue")
    
#     entry = Entry(win, width=20, font = ("Aria", 15), bg = "ghostwhite")
    
#     crawlButton = Button(win, text="Crawl", font=("Arial Bold", 10), bg="royalblue", fg="white", command = lambda: crawl_Button_click(entry, label2))
    
#     label2 = Label(win, text="Enter group name (e.g: jobITDaNang): ", font=("Arial Bold", 10), bg="white", fg="black")
    
#     label.pack(pady=20)
#     label2.pack(pady=5)
#     entry.pack(pady=10)
#     crawlButton.pack(pady=5)
    
#     entry.focus()
    
#     win.mainloop()
    
if __name__ == "__main__":
    # win = Tk()
    # Form(win)
    # crawler(group)
    driver = initDriverProfile()
    isLogin = checkLiveClone(driver)
    print(isLogin)
    
    if(isLogin == False):
        loginFB(driver, userName, passWord)
        
    while True:
        print('...')
        sleep(5)
        
    driver.close()
