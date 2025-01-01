from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Path to the Chrome User Data directory
CHROME_PROFILE_PATH = r"C:\Users\Global Computers\AppData\Local\Google\Chrome\User Data"

# Chrome options to use the default profile
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")  # Path to User Data directory
chrome_options.add_argument("--profile-directory=Default")  # Specify the 'Default' profile
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = None
try:
    # Create the WebDriver instance with options
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.google.com")  # Navigate to a website
    print(f"Page title: {driver.title}")
    time.sleep(5)  # Keep the browser open for 5 seconds
finally:
    if driver:
        driver.quit()  # Close the browser
