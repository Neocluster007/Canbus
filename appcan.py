import time
import os
import json
import requests

import can
import cantools

from vcgencmd import Vcgencmd
import psutil


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
#BitRate = "250000"
#CANDB_Name = "/home/pi/EVO-SmartIoTVehicle-main/candb/thaiev_g9_can.dbc"
#Vehicle_Type = "EVO-G9"

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


os.system(str("sudo ip link set can0 type can bitrate " + BitRate))
os.system("sudo ifconfig can0 up")

CANDB = cantools.database.load_file(str(CANDB_Name))
CAN = can.interface.Bus("can0", bustype="socketcan_ctypes")

vcgm = Vcgencmd()
Device_ID = getserial()
Output = {}

Timeset = 60

try:

    EndLoopTime = time.time() + Timeset

    while True:

        msg = CAN.recv(1.0)

        try:
            msg_tr = CANDB.decode_message(msg.arbitration_id, msg.data)
            Output.update(msg_tr)
            
            # print(Output)

        except Exception:
            pass

        if msg is None:

            print("Timeout occurred, no message.")

        if time.time() > EndLoopTime:

            Output.update({"MAAS_INFORMATION": {
                "DEVICE_ID": Device_ID,
                "vehicle_type": Vehicle_Type,
                "DEVICE_CPU": psutil.cpu_percent(),
                "DEVICE_RAM": psutil.virtual_memory().percent,
                "DEVICE_TEMP": vcgm.measure_temp()},
                "msg_type": "vehicle_can",
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

            EndLoopTime = time.time() + Timeset

except KeyboardInterrupt:
    os.system("sudo ifconfig can0 down")
