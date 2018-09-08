#!/bin/bash

if ! pgrep -f "Si7021" > /dev/null
then
	/home/jason/sensors/raspberry_pi/si7021/Si7021_logger.py &>> /home/jason/raspi_log/si7021_log.txt
fi
