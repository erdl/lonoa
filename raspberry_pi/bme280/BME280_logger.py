from Adafruit_BME280 import *
from time import sleep, time
import csv
import os

OUTPUT_FILE = 'pi_bme280_log.csv'

# Number of readings to take before calculating the average
AVERAGE_READ = 300
# Fieldset of keys used to parse the data list to calculate the average
AVERAGE_FIELD = ['data1', 'data2', 'data3']

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
    return avg_data

def main():
    data_set = []
    while True:
        sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()
        data = {'data1': degrees,
                'data2': hectopascals,
                'data3': humidity }
        data_set.append(data)

        #print 'Temp      = {0:0.3f} deg C'.format(degrees)
        #print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
        #print 'Humidity  = {0:0.2f} %'.format(humidity)

        if len(data_set) >= AVERAGE_READ:
            average_data = average(data_set)
            timestamp, avg_temp, avg_pressure, avg_humidity = average_data
            csvwrite([timestamp, avg_temp, avg_pressure, avg_humidity])
            del data_set[:]
        
        sleep(1)

if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'temperature_c', 'pressure_hpa', 'humidity_percent'])
        main()

    except KeyboardInterrupt:
        pass
