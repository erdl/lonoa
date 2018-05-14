import pigpio
import time

# I2C Address for the Si7021
I2C_ADDRESS = 0x40
# Access Bus 1 on the Raspberry Pi
BUS = 1

# Si7021 Commands for Taking Measurements
CMD_RH = 0xF5
CMD_TEMP = 0xE0

# Convert a two bytes string into a 16 bit integer
def int16bit(b):
    return(b[0] << 8) + (b[1])

def relative_humidity(raw):
    return raw * 125.0 / 65536.0 - 6.0

def temperature(raw):
    return raw * 175.72 / 65536.0 - 46.85

pi = pigpio.pi()
device = pi.i2c_open(BUS, I2C_ADDRESS)

while True:
    device = pi.i2c_write_byte(device, CMD_RH)
    time.sleep(0.1)
    a, b = pi.i2c_read_device(device, 2)
    raw_humidity = int16bit(b)
    humidity = relative_humidity(raw_humidity)
    print("Humidity = " + str(round(humidity, 3)))
    
    
    pi.i2c_write_byte(device, CMD_TEMP)
    c, d = pi.i2c_read_device(device, 2)
    raw_temp = int16bit(d)
    temp = temperature(raw_temp)
    print("Temperature = " + str(round(temp, 3)))
    
    time.sleep(1)
