from Adafruit_BMP280 import *
from time import sleep, time
import os
import csv

# BMP280 uses address 0x76 on the I2C bus
I2C_ADDRESS = 0x76

OUTPUT_FILE = 'pi_bmp280_log.csv'

# Number of readings to take before calculating the average
AVERAGE_READ = 300
# Fieldset of keys used to parse the data list to calculate the average
AVERAGE_FIELD = ['data1', 'data2', 'data3', 'data4']

def csvwrite(data):
    dataCSV = open(OUTPUT_FILE, 'a')
    log = csv.writer(dataCSV)
    log.writerow(data)
    dataCSV.close()

def getsealevel_pa():
    dataCSV = open(OUTPUT_FILE, 'r')
    last_row = dataCSV.readlines()[-1]
    try:
        sealevel_pa = float(last_row.split(",")[4] * 100)
        return sealevel_pa
    except ValueError:
        # default value for sea level pressure
        return 101630.0

def average(data_list):
    avg_data = []
    avg_data.append(time())
    for key in AVERAGE_FIELD:
        avg_data.append(float((sum(data[key] for data in data_list)) / len(data_list)))
    return avg_data

def main():
    data_set = []
    while True:
        sensor = BMP280(mode=BMP280_ULTRAHIGHRES,address=I2C_ADDRESS)

        temp = sensor.read_temperature()
        altitude = sensor.read_altitude(sealevel_pa=getsealevel_pa())
        # pressure is returned in units of pascals and we would like to convert to hectopascal
        atmospheric_pressure = sensor.read_pressure() / 100
        sealevel_pressure = sensor.read_sealevel_pressure(altitude_m=altitude) / 100
        data = {'data1': temp,
                'data2': altitude,
                'data3': atmospheric_pressure,
                'data4': sealevel_pressure }
        data_set.append(data)

        #print 'Temp      = {0:0.1f} deg C'.format(temp)
        #print 'Altitude  = {0:0.2f} meters'.format(altitude)
        #print 'Atmospheric Pressure  = {0:0.2f} hPa'.format(atmospheric_pressure)
        #print 'Sea-Level Pressure = {0:0.2f} hPa'.format(sealevel_pressure)
        
        if len(data_set) >= AVERAGE_READ:
            average_data = average(data_set)
            timestamp, avg_temp, avg_altitude, avg_pressure, avg_sealvl_pressure = average_data
            csvwrite([timestamp, avg_temp, avg_altitude, avg_pressure, avg_sealvl_pressure])
            del data[:]
        
        sleep(1)

if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'temperature_c', 'altitude_m', 'atmospheric-pressure_hpa', 'sealevel-pressure_hpa'])
        main()

    except KeyboardInterrupt:
        pass
