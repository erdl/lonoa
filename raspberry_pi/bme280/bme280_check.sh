#!/bin/bash

if ! pgrep -f "BME280" > /dev/null
then
	/home/jason/sensors/raspberry_pi/bme280/BME280_logger.py &>> /home/jason/raspi_log/bme280_log.txt
fi
