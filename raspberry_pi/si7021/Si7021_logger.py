#!/usr/bin/env python

import pigpio
from time import sleep, time
import csv
import os

OUTPUT_FILE = 'pi_si7021_log.csv'

# Number of readings to take before calculating the average
AVERAGE_READ = 300
# Fieldset of keys used to parse the data list to calculate the average
AVERAGE_FIELD = ['data1', 'data2']

def csvwrite(data):
    dataCSV = open(OUTPUT_FILE, 'a')
    log = csv.writer(dataCSV)
    log.writerow(data)
    dataCSV.close()

def average(data_list):
    avg_data = []
    avg_data.append(time())
    for key in AVERAGE_FIELD:
        avg_data.append(float((sum(data[key] for data in data_list)) / len(data_list)))
        avg_data.append(max(data[key] for data in data_list))
        avg_data.append(min(data[key] for data in data_list))
    return avg_data

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

def main():
    data_set = []
    pi = pigpio.pi()
    device = pi.i2c_open(BUS, I2C_ADDRESS)
    while True:
        device = pi.i2c_write_byte(device, CMD_RH)
        sleep(0.1)
        a, b = pi.i2c_read_device(device, 2)
        raw_humidity = int16bit(b)
        humidity = relative_humidity(raw_humidity)
        #print("Humidity = " + str(round(humidity, 3)))

        pi.i2c_write_byte(device, CMD_TEMP)
        c, d = pi.i2c_read_device(device, 2)
        raw_temp = int16bit(d)
        temp = temperature(raw_temp)
        #print("Temperature = " + str(round(temp, 3)))

        data = {'data1': humidity,
                'data2': temp }
        data_set.append(data)

        if len(data_set) >= AVERAGE_READ:
            average_data = average(data_set)
            timestamp, avg_humidity, max_humidity, min_humidity, avg_temp, max_temp, min_temp = average_data
            csvwrite([timestamp, min_humidity, avg_humidity, max_humidity, min_temp, avg_temp, max_temp])
            del data_set[:]
        
        sleep(1)

if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'humidity_percent_min', 'humidity_percent_avg', 'humidity_percent_max', 'temperature_c_min', 'temperature_c_avg', 'temperature_c_max'])
        main()

    except KeyboardInterrupt:
        pass