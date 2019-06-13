import os, sys, inspect
import time

import bridge
import capablerobot_usbhub 

hub = capablerobot_usbhub.USBHub()
hub.i2c.enable()

import adafruit_ssd1306
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, hub.i2c, addr=0x3C)

while True:
    try:
        oled.fill(0)
        oled.text('Hello World', 0, 0, 1)
        oled.text("{}".format(time.time()), 0, 10, 1)
        oled.show()

        time.sleep(0.05)
    except OSError:
        pass 