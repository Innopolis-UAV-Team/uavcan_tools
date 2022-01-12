#!/bin/bash
# Brief. This script sets several environment variables for following scripts:
# - create_serial_from_udp.sh
# - create_slcan_from_udp.sh


ORIGINAL_ESC_UDP_PORT=12345
COMBINED_UDP_PORT=12346
VIRTUAL_SERIAL_PORT_NAME=/dev/serial/by-id/uavcan_udp
CUSTOM_DSDL_PATH=/home/nex/catkin_landing_ws/src/inno_drone_station/uavcan_communicator/inno_msgs
