#!/bin/bash

function check_processes_related_to_required_port {
    sudo netstat -pna | grep $COMBINED_UDP_PORT
    result=$(sudo netstat -pna | grep $COMBINED_UDP_PORT)
    if [ -z "$result" ]
    then
        echo
    else
        echo
        echo "Process related to the particular port:"
        echo $result
        echo "You may want to kill this process using kill -9 process_id"
    fi
}
function concatenate_udp_and_serial_in_background {
    python3 combine_esp_sockets.py &
    sudo mkdir -p /dev/serial/by-id
    sudo socat PTY,link=$VIRTUAL_SERIAL_PORT_NAME,raw,echo=0,b1000000 UDP4-LISTEN:$COMBINED_UDP_PORT,reuseaddr &
    sleep 0.5
    sudo chmod 777 $VIRTUAL_SERIAL_PORT_NAME
}
function close_background_jobs() {
    echo ""
    echo "$0 ($$). Finishing..."
    pkill -P $$
    exit 0
}

cd "$(dirname "$0")"
source config.sh
echo "$0 ($$). Starting..."
trap 'close_background_jobs' SIGINT SIGTERM
check_processes_related_to_required_port
concatenate_udp_and_serial_in_background
./create_slcan_from_serial.sh $VIRTUAL_SERIAL_PORT_NAME
[ ! -z "$DISPLAY" ] && uavcan_gui_tool --dsdl $CUSTOM_DSDL_PATH &
while true;
do
    sleep 0.5
done
