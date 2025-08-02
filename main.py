from utils.factory import near_pizzerias
from utils.functions import create_chrome_driver, get_live_traffic, log_traffic_data
from datetime import datetime
from zoneinfo import ZoneInfo

dc_time = datetime.now(ZoneInfo("America/New_York"))
dc_time_string = dc_time.strftime("%Y-%m-%d %H:%M:%S")
dc_day_of_week = dc_time.strftime("%A")
dc_hour = dc_time.hour

if dc_hour:#dc_hour>9 or dc_hour<1:
    driver = create_chrome_driver(headless=False)
    for pizzeria, url in near_pizzerias.items():
        live_traffic, historical_traffic = get_live_traffic(driver, url)
        log_traffic_data(pizzeria, dc_time_string, dc_day_of_week, dc_hour, live_traffic, historical_traffic)
        break
    driver.quit()