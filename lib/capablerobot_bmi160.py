import time
import math

try:
    import logging
except ImportError:
    import adafruit_logging as _logging
    logging = _logging.getLogger('BMI160')

from adafruit_bus_device.i2c_device import I2CDevice

_REG_ID = 0x00
_REG_DUMMY = 0x7F
_REG_TIME  = 0x18
_REG_INT   = 0x1C
_REG_TEMP  = 0x20
_REG_INTERFACE_CONF = 0x6B

SENSOR_TIME_LSB = 39e-6

def set_bit(value, bit):
    return value | (1<<bit)

def clear_bit(value, bit):
    return value & ~(1<<bit)

def bytearry_to_int(b):
    x = 0
    for c in b:
        x <<= 8
        x |= c
    return x

class BMI160:

    # Class-level buffer to reduce allocations and heap fragmentation.
    # This is not thread-safe or re-entrant by design!
    _BUFFER = bytearray(6)

    def __init__(self, device, use_spi=True):

        self.device = device
        self.use_spi = use_spi

        ## Read from 0x7F to turn on SPI
        if use_spi:
            self._read_register(_REG_DUMMY)

            time.sleep(0.01)

            # Set SPI mode to 4 wire (bit 0 -> 0)
            # Without this, BMI160 sometimes reverts to 3 wire SPI, cause is unknown
            self._write_register(_REG_INTERFACE_CONF, [0x00])

        self.setup()

    def _read_register(self, reg, length=1):
        if self.use_spi:
            # First bit has to be 1 for BMI160 to know that the
            # SPI transaction is for an address read
            self._BUFFER[0] = set_bit(reg, 7)
        else:
            self._BUFFER[0] = reg

        with self.device as device:
            # device.write(self._BUFFER, end=1)
            # device.readinto(self._BUFFER, start=1, end=length+1)
            device.write_readinto(self._BUFFER, self._BUFFER, out_end=1, in_start=1, in_end=length+1)

        return self._BUFFER[1:length+1]

    def _write_register(self, reg, values):
        if self.use_spi:
            # First bit has to be 0 for BMI160 to know that the
            # SPI transaction is for an address write
            self._BUFFER[0] = clear_bit(reg, 7)
        else:
            self._BUFFER[0] = reg

        with self.device as device:
            device.write(self._BUFFER[0:1] + bytearray(values))


    def setup(self):
        setup = [
            [0x7E, 0x11], ## Turn on ACCEL
            [0x7E, 0x15], ## Turn on GYRO
            [0x41, 0b11], ## Set 2G range
            [0x40, 0x2C], ## Set ACCEL output data rate
            [0x50, 0b00110000], ## Turn on tap interrupts
            [0x54, 0b1101] ## Latch interrupts
        ]

        for packet in setup:
            self._write_register(packet[0], [packet[1]])

            time.sleep(0.01)

    @property
    def id(self):
        value = self._read_register(_REG_ID)[0]

        if value == 0xD1:
            return "BMI160"
        else:
            return "Device unknown"

    @property
    def temperature(self):
        data = self._read_register(_REG_TEMP, length=2)
        reading = data[1] << 8 | data[0]

        if reading & 0x8000:
            return (23.0 - ((0x10000 - reading)/512.0))
        else:
            return ((float(reading)/512.0) + 23.0)

    @property
    def interrupts(self):
        return self._read_register(_REG_INT, length=3)
    
        

    @property
    def time(self):
        data = self._read_register(_REG_TIME, length=3)
        reading = data[2] << 16 | data[1] << 8 | data[0]
        return float(reading)*SENSOR_TIME_LSB
        