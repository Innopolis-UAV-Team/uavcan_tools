#!/bin/bash
# Brief. This script sets several environment variables for following scripts:
# - create_serial_from_udp.sh
# - create_slcan_from_udp.sh
# Input environment variables:
# - UAVCAN_ENVIRONMENT: ["PROD", "MOBILE", "DRONE"]. Empty or otherwise means "PROD".

if [ "$UAVCAN_ENVIRONMENT" = "MOBILE" ]; then
    MOBILE_WIFI_IP_FIRST="192.168.43.176"
    MOBILE_WIFI_IP_SECOND="192.168.43.132"
    ESP_ADDRESSES=($MOBILE_WIFI_IP_FIRST $MOBILE_WIFI_IP_SECOND)
elif [ "$UAVCAN_ENVIRONMENT" = "DRONE" ]; then
    DRONE_WIFI_IP_LANDING_STATION_ESP="192.168.3.140"
    ESP_ADDRESSES=($DRONE_WIFI_IP_LANDING_STATION_ESP)
else
    PROD_WIFI_IP_OF_REAL_JETSON="192.168.10.10"
    PROD_WIFI_IP_OF_DRONE_ESP="192.168.10.20"
    PROD_WIFI_IP_OF_LANDING_STATION_ESP="192.168.10.21"
    ESP_ADDRESSES=($PROD_WIFI_IP_OF_REAL_JETSON $PROD_WIFI_IP_OF_DRONE_ESP $PROD_WIFI_IP_OF_LANDING_STATION_ESP)
fi

ORIGINAL_ESC_UDP_PORT=12345
COMBINED_UDP_PORT=12346
VIRTUAL_SERIAL_PORT_NAME=/dev/serial/by-id/uavcan_udp
CUSTOM_DSDL_PATH=/home/nex/catkin_landing_ws/src/inno_drone_station/uavcan_communicator/inno_msgs
