import supervisor
import sys
import time

import digitalio
import board

_SLIP_END = 0xC0
_SLIP_ESC = 0xDB
_SLIP_ESC_END = 0xDC
_SLIP_ESC_ESC = 0xDD
_EOT = 0x04

_CHR_OFFSET        = 0x30
_CMD_PORT_POWER_EN = 0x41
_CMD_PORT_DATA_EN  = 0x42

class Host():

    def __init__(self, hub):
        self.hub = hub

        self._buf_in = []
        self._buf_msg = []
        self._buf_out = []

    @property
    def connected(self):
        return supervisor.runtime.serial_connected

    @property
    def serial_bytes_available(self):
        return supervisor.runtime.serial_bytes_available

    def fill_in_buffer(self):
        if supervisor.runtime.serial_bytes_available:
            data = bytearray(sys.stdin.read(1))
            
            for byte in data:
                if byte == '\r' or byte == '\n':
                    continue
                else:
                    self._buf_in.append(byte)

            return True

        return False

    def message_send(self, buf):
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

        ## Must send newline for host to see data
        encoded.append(0x13)
        encoded.append(0x10) 

        sys.stdout.write(bytes(encoded))

    def message_received(self):

        while True:
            if len(self._buf_in) == 0:
                return False

            ## Consume byte
            byte = self._buf_in.pop(0)

            if byte == _SLIP_END:
                ## Let caller know there is a message 
                return len(self._buf_msg) > 0

            elif byte == _SLIP_ESC:

                if len(self._buf_in) == 0:
                    ## We got an escape, but not the next byte
                    ## Push back onto queue and return
                    self._buf_in.insert(0, byte)
                    return False

                next_byte = self._buf_in.pop(0)

                if next_byte == _SLIP_ESC_END:
                    self._buf_msg.append(_SLIP_END)
                elif next_byte == _SLIP_ESC_ESC:
                    self._buf_msg.append(_SLIP_ESC)
                else:
                    ## Protocol error, let's clear everything
                    self._buf_msg.clear()
                    self._buf_in.clear()
                    return False

            else:
                # print("MSG BYTE", hex(byte))
                ## Move byte from input stream to message
                self._buf_msg.append(byte)

    def exec_port_power(self):
        port  = self._buf_msg[1] - _CHR_OFFSET
        value = self._buf_msg[2] - _CHR_OFFSET

        if port == 0:
            return self.hub.power_state()

        if value:
            self.hub.power_enable(ports=[port])
        else:
            self.hub.power_disable(ports=[port])

        return None

    def exec_port_data(self):
        port  = self._buf_msg[1] - _CHR_OFFSET
        value = self._buf_msg[2] - _CHR_OFFSET

        if port == 0:
            return self.hub.data_state() + [not self.hub.pin_hen.value]

        if port == 5:
            ## Handle host port control
            self.hub.upstream(state=value)
            return None

        if value:
            self.hub.data_enable(ports=[port])
        else:
            self.hub.data_disable(ports=[port])

        return None
    

    def process_queue(self):
        self.fill_in_buffer()
        
        if self.message_received():
            
            cmd = self._buf_msg[0]
            value = None

            if cmd == _EOT:
                pass
            elif cmd == _CMD_PORT_POWER_EN:
                value = self.exec_port_power()
            elif cmd == _CMD_PORT_DATA_EN:
                value = self.exec_port_data()

            if value is not None:
                self.message_send([cmd, self._buf_msg[1]] + value)

            self._buf_msg.clear()
    