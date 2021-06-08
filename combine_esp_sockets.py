#!/usr/bin/env python3
import socket

ESP_PORT = 12345
ESP_ADDRESSES = [
    "192.168.43.176",
    "192.168.43.132"
]
esp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
esp_sock.bind((socket.gethostname(), ESP_PORT))
esp_sock.settimeout(0.001)

UAVCAN_GUI_TOOL_PORT = 12346
uavcan_gui_tool_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
uavcan_gui_tool_sock.settimeout(0.001)

try:
    while True:

        # ESP -> uavcan_gui_tool
        try:
            data, addr = esp_sock.recvfrom(1024)
            if len(data) != 0:
                uavcan_gui_tool_sock.sendto(data, ("localhost", UAVCAN_GUI_TOOL_PORT))
                # print(addr, len(data), "->", "localhost,", UAVCAN_GUI_TOOL_PORT)
        except socket.timeout as e:
            pass

        # uavcan_gui_tool -> ESPs
        try:
            data, addr = uavcan_gui_tool_sock.recvfrom(1024)
            if len(data) != 0:
                for esp_addr in ESP_ADDRESSES:
                    esp_sock.sendto(data, (esp_addr, ESP_PORT))
                    # print('uavcan_gui_tool', len(data), "->", esp_addr)
        except socket.timeout as e:
            pass
        except socket.gaierror as e:
            print(esp_addr, "socket.gaierror", e)

except KeyboardInterrupt:
    esp_sock.close()
    uavcan_gui_tool_sock.close()
    print('Interrupted by user, socket has been closed!')
