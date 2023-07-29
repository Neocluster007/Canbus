import serial
import time
import string 
import pynmea2
port="/dev/ttyAMA0"
ser=serial.Serial(port,baudrate=9600,timeout=0.5)
dataout =pynmea2.NMEAStreamReader()
while True:
	try:
		newdata=ser.readline()
		newdataK=newdata.decode("utf-8")
		print(newdataK)
		if newdataK[0:6]=="$GPRMC":
			newmsg=pynmea2.parse(newdataK)
			lat=newmsg.latitude
			lng=newmsg.longitude
			gps="Latitude=" +str(lat) + "and Longitude=" +str(lng)
			print(gps)
	except:
		pass
