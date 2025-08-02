## Inferring Pentagon Activity from Pizza

This project attempts to uncover patterns of activity within the Pentagon by monitoring busyness metrics at nearby pizzerias. By collecting public "live busyness" data at regular intervals, we can observe spikes or lulls in pizza demand and consider whether these signals correlate with events or changes inside the Pentagon.

---

## Motivation

The concept of "pizza intelligence" ("Pizzint") plays on the idea that patterns in everyday data—such as orders or foot traffic at pizzerias—could serve as informal indicators of activity in sensitive locations. While this project is intended for educational and exploratory purposes, it showcases how web scraping, data storage, and simple analysis can be combined to reveal hidden trends in publicly available metrics.

## Features

- **Automated Scraping**: Collects live busyness scores for pizzerias around the Pentagon at fixed intervals.
- **Local Storage**: Persists timestamped metrics in an on-disk SQLite database (`data/traffic_logs.db`).
- **Extensible**: Easily add or remove target restaurants by modifying a configuration list.
- **Lightweight**: Uses a headless Chromium instance via Selenium to minimize overhead.

## Architecture

1. **Scraper** (`main.py`): Launches a headless browser, navigates to each Google Maps business profile, extracts the live busyness percentage, and stores it in the database.
3. **Scheduler** (`.github/workflows/scheduler.yml`): Executes the scraper via GitHub Actions every 15 minutes and optionally commits the updated database.

## Data Storage

The collected data is stored in an SQLite database (`data/traffic_logs.db`) with the following schema:

### Table: `traffic_logs`

| Column | Description |
|--------|-------------|
| `pizzeria` | Name of the pizzeria being monitored |
| `timestamp` | Date and time when the data was collected |
| `day_of_week` | Day of the week for the timestamp |
| `hour` | Hour of the day (0-23) |
| `live_traffic` | Current live busyness percentage (0-100) |
| `historical_traffic` | Historical/expected busyness for this time |
| `anomaly` | Automatically calculated difference between live and historical traffic |

## Prerequisites

- **Python** 3.12 or later
- **SQLite** (bundled with Python)
- **Browsers**: Chromium (Headless)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gaeldatascience/inferring-pentagon-activity-from-pizza.git
   cd inferring-pentagon-activity-from-pizza
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   .\.venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```

## Usage

1. **Initialize the database** (run once):
   ```bash
   python initialize_db.py
   ```
2. **Execute the scraper**:
   ```bash
   python main.py
   ```
3. **Inspect data**:
   - The SQLite file is located at `data/traffic_logs.db`.
   - Use any SQLite client (e.g., `sqlite3`, DB Browser) to query and visualize trends.

## Scheduling and Automation

A GitHub Actions workflow (`.github/workflows/scheduler.yml`) runs every 15 minutes:

```yaml
name: Scheduled Traffic Collection
on:
  schedule:
    - cron: '*/15 * * * *'
jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -e .
      - name: Run Scraper
        run: python main.py
      - name: Commit Database (optional)
        run: |
          git config user.name 'github-actions'
          git config user.email 'actions@github.com'
          git add data/traffic_logs.db
          git commit -m 'Update traffic logs'
          git push
```

## Configuration

- **Target Restaurants**: Edit the list in `utils/factory.py` to add or remove Google Maps URLs.
- **Scrape Interval**: Modify the `cron` expression in the GitHub Actions file to change frequency.

## Contributing

Contributions and suggestions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a Pull Request and describe your changes.

Please ensure code quality, include tests or examples where appropriate, and document new behavior.

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is for educational and experimental purposes only. It does not claim to provide accurate or actionable intelligence regarding Pentagon activities. The data collected is publicly available and should not be used for any unlawful or unethical purposes. Always respect privacy and data usage policies when scraping web content.
