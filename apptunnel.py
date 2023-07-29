import threading
import time
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import asyncio
import os

from azure.servicebus.aio import ServiceBusClient
A=0
NAMESPACE_CONNECTION_STR = "Endpoint=sb://maas-iot.servicebus.windows.net/;SharedAccessKeyName=TunnelListener;SharedAccessKey=07wteQMxzwotmSbYlIzGuFINLgELDiUV7+ASbC0L8pc=;EntityPath=tunnel-trigger"
SUBSCRIPTION_NAME = "S1"
TOPIC_NAME = "tunnel-trigger"
API_Host_URL = "https://maas-apigateway.azure-api.net"
#API_Host_URL = "https://maas-core-dev.azurewebsites.net"
API_Key_Authen = "b3233d3da2fb4855b6d152571fa9e3b1"

Timeset = 60
Timeset_1 = 1
Output = {}
Output_A = {}
receiver = None

def get_serial():
    cpuserial = "0000000000000000"
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    cpuserial = line[10:26]
        return cpuserial
    except Exception:
        return "ERROR000000000"

Device_ID = get_serial()
#Device_ID = "0001"
SUBSCRIPTION_NAME = Device_ID

print("ID_Device =", Device_ID)

f = open("IDDevice.txt", "w")
f.write(Device_ID)
f.close()

def start_tunnel():
    print("start tunnel")
    os.system('sh /home/pi/EVO-SmartIoTVehicle-main/run_ngrok.sh')
    time.sleep(10)
    getVersion = subprocess.Popen("curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'", shell=True, stdout=subprocess.PIPE).stdout
    version = getVersion.read()
    URL_Tunnel = version.decode()

    if len(URL_Tunnel.split('\n')[0]) != 0:
        print("URL =", URL_Tunnel.split('\n')[0])
        host = URL_Tunnel.split('\n')[0].split(":")[0] + ":" + URL_Tunnel.split('\n')[0].split(":")[1]
        port = URL_Tunnel.split('\n')[0].split(":")[2]
        Output.update({
            "Device": {
                "device_code": Device_ID,
                "host": host,
                "port": port
            }
        })

        json_output = json.dumps(Output, indent=2)
    
    try:
        requests.patch(API_Host_URL + "/api/v1/devices/connection-update",
                        headers={"Content-Type": "application/json",
                                     "Ocp-Apim-Subscription-Key" : API_Key_Authen,
                                     },
                        data=json_output)
        print(json_output)

    except Exception:
        print("Not Sent")
        pass

def stop_tunnel():
    print("stop tunnel")
    os.system('pkill -f ngrok')
    time.sleep(3)
    Output.update({
        "Device": {
            "device_code": Device_ID,
            "host": "-",
            "port": "-"
        }
    })

    json_output = json.dumps(Output, indent=2)
    
    try:
        requests.patch(API_Host_URL + "/api/v1/devices/connection-update",
                        headers={"Content-Type": "application/json",
                                     "Ocp-Apim-Subscription-Key" : API_Key_Authen,
                                     },
                        data=json_output)
        print(json_output)

    except Exception:
        print("Not Sent")
        pass

async def process_received_messages(msg):
    global receiver
    print("Received:", str(msg))
    CMD_data = str(msg).split(":")
    if CMD_data[0] == Device_ID:
        print("case tunnel")
        if CMD_data[1] == "StartTunnel":
            start_tunnel()
        elif CMD_data[1] == "StopTunnel":
            stop_tunnel()
        # receiver.
    print("complete_message")
    await receiver.complete_message(msg)  # Move the message completion here

async def run():
    global receiver
    async with ServiceBusClient.from_connection_string(conn_str=NAMESPACE_CONNECTION_STR, logging_enable=True) as servicebus_client:
        async with servicebus_client:
            receiver = servicebus_client.get_subscription_receiver(topic_name=TOPIC_NAME, 
                                                                   subscription_name=SUBSCRIPTION_NAME, 
                                                                   max_wait_time=2)
            async with receiver:
                #print("receiving message")
                received_msgs = await receiver.receive_messages(max_wait_time=2, max_message_count=1)
                for msg in received_msgs:
                    await process_received_messages(msg)

def thread_callback():
    EndLoopTime = time.time() + Timeset
    while True:
        if time.time() > EndLoopTime:
            EndLoopTime = time.time() + Timeset
            dt = datetime.now(tz=ZoneInfo("Asia/Bangkok"))
            time_last = str(dt).split(' ')[0] + "T" + str(dt).split(' ')[1] + ""
            print(time_last)

            Output_A.update({
                "Device": {
                    "device_code": Device_ID,
                    "last_ping": time_last
                }
            })

            json_output = json.dumps(Output_A, indent=2)
            
            try:
                requests.patch(API_Host_URL + "/api/v1/devices/status-update",
                                headers={"Content-Type": "application/json",
                                     "Ocp-Apim-Subscription-Key" : API_Key_Authen,
                                     },
                                data=json_output)
                print(json_output)

            except Exception:
                print("Not Sent")
                pass

thr = threading.Thread(target=thread_callback)
thr.start()

EndLoopTime_1 = time.time() + Timeset_1

while True:
    asyncio.run(run())
    '''
    if time.time() > EndLoopTime_1:
        asyncio.run(run())
        EndLoopTime_1 = time.time() + Timeset_1
    '''
