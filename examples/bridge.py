import os, sys, inspect

this_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
bridge_folder = os.path.join(this_folder, '..', 'lib', 'CapableRobot_CircuitPython_USBHub_Bridge')

if os.path.exists(bridge_folder):
    os.system("cd {} && git pull".format(bridge_folder))
else:
    os.system("cd {}/../lib/ && git clone https://github.com/CapableRobot/CapableRobot_CircuitPython_USBHub_Bridge".format(this_folder))

for folder in [bridge_folder, os.path.join('..', 'lib')]:
    lib_folder = os.path.join(this_folder, folder)
    lib_load = os.path.realpath(os.path.abspath(lib_folder))

    if lib_load not in sys.path:
        sys.path.insert(0, lib_load)
