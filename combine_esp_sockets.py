#!/usr/bin/env python3
import socket
import threading
import datetime
import sys

ESP_PORT = 12345
ESP_ADDRESSES_DEFAULT = [
    "192.168.43.176",
    "192.168.43.132"
]

def print_log(log_str):
    print("[{}] SLCAN Traffic Log: {}".format(\
          datetime.datetime.now().strftime("%H:%M:%S"),
          log_str))

def get_addresses_from_args():
    esp_addresses = []
    if len(sys.argv) > 1:
        for address_idx in range(1, len(sys.argv)):
            esp_addresses.append(sys.argv[address_idx])
    else:
        esp_addresses = ESP_ADDRESSES_DEFAULT
    return esp_addresses


esp_addresses = get_addresses_from_args()
print_log("esp addresses are: " + str(esp_addresses))

esp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
esp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# It is a suitable way to get host IP because socket.gethostname() sometimes return wrong IP
temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
temp_sock.connect(("8.8.8.8", 80))
my_ip = temp_sock.getsockname()[0]
temp_sock.close()
print_log("my ip is: " + my_ip)

esp_sock.bind((my_ip, ESP_PORT))
esp_sock.settimeout(0.001)
esp_rx_counter = 0

UAVCAN_GUI_TOOL_PORT = 12346
uavcan_gui_tool_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
uavcan_gui_tool_sock.settimeout(0.001)
local_rx_counter = 0

def print_traffic():
    global crnt_counter
    global log_timer, esp_rx_counter, local_rx_counter
    log_timer = threading.Timer(10.0, print_traffic).start()

    if esp_rx_counter == 0:
        esp_log_str = "{}esp_rx={}{}".format("\033[93m", esp_rx_counter, '\033[0m')
    else:
        esp_log_str = "esp_rx={}".format(esp_rx_counter)

    if local_rx_counter == 0:
        local_rx_str = "{}local_rx={}{}".format("\033[93m", local_rx_counter, '\033[0m')
    else:
        local_rx_str = "local_rx={}".format(local_rx_counter)

    print_log(esp_log_str + ", " + local_rx_str)

    esp_rx_counter = 0
    local_rx_counter = 0

log_timer = threading.Timer(10.0, print_traffic).start()
try:
    while True:
        # ESP -> uavcan_gui_tool
        try:
            data, addr = esp_sock.recvfrom(1024)
            if len(data) != 0:
                uavcan_gui_tool_sock.sendto(data, ("localhost", UAVCAN_GUI_TOOL_PORT))
                esp_rx_counter += len(data)
        except socket.timeout as e:
            pass

        # uavcan_gui_tool -> ESPs
        try:
            data, addr = uavcan_gui_tool_sock.recvfrom(1024)
            if len(data) != 0:
                for esp_addr in esp_addresses:
                    esp_sock.sendto(data, (esp_addr, ESP_PORT))
                    local_rx_counter += len(data)
        except socket.timeout as e:
            pass
        except socket.gaierror as e:
            print(esp_addr, "socket.gaierror", e)

except (KeyboardInterrupt, SystemExit):
    esp_sock.close()
    uavcan_gui_tool_sock.close()
    log_timer.cancel()
    print('Interrupted by user, socket has been closed!')
