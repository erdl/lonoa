#!/bin/bash

if ! pgrep -f "BMP280" > /dev/null
then
	/home/jason/sensors/raspberry_pi/bmp280/BMP280_logger.py &>> /home/jason/raspi_log/bmp280_log.txt
fi
