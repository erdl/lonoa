from time import sleep, time
from Adafruit_CCS811 import Adafruit_CCS811
import csv
import os.path 

def write2csv(data):
	dataCSV = open('pi_ccs811_log.csv', 'a')
	log = csv.writer(dataCSV)
	log.writerow(data)
	dataCSV.close()

###### Initialization for the CCS811 sensor from the Adafruit example.py ######
ccs =  Adafruit_CCS811()

while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0


#adds the file header for new csv
file_exist = os.path.isfile('pi_ccs811_log.csv')
if not file_exist:
	write2csv(['timestamp', 'co2_ppm', 'tvoc_ppb', 'temperature_c'])

while(1):
	if ccs.available():
	    co2 = ccs.geteCO2()
	    tvoc = ccs.getTVOC()
	    temp = ccs.calculateTemperature()
	    timestamp = time()
	    if not ccs.readData():
	      if co2 == 0:
	        pass
	      else:
	        print "timestamp: ", timestamp, ", CO2: ", co2, "ppm, TVOC: ", tvoc, " temp: ", temp
	        write2csv([timestamp, co2, tvoc, temp])
	    else:
	      print "ERROR!"
	      while(1):
	      	pass
	sleep(2)
