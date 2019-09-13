import time
import logging
import sys

import bridge
import capablerobot_usbhub 
import capablerobot_bmi160

def setup_logging():
    fmtstr = '%(asctime)s | %(filename)25s:%(lineno)4d %(funcName)20s() | %(levelname)7s | %(message)s'
    formatter = logging.Formatter(fmtstr)

    handler   = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

# setup_logging()

hub = capablerobot_usbhub.USBHub()
bmi = capablerobot_bmi160.BMI160(hub.spi, use_spi=True)

print(bmi.id)

while True:
	print(bmi.time, bmi.temperature)
	time.sleep(1)
