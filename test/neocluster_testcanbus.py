import os
import can
import time

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(19,GPIO.OUT)
GPIO.output(19,GPIO.LOW)

os.system("sudo ip link set can0 type can bitrate 250000")
os.system("sudo ifconfig can0 up")
can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')# socketcan_native
print("Test CAN receive")
print("Press CTRL-C to exit")
try:
    while True:
        msg = can0.recv(1.0)
        print (msg)
        if msg is None:
            print("Timeout occurred, no message.")
            GPIO.output(19,GPIO.LOW)
        else:
            GPIO.output(19,GPIO.HIGH)
            
except KeyboardInterrupt:
    os.system("sudo ifconfig can0 down")
