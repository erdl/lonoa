import pigpio
import time

pi = pigpio.pi()

device = pi.i2c_open(1, 0x40)

while True:
    device = pi.i2c_write_byte(device, 0xF5)
    time.sleep(0.1)
    a, b = pi.i2c_read_device(device, 2)

    hum_LSB = b[0] << 8
    humidity = hum_LSB + b[1]
    humidity = humidity * 125
    humidity = humidity / 65536
    humidity = humidity - 6

    print("Humidity = " + str(humidity))

    pi.i2c_write_byte(device, 0xE0)
    c, d = pi.i2c_read_device(device, 2)

    temp_MSB = d[0] << 8
    temperature = temp_MSB + d[1]
    temperature = temperature * 172.72
    temperature = temperature / 65536
    temperature = temperature - 46.85

    print("Temperature = " + str(round(temperature, 2)))

    time.sleep(1)