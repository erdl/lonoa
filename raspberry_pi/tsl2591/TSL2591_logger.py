import tsl2591
from time import sleep, time
import csv
import os

OUTPUT_FILE = 'pi_tsl2591_log.csv'

def csvwrite(data):
    dataCSV = open(OUTPUT_FILE, 'a')
    log = csv.writer(dataCSV)
    log.writerow(data)
    dataCSV.close()

def main():
    tsl = tsl2591.Tsl2591()
    full, ir = tsl.get_full_luminosity()
    lux = tsl.calculate_lux(full, ir)
    print "Luminosity   = {} lux".format(lux)

    csvwrite([timestamp, lux])

if __name__ == "__main__":
    try:
        if not os.path.isfile(OUTPUT_FILE):
            csvwrite(['timestamp', 'lux'])
        while True:
            main()
            sleep(2)

    except KeyboardInterrupt:
        pass