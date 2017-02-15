#!/bin/bash
# -*- coding: utf-8 -*-

ip=${1}
gateway=${ip%.*}'.254'

echo -e "DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=static
IPADDR=${ip}
NETMASK=255.255.255.0
GATEWAY=${gateway}
DNS1=10.10.15.110
DNS2=10.10.15.111" > /etc/sysconfig/network-scripts/ifcfg-eth0

