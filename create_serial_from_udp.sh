#!/bin/bash

function check_processes_related_to_required_port {
    echo "Process related to the particular port:"

    sudo netstat -pna | grep $COMBINED_UDP_PORT
    sudo netstat -pna | grep $ORIGINAL_ESC_UDP_PORT

    result=$(sudo netstat -pna | grep $ORIGINAL_ESC_UDP_PORT)
    result="${result}$(sudo netstat -pna | grep $ORIGINAL_ESC_UDP_PORT)"
    if [ -z "$result" ]; then
        echo "[OK] There is no any process related to required ports."
    else
        echo "[WARN] You may want to kill this process using kill -TERM process_id."
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
    echo "$0 ($$). Finishing... Closing all background jobs..."
    pkill -e -P $$
    exit 0
}


cd "$(dirname "$0")"
source config.sh
echo "$0 ($$). Starting..."
trap 'close_background_jobs' SIGINT SIGTERM
check_processes_related_to_required_port
concatenate_udp_and_serial_in_background
while true;
do
    sleep 0.5
done
