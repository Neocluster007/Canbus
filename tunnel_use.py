#import paho.mqtt.client as mqtt
import threading
import time
from datetime import datetime
import os
import subprocess
import json
import requests

from datetime import datetime

from zoneinfo import ZoneInfo

Timeset = 60
Timeset_1 = 1
Output = {}
Output_A = {}

#f = open('data.json')
#data = json.load(f)

#print(data["device"]["plate_number"])

import asyncio
#import psutil

from azure.servicebus.aio import ServiceBusClient

NAMESPACE_CONNECTION_STR = "Endpoint=sb://maas-iot.servicebus.windows.net/;SharedAccessKeyName=TunnelListener;SharedAccessKey=07wteQMxzwotmSbYlIzGuFINLgELDiUV7+ASbC0L8pc=;EntityPath=tunnel-trigger"
SUBSCRIPTION_NAME = "S1"
TOPIC_NAME = "tunnel-trigger"

#API_Host_URL = "https://maas-apigateway.azure-api.net"
API_Host_URL = "https://maas-core-dev.azurewebsites.net"
#maas-core-dev
API_Key_Authen = "b3233d3da2fb4855b6d152571fa9e3b1"

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

Device_ID = getserial()
print("ID_Device = " + Device_ID)

async def run():
    # create a Service Bus client using the connection string
    async with ServiceBusClient.from_connection_string(
        conn_str=NAMESPACE_CONNECTION_STR,
        logging_enable=True) as servicebus_client:

        async with servicebus_client:
            # get the Subscription Receiver object for the subscription
            receiver = servicebus_client.get_subscription_receiver(topic_name=TOPIC_NAME, 
            subscription_name=SUBSCRIPTION_NAME, max_wait_time=5)
            async with receiver:
                received_msgs = await receiver.receive_messages(max_wait_time=5, max_message_count=20)
                for msg in received_msgs:
                    print("Received: " + str(msg))

                    CMD_data = str(msg).split(":")
                    #print("Received Device : " + CMD_data[0])

                    if CMD_data[0] == Device_ID:
                        print("case tunnel")
                        if CMD_data[1] == "StartTunnel":
                            print("start tunnel")
                            os.system('sh /home/pi/EVO-SmartIoTVehicle-main/run_ngrok.sh')

                            time.sleep(10)
                            getVersion =  subprocess.Popen("curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'", shell=True, stdout=subprocess.PIPE).stdout
                            version =  getVersion.read()
                            URL_Tunnel = version.decode()

                            if(len(URL_Tunnel.split('\n')[0]) != 0):
                                print("URL = " + URL_Tunnel.split('\n')[0])
                                host = URL_Tunnel.split('\n')[0].split(":")[0]+":"+URL_Tunnel.split('\n')[0].split(":")[1]
                                port = URL_Tunnel.split('\n')[0].split(":")[2]
                                Output.update({
                                    "Device": {
                                        "device_code": Device_ID,
                                        "host": host,
                                        "port": port
                                    }
                                })

                                JsonOutput = json.dumps(Output, indent=2)
                                
                                try:
                                    requests.patch(API_Host_URL+"/api/v1/devices/connection-update",
                                                    headers={
                                                        #"Ocp-Apim-Subscription-Key" : API_Key_Authen,
                                                        #"Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=tW%2BHuE59CxD9759f%2BEGR916eHv96eQo4kjo3sWFWZ1k%3D&se=1816746314&skn=VehicleCanManagePolicy",
                                                        "Content-Type": "application/json",
                                                    },
                                                    data=JsonOutput,)

                                    print(JsonOutput)

                                except Exception:
                                    print("Not Send")
                                    pass


                            #os.system('sh /home/ballbuen19/run_ngrok.sh')
                        elif CMD_data[1] == "StopTunnel":
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

                            JsonOutput = json.dumps(Output, indent=2)
                            
                            try:
                                requests.patch(API_Host_URL+"/api/v1/devices/connection-update",
                                                headers={
                                                    #"Ocp-Apim-Subscription-Key" : API_Key_Authen,
                                                    #"Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=tW%2BHuE59CxD9759f%2BEGR916eHv96eQo4kjo3sWFWZ1k%3D&se=1816746314&skn=VehicleCanManagePolicy",
                                                    "Content-Type": "application/json",
                                                },
                                                data=JsonOutput,)

                                print(JsonOutput)

                            except Exception:
                                print("Not Send")
                                pass
                        # complete the message so that the message is removed from the subscription
                        await receiver.complete_message(msg)

def thread_callback():
    EndLoopTime = time.time() + Timeset
    while True:
        if time.time() > EndLoopTime:
            #print("Hello inside Thread")
            EndLoopTime = time.time() + Timeset
            #client.publish("/MAAS/Project/685272/Detail/TimeOnline",time.time())

            #getVersion =  subprocess.Popen("curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'", shell=True, stdout=subprocess.PIPE).stdout
            #version =  getVersion.read()
            #URL_Tunnel = version.decode()

            #if(len(URL_Tunnel.split('\n')[0]) != 0):
            #print("URL = " + URL_Tunnel.split('\n')[0])
            #host = URL_Tunnel.split('\n')[0].split(":")[0]+":"+URL_Tunnel.split('\n')[0].split(":")[1]
            #port = URL_Tunnel.split('\n')[0].split(":")[2]

            dt = datetime.now(tz=ZoneInfo("Asia/Bangkok"))
            #ts = datetime.timestamp(dt)
            #current_time = dt.strftime("%H:%M:%S")

            time_last = str(dt).split(' ')[0] + "T"+str(dt).split(' ')[1] + ""
            print(time_last)

            Output_A.update({
                "Device": {
                    "device_code": Device_ID,
                    "last_ping": time_last
                }
            })

            JsonOutput = json.dumps(Output_A, indent=2)
            #https://maas-core-dev.azure-api.net/api/v1/devices/status-update
            try:
                requests.patch(API_Host_URL+"/api/v1/devices/status-update",
                                headers={

                                    #"Ocp-Apim-Subscription-Key" : API_Key_Authen,
                                    #"Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=tW%2BHuE59CxD9759f%2BEGR916eHv96eQo4kjo3sWFWZ1k%3D&se=1816746314&skn=VehicleCanManagePolicy",
                                    "Content-Type": "application/json",
                                },
                                data=JsonOutput,)

                print(JsonOutput)

            except Exception:
                print("Not Send")
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