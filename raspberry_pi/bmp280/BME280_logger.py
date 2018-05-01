from Adafruit_BMP280 import *
from time import sleep, time
import os
import csv

# BMP280 uses address 0x76 on the I2C bus
I2C_ADDRESS = 0x76

OUTPUT_FILE = 'pi_bmp280_log.csv'


def csvwrite(data):
    dataCSV = open(OUTPUT_FILE, 'a')
    log = csv.writer(dataCSV)
    log.writerow(data)
    dataCSV.close()

def main():
    sensor = BMP280(mode=BMP280_STANDARD,address=I2C_ADDRESS)

    temp = sensor.read_temperature()
    # altitude = sensor.read_altitude()
    # pressure is returned in units of pascals and we would like to convert to hectopascal
    atmospheric_pressure = sensor.read_pressure() / 100
    sealevel_pressure = sensor.read_sealevel_pressure(altitude_m=altitude) / 100

    print 'Temp      = {0:0.1f} deg C'.format(temp)
    print 'Altitude  = {0:0.2f} meters'.format(altitude)
    print 'Atmospheric Pressure  = {0:0.2f} hPa'.format(atmospheric_pressure)
    print 'Sea-Level Pressure = {0:0.2f} hPa'.format(sealevel_pressure)
    csvwrite([time(), temp, altitude, atmospheric_pressure, sealevel_pressure])

if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'temperature_c', 'altitude_m', 'atmospheric-pressure_hPa', 'sealevel-pressure_hPa'])
        while True:
            main()
            sleep(2)

    except KeyboardInterrupt:
        pass