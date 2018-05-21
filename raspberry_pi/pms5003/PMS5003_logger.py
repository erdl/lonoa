#!/usr/bin/env python

from time import sleep, time
import serial
import struct
import os
import csv

# Default serial port for raspberry pi 2
PI2_SERIALPORT = "/dev/ttyAMA0"
# Baudrate specified for the PMS5003 sensor
PMS5003_BAUDRATE = 9600

# Fixed flag bytes
START_FLAG1 = b'\x42'
START_FLAG2 = b'\x4d'

# Data is read in the order from high to low (big-endian format)
BYTE_ORDER = ">"
# Convert from bytes to integer for all 14 data values
FORMAT_CHARACTER = "HHHHHHHHHHHHHH"

# Normal frame length is 32 bytes
FRAME_LENGTH = 32
# Frame length excluding data 14 high and data 14 low
CHECKSUM_FRAME_LENGTH = 30

# Index of start flag 1 byte
BYTE_1 = 0
# Index of start flag 2 byte
BYTE_2 = 1
# Index of the first data byte to be unpacked
BYTE_5 = 4

# Number of readings to take before calculating the average
AVERAGE_READ = 300
# Fieldset of keys used to parse the data list to calculate average
AVERAGE_FIELD = ['data1', 'data2', 'data3']

def csvwrite(data):
    dataCSV = open('pi_pms5003_log.csv', 'a')
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


def main():
    # open serial port
    ser = serial.Serial(PI2_SERIALPORT, baudrate=PMS5003_BAUDRATE, timeout=2.0)
    data_set = []
    while True:
        # frame length is 32 bytes
        s = ser.read(FRAME_LENGTH)
        # check if the start flags matches
        if s[BYTE_1] == START_FLAG1 and s[BYTE_2] == START_FLAG2:
            # data returned from the serial line must be converted from two 8 bit high and low to single 16 bit integer
            data = struct.unpack(BYTE_ORDER+FORMAT_CHARACTER, bytes(s[BYTE_5:]))
            # order of the unpacking is according to the transport protocol Active mode in the datasheet
            pm1_standard, pm25_standard, pm10_standard, pm1_env, pm25_env, pm10_env, particles_03um, particles_05um, particles_10um, particles_25um, particles_50um, particles_100um, skip, checksum = data
            # compare the checksum byte to the sum of each byte of the frame excluding the checksum bytes
            # i.e checksum = byte1 + byte2 + ... + byte30
            check = 0
            for i in range(CHECKSUM_FRAME_LENGTH):
                check += ord(s[i])
            if check == checksum:
                #print "Concentration Units (ug/m^3)"
                #print "---------------------------------------"
                #print "PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm1_standard, pm25_standard, pm10_standard)
                #print "---------------------------------------"
                #csvwrite([time(), pm1_standard, pm25_standard, pm10_standard])
                data = {'data1': pm1_standard,
                        'data2': pm25_standard,
                        'data3': pm10_standard }
                data_set.append(data)
                # after taking the AVERAGE_READ number of data, then compute average and log the data
                if len(data_set) >= AVERAGE_READ:
                    average_data = average(data_set)
                    timestamp, avg_pm1, max_pm1, min_pm1, avg_pm25, max_pm25, min_pm25, avg_pm10, max_pm10, min_pm10 = average_data
                    csvwrite([timestamp, min_pm1, avg_pm1, max_pm1, min_pm25, avg_pm25, max_pm25, min_pm10, avg_pm10, max_pm10])
                    del data_set[:]
        sleep(1)

if __name__ == "__main__":
    try:
        if not os.path.isfile('pi_pms5003_log.csv'):
            csvwrite(['timestamp', 'pm1_ug/m^3_min', 'pm1_ug/m^3_avg', 'pm1_ug/m^3_max', 'pm2.5_ug/m^3_min', 'pm2.5_ug/m^3_avg', 'pm2.5_ug/m^3_max', 'pm10_ug/m^3_min', 'pm10_ug/m^3_avg', 'pm10_ug/m^3_max'])
        main()

    except KeyboardInterrupt:
        pass
