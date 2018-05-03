from Adafruit_BME280 import *
from time import sleep, time
import csv
import os

OUTPUT_FILE = 'pi_bme280_log.csv'

def csvwrite(data):
    dataCSV = open(OUTPUT_FILE, 'a')
    log = csv.writer(dataCSV)
    log.writerow(data)
    dataCSV.close()

def main():
    sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

    timestamp = time()
    degrees = sensor.read_temperature()
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    print 'Temp      = {0:0.3f} deg C'.format(degrees)
    print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
    print 'Humidity  = {0:0.2f} %'.format(humidity)

    csvwrite([timestamp, degrees, hectopascals, humidity])

if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'temperature_c', 'pressure_hPa', 'humidity_%'])
        while True:
            main()
            sleep(2)

    except KeyboardInterrupt:
        pass