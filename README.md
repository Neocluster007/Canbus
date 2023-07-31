# EVO-SmartIoTVehicle

sudo apt-get install realvnc-vnc-server
sudo raspi-config - Enable VNC - Enable SPI - Enable Serial
git clone https://github.com/rattanur/EVO-SmartIoTVehicle.git
sudo apt-get install gpsd gpsd-clients
man gpsd
cat /dev/serial0

# Reference

> Intial PI

- https://spin.atomicobject.com/2019/06/09/raspberry-pi-laptop-display/
- https://raspberrypi.stackexchange.com/questions/59599/no-vnc-option-on-raspbian-menu
- https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

> GPS Module

- https://maker.pro/raspberry-pi/tutorial/how-to-use-a-gps-receiver-with-raspberry-pi-4

> CAN Module

- https://stackoverflow.com/questions/58306438/how-to-decode-message-from-a-canbus-iptronik
- https://github.com/commaai/opendbc
- http://www.ett.co.th/productPi/ET-CAN_HAT/ET-CAN-HAT_Manual_Th.pdf
- http://www.ett.co.th/productPi/ET-CAN_HAT/ET-CAN_HAT.zip

> Linux set stratup

- https://www.instructables.com/Raspberry-Pi-Launch-Python-script-on-startup/

> Remote.it

- sudo wget https://downloads.remote.it/remoteit/v4.13.6/remoteit-4.13.6.arm64.deb
- sudo apt install https://downloads.remote.it/remoteit/v4.13.6/remoteit-4.13.6.arm64.deb
- sudo apt remove remoteit

> Node-Red

- https://nodered.org/docs/getting-started/raspberrypi


> Remoteit new Cleim

- Delete the file /etc/remoteit/config.json
- Reboot the device
- Get the new claim code by running:
- grep -i claim /etc/remoteit/config.json

> Git Command

- git add .
- git commit -m “change function b”
- git push

