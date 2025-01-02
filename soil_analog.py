import spidev
import time

# Open SPI bus 0, device (chip select) 0
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_mcp3008(channel):
    """
    Reads raw ADC value from 0-1023 (10-bit) on a specified channel (0–7).
    SPI protocol: we send 3 bytes, and read 3 bytes.
      Byte 1:  0x01 (start bit)
      Byte 2:  (channel + 8) << 4 (single-ended mode)
      Byte 3:  0x00 (don't care)
    """
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    # Construct 10-bit value from the returned bytes
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

try:
    while True:
        # Read from channel 0 (where sensor is connected)
        raw_value = read_mcp3008(0)

        # Convert raw value to a voltage based on a 3.3V reference
        # MCP3008 is 10-bit = 1024 steps
        voltage = (raw_value * 3.3) / 1023.0

        # Print results
        print(f"ADC Raw: {raw_value}  |  Voltage: {voltage:.2f} V")

        # You can interpret higher voltage as "soil more conductive" (more moist)
        # and lower voltage as "soil drier"

        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    spi.close()
