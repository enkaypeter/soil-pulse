#!/usr/bin/env python3

import os
import sqlite3
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

mini_app = Flask(__name__)

CORS(app)

DB_PATH = "soil_data.db"

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

@mini_app.route("/record", methods=["POST"])
def record_soil_reading():
    """
    Accept soil reading payload via POST and save to the database.
    """
    data = request.get_json()
    required_fields = ["timestamp", "sensor_pin", "reading", "state"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO soil_readings (timestamp, sensor_pin, reading, state)
                VALUES (?, ?, ?, ?)
                """,
                (
                    data["timestamp"],
                    data["sensor_pin"],
                    data["reading"],
                    data["state"],
                ),
            )
            conn.commit()

        return jsonify({"message": "Soil reading recorded successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mini_app.route("/history", methods=["GET"])
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
  with mini_app.app_context():
    init_db()

  mini_app.run(host="0.0.0.0", port=5000, debug=True)
