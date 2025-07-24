"""
Cookie Clicker Bot
-------------------
Automates the popular Cookie Clicker game using Selenium and a persistent Chrome profile.

Features:
- Clicks the main cookie continuously.
- Buys upgrades and products automatically.
- Clicks golden cookies when they appear.
- Saves click timing configurations to disk.
- Uses undetected ChromeDriver with persistent user profile.

Note: Requires `.env` file with CHROME_DATA_DIR and CHROME_PROFILE variables set.
"""

import os
import shutil
import time
import threading
from random import randint
from pathlib import Path
from dotenv import load_dotenv
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------------------
# Initial Setup
# ----------------------------------------

print("💾 Don't forget to save your progress in Cookie Clicker before closing the browser (Ctrl + S)!")

# Load environment variables
if not os.path.exists(".env"):
    print("⚠️ .env file not found. Using default values.")
load_dotenv(".env")

# Constants
URL = "https://orteil.dashnet.org/cookieclicker/"
CHROME_DATA_DIR = os.getenv("CHROME_DATA_DIR")
CHROME_PROFILE = os.getenv("CHROME_PROFILE")
CHROME_DATA_DIR = Path(CHROME_DATA_DIR)
CHROME_PROFILE = Path(CHROME_PROFILE)
SLEEP_TIME = 0.01            # Golden cookie scan interval
WAIT_TIME = 120              # Max wait time for elements

# ----------------------------------------
# Helper Functions
# ----------------------------------------

def load_or_initialize(filename: str, default: float = 0.0) -> float:
    """
    Loads a float value from a file or initializes the file with a default value.

    Args:
        filename (str): The file to load from or create.
        default (float): Default value to initialize if file doesn't exist.

    Returns:
        float: Loaded or default value.
    """
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(str(default))
    with open(filename, "r") as f:
        return float(f.read())

def create_new_profile():
    """
    Creates a new Chrome profile directory and prompts the user to configure it manually.
    """
    profile_path = CHROME_DATA_DIR / CHROME_PROFILE

    if not os.path.exists(CHROME_DATA_DIR):
        os.makedirs(CHROME_DATA_DIR)

    if os.path.exists(profile_path):
        shutil.rmtree(profile_path)

    print(f"Creating Chrome profile: {CHROME_PROFILE}")
    print("🔒 Please log in to your Google Account and accept Cookie Clicker cookies. This is a one-time setup.\n")
    time.sleep(2)
    print(f"✅ Profile '{CHROME_PROFILE}' created successfully!")

# ----------------------------------------
# Load Configurable Timings
# ----------------------------------------

UPGRADES_CLICK_SLEEP_TIME = load_or_initialize("upgrades_click_sleep_time.txt")
PRODUCTS_CLICK_SLEEP_TIME = load_or_initialize("products_click_sleep_time.txt")

# ----------------------------------------
# Setup Chrome with Persistent Profile
# ----------------------------------------

try:
    profile_path = CHROME_DATA_DIR / CHROME_PROFILE
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Chrome profile not found at: {profile_path}")
except:
    create_new_profile()
finally:
    options = ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROME_DATA_DIR}")
    options.add_argument(f"--profile-directory={CHROME_PROFILE}")
    driver = Chrome(options=options)

driver.get(URL)
wait = WebDriverWait(driver, WAIT_TIME)

# Wait for cookie to become available
cookie = wait.until(EC.presence_of_element_located((By.ID, "bigCookie")))

# ----------------------------------------
# Worker Threads
# ----------------------------------------

def click_cookie():
    """
    Continuously clicks the big cookie and occasionally increases the delay for realism.
    """
    global cookie, UPGRADES_CLICK_SLEEP_TIME, PRODUCTS_CLICK_SLEEP_TIME
    while True:
        try:
            cookie.click()
        except:
            cookie = wait.until(EC.presence_of_element_located((By.ID, "bigCookie")))

        # Occasionally simulate slowdown
        if randint(0, 100) == 1:
            UPGRADES_CLICK_SLEEP_TIME += 1
            with open("upgrades_click_sleep_time.txt", "w") as f:
                f.write(str(UPGRADES_CLICK_SLEEP_TIME))
        if randint(0, 100) == 30:
            PRODUCTS_CLICK_SLEEP_TIME += 1
            with open("products_click_sleep_time.txt", "w") as f:
                f.write(str(PRODUCTS_CLICK_SLEEP_TIME))

def buy_upgrades():
    """
    Periodically buys available upgrades (top bar items).
    """
    while True:
        try:
            upgrades = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".crate.upgrade.enabled")))[::-1]
            for upgrade in upgrades:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", upgrade)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(upgrade)).click()
                except:
                    continue
            time.sleep(UPGRADES_CLICK_SLEEP_TIME)
        except Exception as e:
            print(f"Error buying upgrades: {e}")

def buy_products():
    """
    Periodically buys available products (bottom store items).
    """
    while True:
        try:
            products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product.unlocked.enabled")))[::-1]
            for product in products:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", product)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(product)).click()
                except:
                    continue
            time.sleep(PRODUCTS_CLICK_SLEEP_TIME)
        except Exception as e:
            print(f"Error buying products: {e}")

last_click_time = 0

def click_golden_cookie():
    """
    Detects and clicks golden cookies (special bonuses).
    """
    global last_click_time
    while True:
        try:
            golden = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".shimmer")))
            golden.click()
            now = time.time()
            if now - last_click_time > 1:
                print("✨ Golden cookie clicked!")
                last_click_time = now
        except:
            pass
        time.sleep(SLEEP_TIME)

# ----------------------------------------
# Start Threads
# ----------------------------------------

cookie_click_thread = threading.Thread(target=click_cookie, daemon=True)
upgrade_thread = threading.Thread(target=buy_upgrades, daemon=True)
product_thread = threading.Thread(target=buy_products, daemon=True)
golden_thread = threading.Thread(target=click_golden_cookie, daemon=True)

cookie_click_thread.start()
upgrade_thread.start()
product_thread.start()
golden_thread.start()

# ----------------------------------------
# Graceful Exit
# ----------------------------------------

try:
    while True:
        driver.title  # keep session alive
        time.sleep(2)
except:
    print("\n⛔ Interrupted by user. Exiting gracefully...")
    driver.quit()
