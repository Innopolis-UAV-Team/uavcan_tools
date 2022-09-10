#!/bin/bash
# Check udp traffic on the desired port.

PORT=12345

sudo tcpdump -i wlp0s20f3 -n udp port $PORT
