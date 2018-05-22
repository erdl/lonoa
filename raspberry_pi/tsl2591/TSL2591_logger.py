#!/usr/bin/env python

import tsl2591
from time import sleep, time
import csv
import os

OUTPUT_FILE = 'pi_tsl2591_log.csv'

# Number of readings to take before calculating the average
AVERAGE_READ = 300
# Fieldset of keys used to parse the data list to calculate the average
AVERAGE_FIELD = ['data1']

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

def main():
    data_set = []
    while True:
        tsl = tsl2591.Tsl2591()
        full, ir = tsl.get_full_luminosity()
        lux = tsl.calculate_lux(full, ir)
        data = {'data1': lux}
        data_set.append(data)

        #print "Luminosity   = {} lux".format(lux)
        
        if len(data_set) >= AVERAGE_READ:
            average_data = average(data_set)
            timestamp, avg_lux, max_lux, min_lux = average_data
            csvwrite([timestamp, min_lux, avg_lux, max_lux])
            del data_set[:]
        
        sleep(1)

if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'illuminance_lux_min', 'illuminance_lux_avg', 'illuminance_lux_max'])
        main()

    except KeyboardInterrupt:
        pass
