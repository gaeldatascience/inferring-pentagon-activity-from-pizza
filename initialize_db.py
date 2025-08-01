import sqlite3

conn = sqlite3.connect("data/traffic_logs.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS traffic_logs")

cursor.execute("""
CREATE TABLE traffic_logs (
    pizzeria TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,          
    day_of_week TEXT,
    hour INTEGER,
    live_traffic INTEGER,
    historical_traffic INTEGER,
    anomaly INTEGER GENERATED ALWAYS AS (
        live_traffic - historical_traffic
    ) STORED
);
""")

conn.commit()
cursor.close()
conn.close()
