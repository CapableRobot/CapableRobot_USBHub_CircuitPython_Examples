import time

import board
import busio

from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_ssd1306

i2c1 = busio.I2C(board.SCL,  board.SDA)
i2c2 = busio.I2C(board.SCL2, board.SDA2)

buf = bytearray(4)
bmi = I2CDevice(i2c1, 0x68)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c2, addr=0x3C)

with bmi as i2c:
    i2c.write(bytearray([0x7E, 0x11]))  ## Turn on ACCEL
    time.sleep(0.01)
    i2c.write(bytearray([0x41, 0b11]))  ## Set 2G range
    time.sleep(0.01)
    i2c.write(bytearray([0x40, 0x2C]))  ## Set ACCEL output data rate
    time.sleep(0.01)
    i2c.write(bytearray([0x50, 0b00110000])) ## Turn on tap interrupts
    time.sleep(0.01)
    i2c.write(bytearray([0x54, 0b1101])) ## Latch interrupts
    time.sleep(0.01)

display_state = 0

while True:
    
    if display_state == 1:
        oled.fill(0)
        oled.show()
    else:
        display_state -= 1

    time.sleep(0.1)

    with bmi as i2c:
        i2c.write_then_readinto(bytearray([0x1C]), buf)

    data = list(buf)
    
    if data[2] == 0xC0:
        oled.fill(0)
        oled.text('Top Knock', 0, 0, 1)
        oled.show()
        display_state = 4

    if data[2] == 0x20:
        oled.fill(0)
        oled.text('Front Knock', 0, 0, 1)
        oled.show()
        display_state = 4

    if data[2] == 0x90:
        oled.fill(0)
        oled.text('Side Knock', 0, 0, 1)
        oled.show()
        display_state = 4