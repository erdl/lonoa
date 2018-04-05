from time import sleep, time
import serial
import struct
import os
import csv

def csvwrite(data):
    dataCSV = open('pi_pms5003_log.csv', 'a')
    log = csv.writer(dataCSV)
    log.writerow(data)
    dataCSV.close()

def main():
    # "/dev/ttyAMA0" is the serial port for the raspberry pi 2
    # 9600 is the default baudrate for the PMS5003 sensor
    # default value of 2 second timeout
    ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2.0) # open serial port
    # frame length is 32 bytes
    s = ser.read(32)
    # check first start byte is 0x42 and second start byte is 0x4d
    if s[0] == b'\x42' and s[1] == b'\x4d':
        # data returned from the serial line must be converted from two 8 bit high and low to single 16 bit integer
        data = struct.unpack(">HHHHHHHHHHHHHH", bytes(s[4:]))
        # order of the unpacking is according to the transport protocol Active mode in the datasheet
        pm1_standard, pm25_standard, pm10_standard, pm1_env, pm25_env, pm10_env, particles_03um, particles_05um, particles_10um, particles_25um, particles_50um, particles_100um, skip, checksum = data
        # compare the checksum byte to the sum of the fram values from s[0] + s[1] + ... + s[29]
        check = 0
        for i in range(30):
            check += ord(s[i])
        if check == checksum:
            print "Concentration Units (ug/m^3)"
            print "---------------------------------------"
            print "PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm1_standard, pm25_standard, pm10_standard)
            print "---------------------------------------"
            csvwrite([time(), pm1_standard, pm25_standard, pm10_standard])

if __name__ == "__main__":
    try:
        if not os.path.isfile('pi_pms5003_log.csv'):
            csvwrite(['timestamp', 'pm1_ug/m^3', 'pm2.5_ug/m^3', 'pm10_ug/m^3'])
        while True:
            main()
            sleep(2)

    except KeyboardInterrupt:
        pass
