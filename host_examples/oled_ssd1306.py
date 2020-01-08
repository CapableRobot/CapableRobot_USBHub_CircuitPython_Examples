#!/usr/bin/env python3
import time

import click

import bridge
import capablerobot_usbhub 
import adafruit_ssd1306

@click.command()
@click.option('--delay', default=50, help='Delay in ms between iterations')
@click.option('--report', default=60, help='Delay in seconds between reporting traffic statistics')
def run(delay, report):
    delay = float(delay) / 1000.0

    hub = capablerobot_usbhub.USBHub()
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, hub.i2c, addr=0x3C)

    print(" -- Running -- ")
    print("  {}".format(time.time()))

    start_time = time.time()
    last_report = time.time()
    good = 0
    total = 0

    while True:
        now = time.time()
        total += 1

        if now - last_report > report:
            
            print("  {:.2f} : {} / {} : {}%".format(now-start_time, good, total, int(100 * good/total)))

            last_report = now
            good = 0
            total = 0

        try:
            oled.fill(0)
            oled.text('Hello World', 0, 0, 1)
            oled.text('USB controlled I2C', 0, 11, 1)
            oled.text("{}".format(time.time()), 0, 21, 1)
            oled.show()

            good += 1
            time.sleep(delay)

        except OSError:
            pass

if __name__ == '__main__':
    run()