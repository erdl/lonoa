#!/bin/bash

if ! pgrep -f "TSL2591" > /dev/null
then
	/home/jason/sensors/raspberry_pi/tsl2591/TSL2591_logger.py &>> /home/jason/raspi_log/tsl2591_log.txt
fi
