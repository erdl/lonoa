#!/bin/bash

if ! pgrep -f "PMS5003" > /dev/null
then
	/home/jason/sensors/raspberry_pi/pms5003/PMS5003_logger.py &>> /home/jason/raspi_log/pms5003_log.txt
fi
