#!/usr/bin/env python3
import socket
import threading
import datetime

ESP_PORT = 12345
ESP_ADDRESSES = [
    "192.168.43.176",
    "192.168.43.132"
]

esp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
esp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
esp_sock.bind((socket.gethostname(), ESP_PORT))
esp_sock.settimeout(0.001)
esp_rx_counter = 0

UAVCAN_GUI_TOOL_PORT = 12346
uavcan_gui_tool_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
uavcan_gui_tool_sock.settimeout(0.001)
local_rx_counter = 0

def print_log():
    global crnt_counter
    global log_timer, esp_rx_counter, local_rx_counter
    log_timer = threading.Timer(10.0, print_log).start()

    if esp_rx_counter == 0:
        esp_log_str = "{}esp_rx={}{}".format("\033[93m", esp_rx_counter, '\033[0m')
    else:
        esp_log_str = "esp_rx={}".format(esp_rx_counter)

    if local_rx_counter == 0:
        local_rx_str = "{}local_rx={}{}".format("\033[93m", local_rx_counter, '\033[0m')
    else:
        local_rx_str = "local_rx={}".format(local_rx_counter)

    print("[{}] SLCAN Traffic Log: {}, {}".format(\
          datetime.datetime.now().strftime("%H:%M:%S"),
          esp_log_str,
          local_rx_str))

    esp_rx_counter = 0
    local_rx_counter = 0

log_timer = threading.Timer(10.0, print_log).start()
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
                for esp_addr in ESP_ADDRESSES:
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
