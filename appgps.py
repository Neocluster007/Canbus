import time
import datetime
import schedule
import os
import json
import requests

import RPi.GPIO as GPIO

import can
import cantools

from vcgencmd import Vcgencmd
import psutil

import serial
import pynmea2

# BUS
# BitRate = "250000"
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/zhiyuan_VCUinfo.dbc"
# Vehicle_Type = "EVO-BUS"

# V1
# BitRate = "250000"
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/thaiev_v9_vcu_protocol.dbc"
# Vehicle_Type = "EVO-V1"

# V9
# BitRate = "250000"
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/thaiev_v9_vcu_protocol.dbc"
# Vehicle_Type = "EVO-V9"

# G1
# BitRate = "250000"
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/thaiev_g9_can.dbc"
# Vehicle_Type = "EVO-G1"

# G9
BitRate = "250000"
CANDB_Name = "/home/pi/EVO-SmartIoTVehicle-main/candb/thaiev_g9_can.dbc"
#Vehicle_Type = "EVO-G9"

# L1
#BitRate = "250000"
#CANDB_Name = "/home/pi/EVO-SmartIoTVehicle-main/candb/thaiev_x1l1_can_protocol.dbc"
Vehicle_Type = "EVO-L1"

# X1
# BitRate = "250000"
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/thaiev_x1l1_can_protocol.dbc"
# Vehicle_Type = "EVO-X1"

# Civic
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/honda_civic_hatchback_ex_2017_can_generated.dbc"
# BitRate = "500000"
# Vehicle_Type = "HONDA-Civic"

GPS_File = "/dev/ttyAMA0"

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(19, GPIO.OUT)
# GPIO.output(19, GPIO.LOW)

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(13, GPIO.OUT)
# GPIO.output(13, GPIO.LOW)

vcgm = Vcgencmd()

JsonOutput = {}
Test = []


def getserial():
    cpuserial = "0000000000000000"
    try:
        f = open("/proc/cpuinfo", "r")
        for line in f:
            if line[0:6] == "Serial":
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial


def convert_to_degrees(raw_value):

    decimal_value = raw_value / 100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value)) / 0.6
    position = degrees + mm_mmmm
    position = "%.4f" % (position)
    return position


def GPS():

    Device_ID = getserial()

    #ser=serial.Serial(port,baudrate=9600,timeout=0.5)

    #Line = File.readline().decode("utf-8")
    ser=serial.Serial(GPS_File,baudrate=9600,timeout=0.5)
    #File = open(GPS_File, "r")
    
    GNRMC_Datetime = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))

    GPVTG_Speed = "0"
    GPVTG_Angle = "0"

    GPGGA_Altitude = "0"
    GPGGA_Geoidal_Seperation = "0"

    GPGSV_Satellite = 0

    GPRMC_Latitude = "0"
    GPRMC_Longitude = "0"

    try:

        
        Line=ser.readline().decode("utf-8")

        EndLoopTime = time.time() + 1

        while time.time() < EndLoopTime:
            
            if Line[0:6] == "$GNRMC":

                Data = Line.split(",")

                # Data : datetime
                if Data[1] == "" or Data[9] == "":
                    GNRMC_Datetime = str(
                        datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
                    )
                else:
                    GNRMC_Datetime = str(
                        Data[9][4:6]
                        + "-"
                        + Data[9][2:4]
                        + "-"
                        + Data[9][0:2]
                        + " "
                        + Data[1][0:2]
                        + ":"
                        + Data[1][2:4]
                        + ":"
                        + Data[1][4:6]
                    )

            if Line[0:6] == "$GPVTG":

                Data = Line.split(",")

                # Data : speed
                if Data[7] == "":
                    GPVTG_Speed = str(0)
                else:
                    GPVTG_Speed = str(float(Data[7]))

                # Data : angle
                if Data[1] == "":
                    GPVTG_Angle = str(0)
                else:
                    GPVTG_Angle = str(float(Data[1]))

            if Line[0:6] == "$GPGGA":

                Data = Line.split(",")

                # Data : Mean Sea Level Altitude
                if Data[9] == "":
                    GPGGA_Altitude = str(0)
                else:
                    GPGGA_Altitude = str(Data[9])

                # Data : Geoidal Seperation
                if Data[11] == "":
                    GPGGA_Geoidal_Seperation = str(0)
                else:
                    GPGGA_Geoidal_Seperation = str(Data[11])

            if Line[0:6] == "$GPGSV":

                Data = Line.split(",")

                # Data : Satellite in view
                if Data[3] == "":
                    GPGSV_Satellite = str(0)
                else:
                    GPGSV_Satellite = str(Data[3])

            if Line[0:6] == "$GPRMC":

                Data = Line.split(",")

                # Data : latitude
                if Data[3] == "":
                    # GPIO.output(6, GPIO.LOW)
                    print("GPS no singal")
                    return
                else:
                    GPRMC_Latitude = str(convert_to_degrees(float(Data[3])))

                # Data : longitude
                if Data[3] == "":
                    # GPIO.output(6, GPIO.LOW)
                    print("GPS no singal")
                    return
                else:
                    GPRMC_Longitude = str(convert_to_degrees(float(Data[5])))

            Line = File.readline()

        if float(GPRMC_Latitude) > 0 and float(GPRMC_Longitude) > 90:

            Output = {
                "MAAS_INFORMATION": {
                    "DEVICE_ID": Device_ID,
                    "vehicle_type": Vehicle_Type,
                    "DEVICE_CPU": psutil.cpu_percent(),
                    "DEVICE_RAM": psutil.virtual_memory().percent,
                    "DEVICE_TEMP": vcgm.measure_temp(),
                },
                "msg_type": "vehicle_gps",
                "datetime": str(
                    datetime.datetime.strptime(
                        GNRMC_Datetime, "%y-%m-%d %H:%M:%S")
                ),
                "latitude": float(GPRMC_Latitude),
                "longitude": float(GPRMC_Longitude),
                "speed": float(GPVTG_Speed),
                "heading": float(GPVTG_Angle),
                "altitude": float(GPGGA_Altitude),
                "geoid": float(GPGGA_Geoidal_Seperation),
                "gp_satellite": float(GPGSV_Satellite)
            }

            JsonOutput = json.dumps(Output, indent=2)

            File.close()

            requests.post(
                "https://maas-gps.servicebus.windows.net/gps/messages?timeout=60&api-version=2014-01",
                headers={
                    "Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=wGD%2FkmpXG4Uljx14q9kRMNXF9LZYCjaFb8z0%2F%2Fv2yZE%3D&se=1814589186&skn=SendSharedAccessKey",
                    "Content-Type": "application/atom+xml;type=entry;charset=utf-8.",
                },
                data=JsonOutput,
            )

            # GPIO.output(6, GPIO.HIGH)
            print(JsonOutput)
            return

    except:
        # GPIO.output(6, GPIO.LOW)
        print("GPS Error")
        return


schedule.every(15).seconds.do(GPS)

while True:
    schedule.run_pending()
    time.sleep(1)
