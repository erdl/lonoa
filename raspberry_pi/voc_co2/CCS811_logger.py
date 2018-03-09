from time import sleep, time
from Adafruit_CCS811 import Adafruit_CCS811
import csv
import os.path 

def write2csv(data):
	dataCSV = open('CCS811_log.csv', 'a')
	log = csv.writer(dataCSV)
	log.writerow(data)
	dataCSV.close()

ccs =  Adafruit_CCS811()

while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0

file_exist = os.path.isfile('CCS811_log.csv')
if not file_exist:
	write2csv(['Timestamp', 'CO2 (ppm)', 'TVOC (ppb)', 'Temperature (C)'])

while(1):
	if ccs.available():
	    CO2 = ccs.geteCO2()
	    TVOC = ccs.getTVOC()
	    temp = ccs.calculateTemperature()
	    timestamp = time()
	    if not ccs.readData():
	      print "timestamp: ", timestamp, ", CO2: ", CO2, "ppm, TVOC: ", TVOC, " temp: ", temp
	      write2csv([timestamp, CO2, TVOC, temp])
	    else:
	      print "ERROR!"
	      while(1):
	      	pass
	sleep(2)