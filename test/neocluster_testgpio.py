import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)
GPIO.output(27,GPIO.LOW)

while True:
    GPIO.output(27,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(27,GPIO.LOW)
    time.sleep(2)