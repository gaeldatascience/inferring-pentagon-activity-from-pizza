import re
import sqlite3
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def create_chrome_driver(headless=True):
    """Create a Chrome WebDriver instance with optimized options for web scraping.
    
    Configures Chrome with various options to avoid detection as an automated browser
    and optimize performance for headless operation. Sets a custom user agent and
    disables automation features that might be detected by websites.
    
    Args:
        headless (bool, optional): Whether to run Chrome in headless mode. 
            Defaults to True.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance ready for use.
    
    Note:
        The binary location is currently configured for Ubuntu systems. 
        Uncomment and modify the Windows path as needed for other platforms.
    """

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"  # path for Ubuntu
    #chrome_options.binary_location = "C:/Users/zetru/AppData/Local/Chromium/Application/chrome.exe"
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
    """Extract live and historical traffic data from a Google Maps business page.
    
    Navigates to a Google Maps business URL, handles cookie consent dialogs,
    and extracts the current live traffic percentage along with historical
    traffic data from the page elements.
    
    Args:
        driver (webdriver.Chrome): Chrome WebDriver instance for web automation.
        url (str): Google Maps business page URL to scrape traffic data from.
    
    Returns:
        tuple[int | None, int | None]: A tuple containing:
            - live_traffic: Current traffic percentage (0-100) or None if not found
            - historical_traffic: Historical traffic percentage or None if not found
    
    Note:
        The function handles French language Google Maps pages and looks for
        "Taux de fréquentation actuel" patterns in aria-labels.
    """
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
            print(f"Live traffic: {live_traffic}")
            pattern = re.compile(r"Taux de fréquentation actuel de (\d+) % \((\d+) % en général\)\.")
            match = pattern.search(live_traffic)
            if match:
                return int(match.group(1)), int(match.group(2))

        return None, None
    finally:
        pass
        
        
def log_traffic_data(pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic):
    """Log traffic data to the SQLite database.
    
    Inserts a new record into the traffic_logs table with the provided traffic
    data. The anomaly column is automatically calculated by the database as
    the difference between live and historical traffic.
    
    Args:
        pizzeria (str): Name of the pizzeria being monitored.
        timestamp (str): Formatted timestamp string (YYYY-MM-DD HH:MM:SS).
        day_of_week (str): Full day name (e.g., 'Monday', 'Tuesday').
        hour (int): Hour of the day (0-23).
        live_traffic (int | None): Current live traffic percentage (0-100).
        historical_traffic (int | None): Historical traffic percentage (0-100).
    
    Note:
        The database connection is automatically opened and closed within
        this function. The anomaly column is computed automatically by SQLite.
    """
    
    conn = sqlite3.connect("data/traffic_logs.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO traffic_logs (pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic))

    conn.commit()
    conn.close()