import time
import os
import json
import requests

import can
import cantools

from vcgencmd import Vcgencmd
import psutil


import threading

import time

import os
import glob
import time
import math

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'




def mapfloat(x, in_min, in_max, out_min, out_max):
    return (float)(x - in_min) * (out_max - out_min) / (float)(in_max - in_min) + out_min;

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

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    try:
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f
    except:
        print("Error Data func")

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
# BitRate = "250000"
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/thaiev_g9_can.dbc"
# Vehicle_Type = "EVO-G9"

# L1
BitRate = "250000"
CANDB_Name = "/home/pi/EVO-SmartIoTVehicle-main/candb/thaiev_x1l1_can_protocol.dbc"
Vehicle_Type = "EVO-L1"

# X1
# BitRate = "250000"
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/thaiev_x1l1_can_protocol.dbc"
# Vehicle_Type = "EVO-X1"

# Civic
# CANDB_Name = "/home/pi/EVO-SmartVehicle_THAIEV-G9/candb/honda_civic_hatchback_ex_2017_can_generated.dbc"
# BitRate = "500000"
# Vehicle_Type = "HONDA-Civic"

'''
os.system(str("sudo ip link set can0 type can bitrate " + BitRate))
os.system("sudo ifconfig can0 up")

CANDB = cantools.database.load_file(str(CANDB_Name))
CAN = can.interface.Bus("can0", bustype="socketcan_ctypes")
'''
vcgm = Vcgencmd()
Device_ID = getserial()
Output = {}

Timeset = 60

val_temp = 0;

val_temp = 0;
val_humidity = 0;

try:
    print("Start LOOP")
    EndLoopTime = time.time() + Timeset

    while True:
        
        
        if time.time() > EndLoopTime:
            try:
                try:

                    val_temp = read_temp()[0]
                    val_humidity = read_temp()[1]*(-1)
                    #print(str(val_temp) + " : " + str(math.isnan(val_temp)))
                except:
                    print("Data Error ")

                if math.isnan(val_temp) == False :
                    Output.update({"MAAS_INFORMATION": {
                        "DEVICE_ID": Device_ID,
                        "vehicle_type": Vehicle_Type,
                        "DEVICE_CPU": psutil.cpu_percent(),
                        "DEVICE_RAM": psutil.virtual_memory().percent,
                        "DEVICE_TEMP": vcgm.measure_temp()},
                        "msg_type": "vehicle_can",
                        "PlateNumber":685272,
                        "temparature_C":val_temp,
                        "humidity":val_humidity
                    })

                    JsonOutput = json.dumps(Output, indent=2)

                    try:
                        requests.post("https://maas-gps.servicebus.windows.net/vehicle-can/messages?timeout=60&api-version=2014-01",
                                    headers={
                                        "Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=tW%2BHuE59CxD9759f%2BEGR916eHv96eQo4kjo3sWFWZ1k%3D&se=1816746314&skn=VehicleCanManagePolicy",
                                        "Content-Type": "application/atom+xml;type=entry;charset=utf-8.",
                                    },
                                    data=JsonOutput,)

                        print(JsonOutput)

                    except Exception:
                        print("Json Temp Not send")
                        pass

                    
                    
                    
                '''
                    
                Output.update({"MAAS_INFORMATION": {
                    "DEVICE_ID": Device_ID,
                    "vehicle_type": Vehicle_Type,
                    "DEVICE_CPU": psutil.cpu_percent(),
                    "DEVICE_RAM": psutil.virtual_memory().percent,
                    "DEVICE_TEMP": vcgm.measure_temp()},
                    "msg_type": "vehicle_can",
                    "PlateNumber":685272,
                    "temparature_C":val_temp,
                    "humidity":val_humidity
                })

                JsonOutput = json.dumps(Output, indent=2)

                try:
                    requests.post("https://maas-gps.servicebus.windows.net/vehicle-can/messages?timeout=60&api-version=2014-01",
                                  headers={
                                      "Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=tW%2BHuE59CxD9759f%2BEGR916eHv96eQo4kjo3sWFWZ1k%3D&se=1816746314&skn=VehicleCanManagePolicy",
                                      "Content-Type": "application/atom+xml;type=entry;charset=utf-8.",
                                  },
                                  data=JsonOutput,)

                    print(JsonOutput)

                except Exception:
                    pass
                '''
                    
            except:
                print("An exception occurred")

            EndLoopTime = time.time() + Timeset

except KeyboardInterrupt:
    os.system("sudo ifconfig can0 down")
