#!/bin/bash

# Config
ESP_ADDRESSES=("192.168.43.71")     # Phone WiFi

ORIGINAL_ESC_UDP_PORT=12345
COMBINED_UDP_PORT=12346
VIRTUAL_SERIAL_PORT_NAME=/dev/serial/by-id/uavcan_udp
CUSTOM_DSDL_PATH=/home/nex/catkin_landing_ws/src/inno_drone_station/uavcan_communicator/inno_msgs
