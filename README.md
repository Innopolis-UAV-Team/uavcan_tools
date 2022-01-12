# UAVCAN Tools

This repository contains several scripts which might be usefull for an UAVCAN application.

The main scripts are shown in the table below:

| № | Script name                   | Info                                                 |
| - | ----------------------------- |:----------------------------------------------------:|
| 1 | `create_serial_from_udp.sh`   | Create a virtual serial port and concatenate it with UDP port. You may need to use this script if you want to run such application as `uavcan_gui_tool` with remote CAN-network connected to your PC via UDP. It may work with several devices simultaniously. |
| 2 | `create_slcan_from_serial.sh` | Create a virtual CAN-port based on SLCAN (serial port). Compared to a serial port, a virtual CAN-port allows you to use several process on the same port. It might be `uavcan_gui_tool` and your custom node. |
| 3 | `create_slcan_from_serial.sh` | Create a virtual CAN-port and concatenate it with UDP port. Just both features in a single script. |


## Installation

```bash
sudo apt-get install -y can-utils socat net-tools
pip3 install netifaces
```

## Used devices

These scripts were tested with following devices:
- [UAVCAN Sniffer and Programmer](https://github.com/InnopolisAero/inno_uavcan_node_binaries/blob/master/doc/programmer_sniffer/README.md)
- [UAVCAN WiFi Sniffer node](https://github.com/InnopolisAero/inno_uavcan_node_binaries/blob/master/doc/wifi_bridge/README.md)