## Inferring Pentagon Activity from Pizza

This project explores the potential of using late-night foot traffic at Pentagon-area pizzerias as a proxy indicator of operational activity, leveraging automated Google Maps scraping with Playwright, scheduled every 15 minutes, and persistent logging in a SQLite database.

---

### Motivation

"Pizza intelligence" ("Pizzint") relies on the hypothesis that late-night gatherings at government sites correlate with increased local pizza delivery activity. Through the collection and analysis of such indirect behavioral signals, it becomes possible to detect anomalies that might suggest operational movements. This project illustrates how public data, when systematically processed, can yield insight into covert activity.

### How It Works

The project operates through an asynchronous web scraping pipeline that efficiently collects traffic data from multiple Pentagon-area pizzerias:

1. **Browser Context Setup**: Creates a Playwright browser instance with Chromium, configured with French locale and headers optimized for Google Maps scraping.

2. **Concurrent Data Collection**: Navigates to Google Maps business pages for each target pizzeria simultaneously, handling cookie consent dialogs and extracting live traffic percentages.

3. **Data Processing**: Parses French language traffic patterns ("Taux de fréquentation actuel") to extract both current and historical traffic percentages.

4. **Database Logging**: Stores timestamped metrics in a SQLite database, with automatic anomaly calculation to identify unusual activity spikes or drops.

5. **Scheduled Execution**: Runs every 15 minutes during pizzeria operating hours (10am-1am) when traffic data is available and meaningful for analysis.

---

## Project Structure

```
inferring-pentagon-activity-from-pizza/
├── main.py              # Async orchestration: manages browser contexts and concurrent scraping
├── initialize_db.py     # Database initialization: creates SQLite schema with anomaly detection
├── utils/               # Core functionality modules
│   ├── functions.py     # Web scraping functions using Playwright
│   └── factory.py       # Pizzeria configuration and Google Maps URLs
├── data/                # SQLite database storage for traffic logs
├── .github/workflows/   # GitHub Actions automation for scheduled execution
└── README.md            # Project documentation
```

### Core Components

1. **Main Orchestrator** (`main.py`): Manages the complete scraping workflow using asyncio for concurrent execution across multiple pizzerias during operating hours.

2. **Web Scraping Engine** (`utils/functions.py`): 
   - Creates optimized Playwright browser contexts with French locale
   - Extracts live and historical traffic data from Google Maps aria-labels
   - Handles cookie consent dialogs and data validation

3. **Data Persistence** (`initialize_db.py` & logging): Maintains SQLite database with automatic anomaly calculation for traffic pattern analysis.

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
- **Playwright**: Modern browser automation framework
- **Chromium**: Automatically installed via Playwright

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
3. Install dependencies and Playwright browsers:
   ```bash
   pip install -e .
   playwright install chromium
   ```

## Usage

1. **Execute the async scraper**:
   ```bash
   python main.py
   ```
   
   The scraper will:
   - Create concurrent browser contexts for each pizzeria
   - Extract traffic data from French Google Maps pages
   - Log results to the SQLite database with anomaly detection
   - Only run during operating hours
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
          playwright install chromium
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
