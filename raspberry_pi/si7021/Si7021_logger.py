import pigpio
from time import sleep, time
import csv
import os

OUTPUT_FILE = 'pi_si7021_log.csv'

def csvwrite(data):
    dataCSV = open(OUTPUT_FILE, 'a')
    log = csv.writer(dataCSV)
    log.writerow(data)
    dataCSV.close()

# I2C Address for the Si7021
I2C_ADDRESS = 0x40
# Access Bus 1 on the Raspberry Pi
BUS = 1

# Si7021 Commands for Taking Measurements
CMD_RH = 0xF5
CMD_TEMP = 0xE0

# Convert a two bytes string into a 16 bit integer
def int16bit(b):
    return(b[0] << 8) + (b[1])

def relative_humidity(raw):
    return raw * 125.0 / 65536.0 - 6.0

def temperature(raw):
    return raw * 175.72 / 65536.0 - 46.85

pi = pigpio.pi()
device = pi.i2c_open(BUS, I2C_ADDRESS)


def main():
    device = pi.i2c_write_byte(device, CMD_RH)
    sleep(0.1)
    a, b = pi.i2c_read_device(device, 2)
    raw_humidity = int16bit(b)
    humidity = relative_humidity(raw_humidity)
    print("Humidity = " + str(round(humidity, 3)))

    pi.i2c_write_byte(device, CMD_TEMP)
    c, d = pi.i2c_read_device(device, 2)
    raw_temp = int16bit(d)
    temp = temperature(raw_temp)
    print("Temperature = " + str(round(temp, 3)))

    csvwrite([timestamp, humidity, temp])


if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'humidity_percent', 'temperature_c'])
        while True:
            main()
            sleep(2)

    except KeyboardInterrupt:
        pass