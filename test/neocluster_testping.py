import platform
import subprocess
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(6,GPIO.OUT)
GPIO.output(6,GPIO.LOW)

def myping(host):
    parameter = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', parameter, '1', host]
    response = subprocess.call(command)
    if response == 0:
        GPIO.output(6,GPIO.HIGH)
        return True
    else:
        GPIO.output(6,GPIO.LOW)
        return False
print(myping("www.google.com"))