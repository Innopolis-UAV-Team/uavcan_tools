#!/usr/bin/env python3
import socket
import threading
import datetime
import sys


ESP_PORT = 12345
UAVCAN_GUI_TOOL_PORT = 12346
ESP_ADDRESSES_DEFAULT = [
    "192.168.43.176",
    "192.168.43.132"
]

LOG_PERIOD_SEC = 1.0
TIME_BEFORE_START_FIRST_LOG = 2.0


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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

def get_host_ip():
    # It is a suitable way to get host IP because socket.gethostname() sometimes return wrong IP
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))
    my_ip = temp_sock.getsockname()[0]
    temp_sock.close()
    return my_ip


class Concatenator:
    def __init__(self):
        self.esp_addresses = get_addresses_from_args()
        print_log("esp addresses are: " + str(self.esp_addresses))

        self.esp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.esp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.my_ip = get_host_ip()
        print_log("my ip is: " + self.my_ip)

        self.esp_sock.bind((self.my_ip, ESP_PORT))
        self.esp_sock.settimeout(0.001)
        self.rx_bytes_counter_from_esp = 0
        self.rx_counter_from_esp = 0
        self.rx_timeout_counter_from_esp = 0
        self.rx_error_counter_from_esp = 0
        self.tx_timeout_counter_to_gui = 0
        self.tx_error_counter_to_gui = 0

        self.uavcan_gui_tool_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.uavcan_gui_tool_sock.settimeout(0.001)
        self.rx_bytes_counter_from_gui = 0
        self.rx_counter_from_gui = 0
        self.rx_timeout_counter_from_gui = 0
        self.rx_error_counter_from_gui = 0
        self.tx_error_counter_to_esp = 0
        self.tx_timeout_counter_to_esp = 0

        self.log_timer = threading.Timer(TIME_BEFORE_START_FIRST_LOG, self._print_traffic).start()

    def __del__(self):
        self.esp_sock.close()
        self.uavcan_gui_tool_sock.close()
        self.log_timer.cancel()
        print('Interrupted by user, socket has been closed!')

    def spin(self):
        self._spin_esp_to_gui_tool()
        self._spin_gui_tool_to_esp()

    def _spin_esp_to_gui_tool(self):
        try:
            data, addr = self.esp_sock.recvfrom(1024)
        except socket.timeout as e:
            self.rx_timeout_counter_from_esp += 1
            return
        except socket.gaierror as e:
            self.rx_error_counter_from_esp += 1
            return
        if len(data) != 0:
            try:
                self.uavcan_gui_tool_sock.sendto(data, ("localhost", UAVCAN_GUI_TOOL_PORT))
            except socket.timeout as e:
                pass
            except socket.gaierror as e:
                pass
            self.rx_bytes_counter_from_esp += len(data)
            self.rx_counter_from_esp += 1

    def _spin_gui_tool_to_esp(self):
        try:
            data, addr = self.uavcan_gui_tool_sock.recvfrom(1024)
        except socket.timeout as e:
            self.rx_timeout_counter_from_gui += 1
            return
        except socket.gaierror as e:
            self.rx_error_counter_from_gui += 1
            return
        if len(data) != 0:
            for esp_addr in self.esp_addresses:
                try:
                    self.esp_sock.sendto(data, (esp_addr, ESP_PORT))
                except socket.timeout as e:
                    self.tx_timeout_counter_to_esp += 1
                except socket.gaierror as e:
                    self.tx_error_counter_to_esp += 1
                self.rx_bytes_counter_from_gui += len(data)
                self.rx_counter_from_gui += 1

    def _print_traffic(self):
        self.log_timer = threading.Timer(LOG_PERIOD_SEC, self._print_traffic).start()

        if self.rx_bytes_counter_from_esp == 0:
            esp_log_str = "{}esp_sock rx={}{}".format(Colors.WARNING,
                                                      self.rx_bytes_counter_from_esp,
                                                      Colors.ENDC)
        else:
            esp_log_str = "esp_sock rx={}/{}".format(self.rx_bytes_counter_from_esp,
                                                     self.rx_counter_from_esp)
            if self.rx_error_counter_from_esp is not 0:
                esp_log_str += "/{}err={}{}".format(Colors.FAIL,
                                                    self.rx_error_counter_from_esp,
                                                    Colors.ENDC)

        if self.rx_bytes_counter_from_gui == 0:
            local_rx_str = "{}gui_sock rx={}{}".format(Colors.WARNING,
                                                    self.rx_bytes_counter_from_gui,
                                                    Colors.ENDC)
        else:
            local_rx_str = "gui_sock rx={}/{}".format(self.rx_bytes_counter_from_gui,
                                                      self.rx_counter_from_gui)
            if self.rx_error_counter_from_gui is not 0:
                local_rx_str += "/{}err={}{}".format(Colors.FAIL,
                                                     self.rx_error_counter_from_gui,
                                                     Colors.ENDC)

        print_log(esp_log_str + ", " + local_rx_str)

        self.rx_bytes_counter_from_esp = 0
        self.rx_counter_from_esp = 0
        self.rx_timeout_counter_from_esp = 0
        self.rx_error_counter_from_esp = 0

        self.rx_bytes_counter_from_gui = 0
        self.rx_counter_from_gui = 0
        self.rx_timeout_counter_from_gui = 0
        self.rx_error_counter_from_gui = 0
        self.tx_error_counter_to_esp = 0


if __name__=="__main__":
    concatenator = Concatenator()
    try:
        while True:
            concatenator.spin()
    except (KeyboardInterrupt, SystemExit):
        del concatenator