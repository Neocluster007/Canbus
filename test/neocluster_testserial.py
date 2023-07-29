import serial
import time
import string
import pynmea2
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(13,GPIO.OUT)
GPIO.output(13,GPIO.LOW)

while True:
    port="/dev/ttyAMA0"
    ser=serial.Serial(port,baudrate=9600,timeout=0.5)
    dataout =pynmea2.NMEAStreamReader()
    newdata=ser.readline()
    if newdata[0:6]=="$GPRMC":
        newmsg=pynmea2.parse(newdata)
        lat=newmsg.latitude
        lng=newmsg.longitude
        
        if lat != 0 and lng != 0:
            GPIO.output(6,GPIO.HIGH)
        else:
            GPIO.output(6,GPIO.LOW)
        
        gps="Latitude=" +str(lat) + " : Longitude=" +str(lng)
        print(gps)
