import serial
import time
import click

_SLIP_END = 0xC0
_SLIP_ESC = 0xDB
_SLIP_ESC_END = 0xDC
_SLIP_ESC_ESC = 0xDD
_EOT = 0x04

_CHR_OFFSET        = 0x30
_CMD_PORT_POWER_EN = 0x41
_CMD_PORT_DATA_EN  = 0x42

class USBHub():

    def __init__(self, port):
        self.port = port

        self.handle = serial.Serial(
            port=port, baudrate=115200, 
            bytesize=8, parity='N', stopbits=1, 
            xonxoff=False, rtscts=False,
            timeout=0.5
        )

    def close(self):
        self.handle.flush()
        self.handle.close()

    def write(self, buf):
        encoded = [_SLIP_END]

        for byte in buf:
            if byte == _SLIP_END:
                encoded.append(_SLIP_ESC)
                encoded.append(_SLIP_ESC_END)
            elif byte == _SLIP_ESC:
                encoded.append(_SLIP_ESC)
                encoded.append(_SLIP_ESC_ESC)
            else:
                encoded.append(byte)

        encoded.append(_SLIP_END)

        ## Must send EOT to prevent MCU from waiting for more data
        encoded.append(_EOT) 

        self.handle.write(bytes(encoded))

        for line in self.handle.readlines():
            out = []
            data = bytearray(line)

            while True:
                if len(data) == 0:
                    break

                byte = data.pop(0)

                if byte == _SLIP_END:
                    if len(out) > 0:
                        return out

                elif byte == _SLIP_ESC:
                    if len(data) == 0:
                        break
                    elif byte == _SLIP_ESC_END:
                        out.append(_SLIP_END)
                    elif byte == _SLIP_ESC_ESC:
                        out.append(_SLIP_ESC)
                    else:
                        break
                else:
                    out.append(byte)

    def power_enable(self, ports=[]):
        for port in ports:
            self.write([_CMD_PORT_POWER_EN, port+_CHR_OFFSET, _CHR_OFFSET+1])

    def power_disable(self, ports=[]):
        for port in ports:
            self.write([_CMD_PORT_POWER_EN, port+_CHR_OFFSET, _CHR_OFFSET])

    def power_state(self):
        value = self.write([_CMD_PORT_POWER_EN, _CHR_OFFSET, _CHR_OFFSET])[2:]
        return ["on" if idx else "off" for idx in value]

    def data_enable(self, ports=[]):
        for port in ports:
            self.write([_CMD_PORT_DATA_EN, port+_CHR_OFFSET, _CHR_OFFSET+1])

    def data_disable(self, ports=[]):
        for port in ports:
            self.write([_CMD_PORT_DATA_EN, port+_CHR_OFFSET, _CHR_OFFSET])

    def data_state(self):
        value = self.write([_CMD_PORT_DATA_EN, _CHR_OFFSET, _CHR_OFFSET])[2:]
        return ["on" if idx else "off" for idx in value]

COL_WIDTH = 12
PORTS = ["Port {}".format(num) for num in [1,2,3,4]]


def _print_row(data):
    print(*[str(v).rjust(COL_WIDTH) for v in data])

@click.group()
@click.option('--port', 'port', default='/dev/ttyUSB0', help='Serial port of USB Hub MCU')
@click.option('--verbose', default=False, is_flag=True, help='Increase logging level.')
def cli(port, verbose):
    global hub

    hub = USBHub(port=port)

@cli.group()
def data():
    """Sub-commands for data control & monitoring"""
    pass

@data.command()
@click.option('--port', default=None, help='Comma separated list of ports (1 thru 4) to act upon.')
@click.option('--on', default=False, is_flag=True, help='Enable data to the listed ports.')
@click.option('--off', default=False, is_flag=True, help='Disable data to the listed ports.')
def state(port, on, off):
    """ Get or set per-port data state.  With no arguments, will print out if port data is on or off. """

    if on and off:
        print("Error : Please specify '--on' or '--off', not both.")
        return

    if on or off:
        if port is None:
            print("Error : Please specify at least one port with '--port' flag")
            return
        else:
            port = [int(p) for p in port.split(",")]

    if on:
        hub.data_enable(ports=port)
    elif off:
        hub.data_disable(ports=port)
    else:
        _print_row(PORTS)
        _print_row(hub.data_state())
        # _print_row(hub.speeds())

@cli.group()
def power():
    """Sub-commands for power control & monitoring"""
    pass

@power.command()
@click.option('--port', default=None, help='Comma separated list of ports (1 thru 4) to act upon.')
@click.option('--on', default=False, is_flag=True, help='Enable power to the listed ports.')
@click.option('--off', default=False, is_flag=True, help='Disable power to the listed ports.')
@click.option('--reset', default=False, is_flag=True, help='Reset power to the listed ports (cycles power off & on).')
@click.option('--delay', default=500, help='Delay in ms between off and on states during reset action.')
def state(port, on, off, reset, delay):
    """ Get or set per-port power state.  With no arguments, will print out if port power is on or off. """

    if on and off:
        print("Error : Please specify '--on' or '--off', not both.")
        return

    if on or off or reset:
        if port is None:
            print("Error : Please specify at least one port with '--port' flag")
            return
        else:
            port = [int(p) for p in port.split(",")]

    if on:
        hub.power_enable(ports=port)
    elif off:
        hub.power_disable(ports=port)
    elif reset:
        hub.power_disable(ports=port)
        time.sleep(float(delay)/1000)
        hub.power_enable(ports=port)
    else:
        _print_row(PORTS)
        _print_row(hub.power_state())

def main():
    cli()

if __name__ == '__main__':
    main()
