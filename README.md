# uavcan_tools

Typical way of working with UAVCAN devices is to connect device via SLCAN adapter to USB socket and to use `uavcan_gui_tool`.

These scripts allows following things:

1. Create virtual serial port and concatenate UDP port with it.

So you can use `uavcan_gui_tool` not only when your device has a wire connection, but also if your device send data through UDP using SLACAN protocol.

Here it should be noticed that it is possible to combine several UDP sockets into one, so you can communicate with several devices simultaniously. 

```bash
create_serial_from_udp.sh
```

2. Create SLCAN from serial port

It allows you to work with your devices from several processes. Typical serial port lets use only single process.

```bash
create_slcan_from_serial.sh
```

3. udp <-> SLCAN

Both features in a single script.

```bash
create_slcan_from_udp.sh
```

## Installation

```bash
sudo apt-get install -y can-utils socat net-tools
pip3 install netifaces
```
