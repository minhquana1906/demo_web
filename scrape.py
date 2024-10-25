import os
import time

import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)

URL = "https://thecoffeehouse.com/collections/all"
WAIT_TIMEOUT = 5

chrome_options = Options()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(options=chrome_options)

driver.get(URL)

SCROLL_PAUSE_TIME = 2
SCROLL_INCREMENT = 400

driver.execute_script("window.scrollTo(0, 0);")
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    previous_scrollY = driver.execute_script("return window.scrollY")
    driver.execute_script(
        f"window.scrollBy( 0, {SCROLL_INCREMENT} )"
    )  # Alternative scroll, a bit slower but reliable
    # html = driver.find_element(By.TAG_NAME, 'html')
    # html.send_keys(Keys.PAGE_DOWN) #Faster scroll, inelegant but works (Could translate to value scroll like above)
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    if previous_scrollY == driver.execute_script("return window.scrollY"):
        break

print("Scrolling is done!")
time.sleep(WAIT_TIMEOUT)

page = BeautifulSoup(driver.page_source, features="html.parser")


prods = page.find_all("div", {"class": "menu_item"})
logger.info(f"Number of prods: {len(prods)}")

products = []

logger.info("Start scraping the products")

for prod in prods:
    try:
        image_div = prod.find("div", class_="menu_item_image")
        if image_div:
            image_tag = image_div.find("img")
            if image_tag:
                image_url = "http:" + image_tag.get("src")
                print(image_url)  # Prints the URL of the image

        menu_item_info = prod.find("div", class_="menu_item_info")
        if menu_item_info:
            product_name = menu_item_info.find("h3").text
            print(product_name)  # Prints the name of the product
            price_text = menu_item_info.find("div", class_="price_product_item").text
            price = int(price_text.replace(".", "").replace(" đ", ""))
            print(price)

        products.append(
            {"product_name": product_name, "price": price, "image_url": image_url}
        )

    except:
        print("Either image's URL or product name or price can not be found, skipped!")

time.sleep(WAIT_TIMEOUT)
driver.quit()

df = pd.DataFrame.from_dict(products)
print(df)

os.makedirs("data", exist_ok=True)
logger.info("Data folder is created")

dest = os.path.join("data", "products.csv")

if os.path.exists(dest):
    df.to_csv(dest, mode="a", index=False, header=True)
    logger.info(f"Data is appended to {dest}")
else:
    df.to_csv(dest, mode="w", index=False, header=True)
    logger.info(f"Data is saved to {dest}")
