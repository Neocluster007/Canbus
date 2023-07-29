import time
import datetime
import schedule
import os
import json
import requests

import can
import cantools

from vcgencmd import Vcgencmd
import psutil

# CANDB_Name = "thaiev_g9_chenglong.dbc"
CANDB_Name = "honda_civic_hatchback_ex_2017_can_generated.dbc"

BitRate = "250000"
# BitRate = "500000"

GPS_File = "/dev/serial0"

vcgm = Vcgencmd()

JsonOutput = {}


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


Device_ID = getserial()


def GPS():

    File = open(GPS_File, "r")
    Line = File.readline()

    GNRMC_Datetime = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    GNRMC_Status = "E"

    GPVTG_Speed = "0"
    GPVTG_Angle = "0"

    GPGGA_Altitude = "0"
    GPGGA_Geoidal_Seperation = "0"

    GPGSA_DOP = "0.00"
    GPGSA_HDOP = "0.00"
    GPGSA_VDOP = "0.00"

    GPTHS_Heading = 0
    GPTHS_Status = "E"

    GPGSV_Satellite = 0
    GPGSV_SNR = 0
    GPGSV_Elevation = 0
    GPGSV_Azimuth = 0

    GPRMC_Datetime = str(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    GPRMC_Latitude = "0"
    GPRMC_Longitude = "0"
    GPRMC_Status = "E"
    GPRMC_EWIndicator = "A"
    GPRMC_NSIndicator = "A"
    GPRMC_Speed = "0"
    GPRMC_Cog = "0"

    EndLoopTime = time.time() + 3

    while time.time() < EndLoopTime:

        if Line[0:6] == "$GPVTG":

            Data = Line.split(",")
            try:
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
            except:
                GPVTG_Speed = str(0)
                GPVTG_Angle = str(0)

        if Line[0:6] == "$GPGGA":

            Data = Line.split(",")
            try:
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
            except:
                GPGGA_Altitude = str(0)
                GPGGA_Geoidal_Seperation = str(0)

        if Line[0:6] == "$GPGSA":

            Data = Line.split(",")
            try:
                # Data : Dilution of precision
                if Data[15] == "":
                    GPGSA_DOP = str("0.00")
                else:
                    GPGSA_DOP = str(Data[15])

                # Data : Horizontal dilution of precision
                if Data[16] == "":
                    GPGSA_HDOP = str("0.00")
                else:
                    GPGSA_HDOP = str(Data[16])

                # Data : Vertical dilution of precision
                if Data[17] == "":
                    GPGSA_VDOP = str("0.00")
                else:
                    GPGSA_VDOP = str(Data[17][0:4])
            except:
                GPGSA_DOP = str("0.00")
                GPGSA_HDOP = str("0.00")
                GPGSA_VDOP = str("0.00")

        if Line[0:6] == "$GPTHS":

            Data = Line.split(",")

            try:
                # Data : Heading
                if Data[1] == "":
                    GPTHS_Heading = str(0)
                else:
                    GPTHS_Heading = str(float(Data[1]))

                # # Data : Status
                # if Data[2] == "":
                #     GPTHS_Status = str(0)
                # else:
                #     GPTHS_Status = str(float(Data[2]))
            except:
                GPTHS_Heading = str(0)
                # GPTHS_Status = str(0)

        if Line[0:6] == "$GPGSV":

            Data = Line.split(",")

            try:
                # Data : Satellite in view
                if Data[3] == "":
                    GPGSV_Satellite = str(0)
                else:
                    GPGSV_Satellite = str(Data[3])

                # Data : Signal to Noise ratio
                if Data[7] == "":
                    GPGSV_SNR = str(0)
                else:
                    GPGSV_SNR = str(Data[7])

                # Data : Elevation
                if Data[5] == "":
                    GPGSV_Elevation = str(0)
                else:
                    GPGSV_Elevation = str(Data[5])

                # Data : Azimuth
                if Data[6] == "":
                    GPGSV_Azimuth = str(0)
                else:
                    GPGSV_Azimuth = str(Data[6])
            except:
                GPGSV_Satellite = str(0)
                GPGSV_SNR = str(0)
                GPGSV_Elevation = str(0)
                GPGSV_Azimuth = str(0)

        if Line[0:6] == "$GPRMC":

            Data = Line.split(",")

            try:
                # Data : status
                if Data[2] == "":
                    GPRMC_Status = str("E")
                else:
                    GPRMC_Status = str(Data[2])

                # Data : latitude
                if Data[3] == "":
                    GPRMC_Latitude = str("0.000")
                else:
                    GPRMC_Latitude = str(convert_to_degrees(float(Data[3])))

                # Data : NS Indicator
                if Data[4] == "":
                    GPRMC_NSIndicator = str("")
                else:
                    GPRMC_NSIndicator = str(Data[4])

                # Data : longitude
                if Data[5] == "":
                    GPRMC_Longitude = str("0.000")
                else:
                    GPRMC_Longitude = str(convert_to_degrees(float(Data[5])))

                # Data : EW Indicator
                if Data[6] == "":
                    GPRMC_EWIndicator = str("")
                else:
                    GPRMC_EWIndicator = str(Data[6])

                # Data : speed
                if Data[7] == "":
                    GPRMC_Speed = str(0)
                else:
                    GPRMC_Speed = str(float(Data[7]))

                # Data : Course over ground
                if Data[8] == "":
                    GPRMC_Cog = str(0)
                else:
                    GPRMC_Cog = str(float(Data[8]))

                # Data : datetime
                if Data[1] == "" or Data[9] == "":
                    GPRMC_Datetime = str(
                        datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
                    )
                else:
                    GPRMC_Datetime = str(
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
            except:
                GPRMC_Status = str("E")
                GPRMC_Latitude = str("0.000")
                GPRMC_NSIndicator = str("")
                GPRMC_Longitude = str("0.000")
                GPRMC_EWIndicator = str("")
                GPRMC_Speed = str(0)
                GPRMC_Cog = str(0)
                GPRMC_Datetime = str(
                    datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
                )

        Line = File.readline()

    Output = {
        "datetime": str(
            datetime.datetime.strptime(GPRMC_Datetime, "%y-%m-%d %H:%M:%S")
        ),
        "status": GPRMC_Status,
        "latitude": float(GPRMC_Latitude),
        "latitude_indicator": GPRMC_NSIndicator,
        "longitude": float(GPRMC_Longitude),
        "longitude_indicator": GPRMC_EWIndicator,
        "speed": float(GPRMC_Speed),
        "cog": float(GPRMC_Cog),
        "angle": float(GPVTG_Angle),
        "altitude": float(GPGGA_Altitude),
        "heading": float(GPTHS_Heading),
        "elevation": float(GPGSV_Elevation),
        "azimuth": float(GPGSV_Azimuth),
        "geoid": float(GPGGA_Geoidal_Seperation),
        "dop": float(GPGSA_DOP),
        "hdop": float(GPGSA_HDOP),
        "vdop": float(GPGSA_VDOP),
        # "heading_status": float(GPTHS_Status),
        "gp_satellite": float(GPGSV_Satellite),
        # "gp_snr": float(GPGSV_SNR),
        # "gl_satellite": float(GLONASS_Satellite),
        # "gl_snr": float(GLONASS_SNR),
        "deviceid": Device_ID,
        "source": "MAAS",
        "msg_type": "vehicle_gps",
    }

    JsonOutput = json.dumps(Output, indent=2)

    File.close()

    try:
        requests.post(
            "https://maas-gps.servicebus.windows.net/gps/messages?timeout=60&api-version=2014-01",
            headers={
                "Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=EyX0bSA9opKYTEEM0It%2FQhrKbLYZHUiFDA6QOEcGge8%3D&se=1656084274&skn=SendSharedAccessKey",
                "Content-Type": "application/atom+xml;type=entry;charset=utf-8.",
            },
            data=JsonOutput,
        )

        # Test
        print(JsonOutput)
        return

    except:
        print("GPS Error")
        return


def CAN():

    Output = {
        "MAAS_INFORMATION": {
            "DEVICE_ID": Device_ID,
            "DEVICE_CPU": psutil.cpu_percent(),
            "DEVICE_RAM": psutil.virtual_memory().percent,
            "DEVICE_TEMP": vcgm.measure_temp(),
        },
        "msg_type": "vehicle_can",
    }

    os.system(str("sudo ip link set can0 type can bitrate " + BitRate))
    os.system("sudo ifconfig can0 up")
    os.system("candump can0 > can_raw.log")

    CANDB = cantools.database.load_file(str("candb/" + CANDB_Name))
    CAN = can.interface.Bus("can0", bustype="socketcan", duration=1)

    if CAN.recv(1.0) is not None:

        CAN.recv(1.0)

        Count = 0
        EndLoopTime = time.time() + 5

        for msg in CAN:

            try:
                Output.update(CANDB.decode_message(msg.arbitration_id, msg.data))
            except:
                ()

            if Count >= 200 or time.time() < EndLoopTime:
                break

            Count = Count + 1

    JsonOutput = json.dumps(Output, indent=2)

    CAN.shutdown()

    try:
        requests.post(
            "https://maas-gps.servicebus.windows.net/vehicle-can/messages?timeout=60&api-version=2014-01",
            headers={
                "Authorization": "SharedAccessSignature sr=http%3A%2F%2Fmaas-gps.servicebus.windows.net%2F&sig=PhFHxqaAW6GSb9svqGjqMrt%2F%2FygnKB6n%2BnvE%2FQ%2BaHdg%3D&se=1658145566&skn=VehicleCanManagePolicy",
                "Content-Type": "application/atom+xml;type=entry;charset=utf-8.",
            },
            data=JsonOutput,
        )
        # Test
        print(JsonOutput)
        return

    except:
        print("CAN Error")
        return


schedule.every(5).seconds.do(GPS)
schedule.every(60).seconds.do(CAN)

while True:
    schedule.run_pending()
    time.sleep(1)
