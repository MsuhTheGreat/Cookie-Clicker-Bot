import os
import shutil
import time
import threading
from random import randint
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import psutil
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
if not os.path.exists(".env"):
    print("⚠️ .env file not found. Using default values.")
load_dotenv(".env")

# Constants
URL = "https://orteil.dashnet.org/cookieclicker/"
CHROME_DATA_DIR = os.getenv("CHROME_DATA_DIR")
CHROME_PROFILE = os.getenv("CHROME_PROFILE")
CHROME_PATH = os.getenv("CHROME_PATH", "chrome.exe")
SLEEP_TIME = 0.01
WAIT_TIME = 60


def load_or_initialize(filename, default=0.0):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(str(default))
    with open(filename, "r") as f:
        return float(f.read())


def create_new_profile():
    """Creates a new Chrome profile using Chrome's command line."""
    chrome_path = Path(CHROME_PATH)
    chrome_data_dir = Path(CHROME_DATA_DIR)
    chrome_profile = Path(CHROME_PROFILE)

    profile_path = chrome_data_dir \ chrome_profile

    # Ensure we have the proper directory
    if not os.path.exists(chrome_data_dir):
        os.makedirs(chrome_data_dir)

    # Remove old profile if it exists
    if os.path.exists(profile_path):
        shutil.rmtree(profile_path)

    print(f"Creating Chrome profile: {chrome_profile}")
    try:
        subprocess.run([
            f"{chrome_path}",
            f"--user-data-dir={chrome_data_dir}",
            f"--profile-directory={chrome_profile}",
            "--headless",
            "--disable-gpu",
            "about:blank"
        ], timeout=30, check=True)
        print(f"Profile {chrome_profile} created successfully!")
    except Exception as e:
        print(f"Error running subprocess: {e}")


def kill_chrome_processes():
    """Kill any running Chrome processes."""
    try:
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():
                proc.kill()
                print(f"Killed Chrome process: {proc.info['pid']}")

    except psutil.NoSuchProcess as e:
        print(f"Error: No such process found - {e}")
    except psutil.AccessDenied as e:
        print(f"Error: Access denied to kill process - {e}")
    except psutil.ZombieProcess as e:
        print(f"Error: Zombie process encountered - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def setup_chrome_profile():
    """Setup Chrome profile for manual login and CAPTCHA handling."""
    print("\nLaunching Chrome for manual profile setup...")
    chrome_data_dir = Path(CHROME_DATA_DIR)
    chrome_profile = Path(CHROME_PROFILE)
    options = ChromeOptions()
    options.add_argument(f"--user-data-dir={chrome_data_dir}")
    options.add_argument(f"--profile-directory={chrome_profile}")
    
    print("🔒 Please log in and set up your Chrome profile. Also sign in to Chrome and go to Cookie Clicker website and consent for storing cookies etc. It is a must.\n")
    time.sleep(2)

    driver = Chrome(options=options)
    driver.get("https://www.google.com/")
    
    input("✅ Press Enter when you're finished: ")

    try: return driver
    except: return None


UPGRADES_CLICK_SLEEP_TIME = load_or_initialize("upgrades_click_sleep_time.txt")
PRODUCTS_CLICK_SLEEP_TIME = load_or_initialize("products_click_sleep_time.txt")

# Prepare Chrome
try:
    chrome_data_dir = Path(CHROME_DATA_DIR)
    chrome_profile = Path(CHROME_PROFILE)
    profile_path = os.path.join(chrome_data_dir, chrome_profile)
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Chrome profile not found at: {profile_path}")
    options = ChromeOptions()
    options.add_argument(f"--user-data-dir={chrome_data_dir}")
    options.add_argument(f"--profile-directory={chrome_profile}")
    driver = Chrome(options=options)
except:
    kill_chrome_processes()
    create_new_profile()
    driver = setup_chrome_profile()

if driver:
    driver.get(URL)
else:
    options = ChromeOptions()
    chrome_data_dir = Path(CHROME_DATA_DIR)
    chrome_profile = Path(CHROME_PROFILE)
    options.add_argument(f"--user-data-dir={chrome_data_dir}")
    options.add_argument(f"--profile-directory={chrome_profile}")
    driver = Chrome(options=options)
    driver.get(URL)

# Wait until the cookie is present
wait =  WebDriverWait(driver, WAIT_TIME)
cookie = wait.until(EC.presence_of_element_located((By.ID, "bigCookie")))


def click_cookie():
    global cookie, UPGRADES_CLICK_SLEEP_TIME, PRODUCTS_CLICK_SLEEP_TIME
    while True:
        try:
            cookie.click()
        except:
            cookie = wait.until(EC.presence_of_element_located((By.ID, "bigCookie")))

        # Occasionally increase click delay (simulate slowdown)
        if randint(0, 100) == 1:
            UPGRADES_CLICK_SLEEP_TIME += 1
            PRODUCTS_CLICK_SLEEP_TIME += 1

            with open("upgrades_click_sleep_time.txt", "w") as f:
                f.write(str(UPGRADES_CLICK_SLEEP_TIME))

            with open("products_click_sleep_time.txt", "w") as f:
                f.write(str(PRODUCTS_CLICK_SLEEP_TIME))


def buy_upgrades():
    while True:
        try:
            upgrades = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".crate.upgrade.enabled")))[::-1]
            # upgrades = driver.find_elements(By.CSS_SELECTOR, ".crate.upgrade.enabled")[::-1]
            for upgrade in upgrades:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", upgrade)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(upgrade))
                    upgrade.click()
                except:
                    continue
        except Exception as e:
            print(f"Error buying upgrades: {e}")
        time.sleep(UPGRADES_CLICK_SLEEP_TIME)


def buy_products():
    while True:
        try:
            products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product.unlocked.enabled")))[::-1]
            # products = driver.find_elements(By.CSS_SELECTOR, ".product.unlocked.enabled")[::-1]
            for product in products:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", product)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(product))
                    product.click()
                except:
                    continue
        except Exception as e:
            print(f"Error buying products: {e}")
        time.sleep(PRODUCTS_CLICK_SLEEP_TIME)


def click_golden_cookie():
    while True:
        try:
            golden = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".shimmer")))
            # golden = driver.find_element(By.CSS_SELECTOR, ".shimmer")
            golden.click()
            print("✨ Golden cookie clicked!")
        except:
            pass
        time.sleep(SLEEP_TIME)


# Threads
cookie_click_thread = threading.Thread(target=click_cookie)
upgrade_thread = threading.Thread(target=buy_upgrades)
product_thread = threading.Thread(target=buy_products)
golden_thread = threading.Thread(target=click_golden_cookie)

cookie_click_thread.start()
upgrade_thread.start()
product_thread.start()
golden_thread.start()

# Graceful shutdown
try:
    cookie_click_thread.join()
    upgrade_thread.join()
    product_thread.join()
    golden_thread.join()
except:
    print("\n⛔ Interrupted by user. Exiting gracefully...")
    driver.quit()
