import re
import sqlite3
from playwright.async_api import Playwright


def log_traffic_data(
    pizzeria: str,
    timestamp: str,
    day_of_week: str,
    hour: int,
    live_traffic: int | None,
    historical_traffic: int | None,
):
    """Log traffic data to the SQLite database.

    Inserts a new record into the traffic_logs table with the provided traffic
    data. The anomaly column is automatically calculated by the database as
    the difference between live and historical traffic. Skips logging if either
    traffic value is None.

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

    if live_traffic is None or historical_traffic is None:
        print(f"Skipped logging: missing traffic data for {pizzeria}")
        return

    conn = sqlite3.connect("data/traffic_logs.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO traffic_logs
          (pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (pizzeria, timestamp, day_of_week, hour, live_traffic, historical_traffic),
    )
    conn.commit()
    conn.close()


async def fetch_traffic(page, url: str) -> tuple[int | None, int | None]:
    """Extract live and historical traffic data from a Google Maps page.

    Navigates to the specified Google Maps business URL and scrapes the live
    traffic percentage along with historical traffic data. Handles cookie
    consent dialogs automatically and extracts data from aria-labels.

    Args:
        page: Playwright page instance for web automation.
        url (str): Google Maps business page URL to scrape traffic data from.

    Returns:
        tuple[int | None, int | None]: A tuple containing:
            - live_traffic: Current traffic percentage (0-100) or None if not found
            - historical_traffic: Historical traffic percentage or None if not found

    Note:
        The function handles French language Google Maps pages and looks for
        "Taux de fréquentation actuel" patterns in aria-labels.
    """
    await page.goto(url)
    await page.wait_for_timeout(1_000)
    try:
        await page.click('input[value="Tout refuser"]', timeout=2_000)
        await page.wait_for_timeout(1_000)
    except:
        pass

    labels = await page.locator("div.dpoVLd").evaluate_all(
        "els => els.map(el => el.getAttribute('aria-label')).filter(Boolean)"
    )
    for label in labels:
        text = re.sub(r"\s+", " ", label)
        if "actuel" in text:
            m = re.search(
                r"Taux de fréquentation actuel de (\d+) % \((\d+) % en général\)\.",
                text,
            )
            if m:
                return int(m.group(1)), int(m.group(2))
    return None, None


async def create_playwright_context(p: Playwright, headless: bool = True) -> tuple:
    """Launch Chromium and create a browser context with FR locale and headers.

    Creates a Playwright browser instance with Chromium and configures a browser
    context optimized for French Google Maps scraping. Sets French locale,
    user agent, and language headers to ensure proper page rendering.

    Args:
        p (Playwright): Playwright instance for browser automation.
        headless (bool, optional): Whether to run browser in headless mode.
            Defaults to True.

    Returns:
        tuple: A tuple containing:
            - browser: Playwright browser instance
            - context: Browser context with French locale configuration

    Note:
        The context is configured specifically for French Google Maps pages
        with appropriate locale and headers.
    """
    browser = await p.chromium.launch(
        headless=headless, args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    context = await browser.new_context(
        locale="fr-FR",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        extra_http_headers={"Accept-Language": "fr-FR,fr"},
    )
    return browser, context
