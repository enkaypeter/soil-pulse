#!/usr/bin/env python3

import os
import sqlite3
from datetime import datetime

import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

DB_PATH = "soil_data.db"  # SQLite database file
DEFAULT_SENSOR_PIN = 3
# Ensure we set BCM mode once globally (avoid repeating)
GPIO.setmode(GPIO.BCM)

def init_db():
    """
    Create the readings table if it doesn't exist.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS soil_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                sensor_pin INTEGER NOT NULL,
                reading INTEGER NOT NULL,
                state TEXT NOT NULL
            )
            """
        )
        conn.commit()

@app.route("/read_soil", methods=["GET"])
def read_soil():
    """
    Reads the sensor's digital output.
    Optional query param 'pin', e.g. /read_soil?pin=3
    Defaults to pin=3.
    Saves the result in the DB, returns JSON of the reading.
    """
    # 1. Determine which BCM pin to read
    pin_str = request.args.get("pin", DEFAULT_SENSOR_PIN)
    try:
        sensor_pin = int(pin_str)
    except ValueError:
        sensor_pin = DEFAULT_SENSOR_PIN

    # 2. Setup and read GPIO
    print(f"sensor {sensor_pin}")
    GPIO.setup(sensor_pin, GPIO.IN)
    val = GPIO.input(sensor_pin)

    # Interpret the reading (0=wet, 1=dry in many sensor modules)
    state = "DRY" if val == GPIO.HIGH else "WET"

    # Optional: cleanup the pin after reading
    GPIO.cleanup(sensor_pin)

    # 3. Prepare a timestamp
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. Save to SQLite
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO soil_readings (timestamp, sensor_pin, reading, state)
            VALUES (?, ?, ?, ?)
            """,
            (now_str, sensor_pin, val, state),
        )
        conn.commit()

    # 5. Return JSON response
    response = {
        "timestamp": now_str,
        "sensor_pin": sensor_pin,
        "reading": val,
        "state": state,
    }
    return jsonify(response)

@app.route("/history", methods=["GET"])
def history():
    """
    Returns all recorded soil readings from the DB in JSON.
    You can add pagination, filters, etc., if desired.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # allows dict-like access
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soil_readings ORDER BY id DESC")
        rows = cursor.fetchall()

    # Convert rows to a list of dicts
    results = []
    for row in rows:
        results.append(
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "sensor_pin": row["sensor_pin"],
                "reading": row["reading"],
                "state": row["state"],
            }
        )

    return jsonify(results)

if __name__ == "__main__":
  with app.app_context():
    init_db()

  app.run(host="0.0.0.0", port=5000, debug=True)
