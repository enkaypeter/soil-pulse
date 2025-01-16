import requests
import time
import random
from datetime import datetime
import RPi.GPIO as GPIO  # For reading the soil sensor

# API endpoint to send the soil readings
API_ENDPOINT = ""

# Default sensor pin
DEFAULT_SENSOR_PIN = 3

def read_soil_sensor(sensor_pin=DEFAULT_SENSOR_PIN):
    """
    Reads the soil sensor's digital output.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensor_pin, GPIO.IN)
    val = GPIO.input(sensor_pin)
    state = "DRY" if val == GPIO.HIGH else "WET"
    GPIO.cleanup(sensor_pin)
    return val, state

def generate_soil_reading():
    """
    Reads the soil sensor and generates a reading in the required format.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_pin = DEFAULT_SENSOR_PIN  # Pin to read from
    val, state = read_soil_sensor(sensor_pin)

    return {
        "timestamp": now_str,
        "sensor_pin": sensor_pin,
        "reading": val,
        "state": state,
    }

def send_soil_reading():
    """
    Sends the soil reading to the API endpoint.
    """
    try:
        soil_reading = generate_soil_reading()
        response = requests.post(API_ENDPOINT, json=soil_reading)

        if response.status_code == 200:
            print(f"Successfully sent data: {soil_reading}")
        else:
            print(f"Failed to send data: {response.status_code}, {response.text}")

    except requests.RequestException as e:
        print(f"Error sending data: {e}")

def main():
    """
    Periodically sends soil readings to the API endpoint.
    """
    print("Sending soil readings...")
    send_soil_reading()

if __name__ == "__main__":
    main()
