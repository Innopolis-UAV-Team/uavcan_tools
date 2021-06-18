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
    DIR=$(dirname $(readlink -f $0))
    echo $DIR
    echo $DIR
    echo $DIR
    $DIR/combine_esp_sockets.py &
    sudo mkdir -p /dev/serial/by-id
    sudo socat -v -d -d PTY,link=$VIRTUAL_SERIAL_PORT_NAME,raw,echo=0,b1000000 UDP4-LISTEN:$COMBINED_UDP_PORT,reuseaddr &
    sleep 0.5
    sudo chmod 777 $VIRTUAL_SERIAL_PORT_NAME
}
function close_background_jobs() {
    echo ""
    echo "Finishing... Closing all background jobs..."
    jobs
    kill %1
    kill %2
    kill %3
    exit 0
}


source config.sh
echo "Starting... Pid of this process is" $$
trap 'close_background_jobs' SIGINT
check_processes_related_to_required_port
concatenate_udp_and_serial_in_background
uavcan_gui_tool --dsdl $CUSTOM_DSDL_PATH &
while true;
do
    sleep 0.5
done
