# Hub Control over MCU Port

This directory holds Host and MCU software which enable the Programmable USB Hub to be controlled over the MCU USB Port.

For control of the USB Hub over the Host USB Port, please install the [Host Driver](https://github.com/CapableRobot/CapableRobot_USBHub_Driver).

## Installation on the MCU

To enable this USB-serial control and monitoring interface, the MCU's firmware must be upgraded.  To do this:

- First download the current release of MCU firmware from the [Firmware Repository](https://github.com/CapableRobot/CapableRobot_USBHub_Firmware).
- Copy the contents of the 'lib' folder from the downloaded code to the USB Hub's 'CIRCUITPY/lib' folder, which will appear as a USB mass-storage drive once the MCU port is connected to a host, and power applied to the USB Hub.
- Copy the 'code.py' and 'capablerobot_host.py' files within the 'mcu' folder in this repository to the mounted CIRCUITPY drive.
- Reboot the USB Hub

Your Hub should now respond to the USB serial commands via the Host software (see below).

## Installation on the Host

- Download the 'capablerobot_host.py' inside of the 'host' folder.
- Install depedencies : `pip install pyserial` and `pip install click`
- Run : `python capablerobot_mculink.py --help`

The file implements a command-line interface which is similar to the [Host-side Python Driver](https://github.com/CapableRobot/CapableRobot_USBHub_Driver), but it can also be used as a Python library within a larger Python program or script.
