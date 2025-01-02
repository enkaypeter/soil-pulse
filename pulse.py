import RPi.GPIO as GPIO
import time

# Choose a GPIO pin to read the D0 signal. 
# For example, let's use GPIO17 (physical pin 11).
SENSOR_PIN = 17

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)

def loop():
    while True:
        sensor_value = GPIO.input(SENSOR_PIN)
        # sensor_value == 0 or 1 depending on moisture level
        if sensor_value == 0:
            print("Soil is wet (LOW).")
        else:
            print("Soil is dry (HIGH).")
        time.sleep(1)

if __name__ == '__main__':
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
