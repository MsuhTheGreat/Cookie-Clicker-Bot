from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import threading
import time

CHROME_PROFILE_PATH = r"C:\Users\Global Computers\AppData\Local\Google\Chrome\User Data"
URL = "https://orteil.dashnet.org/cookieclicker/"
SLEEP_TIME = 0.01
with open("upgrades_click_sleep_time.txt", mode="r") as file:
    UPGRADES_CLICK_SLEEP_TIME = float(file.read())
with open("products_click_sleep_time.txt", mode="r") as file:
    PRODUCTS_CLICK_SLEEP_TIME = float(file.read())

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
chrome_options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome(options=chrome_options)
driver.get(url=URL)

time.sleep(10)

cookie = driver.find_element(By.ID, "bigCookie")


def click_cookie() -> None:
    global cookie
    global UPGRADES_CLICK_SLEEP_TIME
    global PRODUCTS_CLICK_SLEEP_TIME
    
    while True:
        try:
            cookie.click()
        except StaleElementReferenceException:
            cookie = driver.find_element(By.ID, "bigCookie")
        
        UPGRADES_CLICK_SLEEP_TIME += SLEEP_TIME
        PRODUCTS_CLICK_SLEEP_TIME += SLEEP_TIME
        
        with open("upgrades_click_sleep_time.txt", mode="w") as file:
            file.write(str(UPGRADES_CLICK_SLEEP_TIME))
        with open("products_click_sleep_time.txt", mode="w") as file:
            file.write(str(PRODUCTS_CLICK_SLEEP_TIME))
        
        time.sleep(0.05)


def buy_upgrades() -> None:
    while True:
        try:
            upgrades = driver.find_elements(By.CSS_SELECTOR, ".crate.upgrade.enabled")
            upgrades = upgrades[::-1]
            if len(upgrades) != 0:
                for upgrade in upgrades:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", upgrade)
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(upgrade))
                        upgrade.click()
                    except StaleElementReferenceException:
                        continue
        except Exception as e:
            print(f"Error Occured During Upgrades Purchase: {e}")
        
        time.sleep(UPGRADES_CLICK_SLEEP_TIME)


def buy_products() -> None:
    while True:
        try:
            products = driver.find_elements(By.CSS_SELECTOR, ".product.unlocked.enabled")
            products = products[::-1]
            if len(products) != 0:
                for product in products:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", product)
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(product))
                        product.click()
                    except StaleElementReferenceException:
                        continue
        except Exception as e:
            print(f"Error Occured During Products Purchase: {e}")
        
        time.sleep(PRODUCTS_CLICK_SLEEP_TIME)


def click_golden_cookie() -> None:
    while True:
        try:
            golden_cookie = driver.find_element(By.CSS_SELECTOR, ".shimmer")
            golden_cookie.click()
            print("Golden Cookie Found And Clicked!")
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        time.sleep(SLEEP_TIME)


cookie_click_thread = threading.Thread(target=click_cookie)
upgrade_purchasing_thread = threading.Thread(target=buy_upgrades)
product_purchasing_thread = threading.Thread(target=buy_products)
golden_cookie_click_thread = threading.Thread(target=click_golden_cookie)

cookie_click_thread.start()
upgrade_purchasing_thread.start()
product_purchasing_thread.start()
golden_cookie_click_thread.start()