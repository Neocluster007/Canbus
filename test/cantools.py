import os
import can
import cantools

CANDB_Name = "thaiev_g9_chenglong.dbc"
BitRate = "250000"
# BitRate = "500000"

os.system(str("sudo ip link set can0 type can bitrate " + BitRate))
os.system("sudo ifconfig can0 up")

can0 = can.interface.Bus(channel="can0", bustype="socketcan_ctypes")
CANDB = cantools.database.load_file(str("/candb/" + CANDB_Name))

print(CANDB.messages)

print("Test CAN receive")
print("Press CTRL-C to exit")

try:
    while True:

        msg = can0.recv(10.0)

        print(msg)

        if msg is not None:
            try:
                print(CANDB.decode_message(msg.arbitration_id, msg.data))
            except:
                print("DBC, no data")

        if msg is None:
            print("Timeout occurred, no message.")

except KeyboardInterrupt:
    os.system("sudo ifconfig can0 down")
