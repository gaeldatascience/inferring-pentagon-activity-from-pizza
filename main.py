import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.async_api import async_playwright

from utils.factory import near_pizzerias
from utils.functions import (
    log_traffic_data,
    fetch_traffic,
    create_playwright_context,
)

async def main():
    """Main scraping function that collects traffic data from Pentagon-area pizzerias.
    
    Orchestrates the web scraping process by:
    1. Setting up timestamp and timezone data for Washington DC
    2. Creating browser context and pages for each pizzeria
    3. Concurrently fetching traffic data from all pizzerias
    4. Logging the collected data to the SQLite database
    
    The function only runs during off-peak hours (between 1am and 9am) to avoid
    detection and minimize impact on the monitored websites.
    
    Note:
        Uses asyncio.gather() for concurrent scraping to improve performance
        and reduce total execution time.
    """
    # Timestamp in New York / Washington DC timezone
    now = datetime.now(ZoneInfo("America/New_York"))
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    dow = now.strftime("%A")
    hr = now.hour

    if hr > 9 or hr < 1:
        async with async_playwright() as p:
            browser, context = await create_playwright_context(p, headless=True)
            tasks = []
            pages = []

            for name, url in near_pizzerias.items():
                page = await context.new_page()
                pages.append((name, page))
                tasks.append(fetch_traffic(page, url))

            results = await asyncio.gather(*tasks)

            for (name, _), (live, hist) in zip(pages, results):
                print(f"{name}: {live}%, {hist}%")
                log_traffic_data(name, ts, dow, hr, live, hist)

            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())