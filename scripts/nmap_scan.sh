#!/bin/bash
# Scan network
my_ip_address=$(hostname -I | cut -f 1 -d " ")
echo "My address is:" $my_ip_address
echo "nmap -sn $my_ip_address/24..."
nmap -sn $my_ip_address/24
