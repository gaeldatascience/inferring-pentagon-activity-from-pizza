import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sqlite3

def create_chrome_driver(headless=True):

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"  # path for Ubuntu
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    if headless:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

    return webdriver.Chrome(options=chrome_options)


def get_live_traffic(driver, url):
    try:
        driver.get(url)
        time.sleep(1)
        
        try:
            refuser_btn = driver.find_element(By.XPATH, '//input[@value="Tout refuser"]')
            refuser_btn.click()
            time.sleep(1)
        except:
            pass
        
        elements = driver.find_elements(By.XPATH, '//div[contains(@class, "dpoVLd")]')
        aria_labels = [el.get_attribute("aria-label") for el in elements if el.get_attribute("aria-label")]

        live_traffic = next(
            (re.sub(r'\s+', ' ', label) for label in aria_labels if "actuel" in label),
            None
        )

        if live_traffic:
            pattern = re.compile(r"Taux de fréquentation actuel de (\d+) % \((\d+) % en général\)\.")
            match = pattern.search(live_traffic)
            if match:
                return int(match.group(1)), int(match.group(2))

        return None, None
    finally:
        pass
        
        
def log_traffic_data(pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic):
    
    conn = sqlite3.connect("data/traffic_logs.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO traffic_logs (pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic))

    conn.commit()
    conn.close()