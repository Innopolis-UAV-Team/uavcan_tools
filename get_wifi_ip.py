#!/usr/bin/env python3
# This script defines wifi interface (wlan0, wlp0s20f3, etc) and return wifi IP address

try:
    from netifaces import interfaces, ifaddresses, AF_INET
except ImportError:
    print("The python package netifaces is required.")
    print("You can install it from the PyPI with ``pip install netifaces''.")
    exit(1)

def get_wifi_ip():
    wifi_ip = "127.0.0.1"
    wifi_iface_name = "unknown"
    ifaces = interfaces()

    for iface in ifaces:
        try:
            if iface[0:2] == "wl" or iface[0:3] == "eth":
                wifi_iface_name = iface
                wifi_ip = ifaddresses(wifi_iface_name)[AF_INET][0]['addr']
                break
        except:
            pass

    return wifi_ip

if __name__=="__main__":
    print(get_wifi_ip())
