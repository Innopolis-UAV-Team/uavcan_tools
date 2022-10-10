#!/usr/bin/env python3
import socket
import threading
import time
from get_wifi_ip import get_wifi_ip
from slcan_parser import parse_data
from color_logging import Colors, log_info, log_warn, log_err

ESP_PORT = 12345
UAVCAN_GUI_TOOL_PORT = 12346

LOG_PERIOD_SEC = 10.0
TIME_BEFORE_START_FIRST_LOG = 2.0

class NodeInfo:
    def __init__(self, time, buffer="kek") -> None:
        self.time = time
        self.buffer = buffer

class Concatenator:
    def __init__(self):
        self.nodes_online = dict()

        self.my_ip = get_wifi_ip()
        ip_info_str = "Host IP is {}".format(self.my_ip)
        if self.my_ip == "127.0.0.1":
            log_err(ip_info_str)
        else:
            log_info(ip_info_str)

        self.esp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.esp_sock.bind(("", 12345))
        self.esp_sock.settimeout(0.001)
        self.esp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        log_err('Interrupted by user, socket has been closed!')

    def spin(self):
        self._spin_esp_to_gui_tool()
        self._spin_gui_tool_to_esp()

    def _spin_esp_to_gui_tool(self):
        # recv from the network:
        data = None
        try:
            data, addr = self.esp_sock.recvfrom(1024)
            self._update_esp_addresses_timestampts(addr)
            data = self._parse_received_data(data, addr)
        except socket.timeout as e:
            self.rx_timeout_counter_from_esp += 1
        except socket.gaierror as e:
            print(e)
            self.rx_error_counter_from_esp += 1
            return
        self._remove_unused_esp_addresses()

        # send to the local application:
        if data is not None and len(data) != 0:
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
            for esp_addr in self.nodes_online:
                try:
                    self.esp_sock.sendto(data, (esp_addr, ESP_PORT))
                except socket.timeout as e:
                    self.tx_timeout_counter_to_esp += 1
                except socket.gaierror as e:
                    self.tx_error_counter_to_esp += 1
                self.rx_bytes_counter_from_gui += len(data)
                self.rx_counter_from_gui += 1

    def _parse_received_data(self, new_coming_bytes, addr):
        """
        Based on previously stored and new coming bytes, return parsed frame and skip broken.
        """
        try:
            new_coming_bytes = new_coming_bytes.decode("utf-8")
        except UnicodeDecodeError:
            log_err("UnicodeDecodeError")
            return []
        storage_buffer = self.nodes_online[addr[0]].buffer
        parsed_frames, storage_buffer = parse_data(storage_buffer, new_coming_bytes)
        # print("\ncase:", len(new_coming_bytes), addr[0])
        # print("- stored: {} {}".format(len(self.nodes_online[addr[0]].buffer), self.nodes_online[addr[0]].buffer.encode()))
        # print("- coming: {} {}".format(len(new_coming_bytes), new_coming_bytes.encode()))
        # print("- parsed: {} {}".format(len(parsed_frames), parsed_frames.encode()))
        # print("- stored: {} {}".format(len(storage_buffer), storage_buffer.encode()))
        self.nodes_online[addr[0]].buffer = storage_buffer

        return parsed_frames.encode()

    def _update_esp_addresses_timestampts(self, addr):
        if addr[0] not in self.nodes_online.keys():
            log_warn("New node ({}) has been added to the existed set: {}".format(addr[0], self.nodes_online.keys()))
        if addr[0] in self.nodes_online:
            self.nodes_online[addr[0]].time = time.time()
        else:
            self.nodes_online[addr[0]] = NodeInfo(time=time.time())

    def _remove_unused_esp_addresses(self):
        MAX_DELAY_SEC = 5.0
        crnt_time = time.time()
        for addr in self.nodes_online:
            last_recv_time_sec = self.nodes_online[addr].time
            if last_recv_time_sec + MAX_DELAY_SEC < crnt_time:
                log_warn("{} has been inactive for last {} seconds.".format(addr, MAX_DELAY_SEC))
                del self.nodes_online[addr]
                log_warn("New set of nodes is {}.".format(self.nodes_online))
                break

    def _print_traffic(self):
        self.log_timer = threading.Timer(LOG_PERIOD_SEC, self._print_traffic).start()

        if self.rx_bytes_counter_from_esp == 0:
            esp_log_str = f"{Colors.WARNING}esp_sock rx={self.rx_bytes_counter_from_esp}{Colors.ENDC}"
        else:
            esp_log_str = f"esp_sock rx={self.rx_bytes_counter_from_esp}/{self.rx_counter_from_esp}"
            if self.rx_error_counter_from_esp != 0:
                esp_log_str += f"/{Colors.FAIL}err={self.rx_error_counter_from_esp}{Colors.ENDC}"

        if self.rx_bytes_counter_from_gui == 0:
            local_rx_str = "{}gui_sock rx={}{}".format(Colors.WARNING,
                                                       self.rx_bytes_counter_from_gui,
                                                       Colors.ENDC)
        else:
            local_rx_str = "gui_sock rx={}/{}".format(self.rx_bytes_counter_from_gui,
                                                      self.rx_counter_from_gui)
            if self.rx_error_counter_from_gui != 0:
                local_rx_str += "/{}err={}{}".format(Colors.FAIL,
                                                     self.rx_error_counter_from_gui,
                                                     Colors.ENDC)

        log_info(esp_log_str + ", " + local_rx_str)

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
