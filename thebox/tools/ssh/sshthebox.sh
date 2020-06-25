#!/bin/bash

# Simple script to ssh from command line to TheBox (test environment)

declare -A thebox_fwd_ports=( \
    ["b1"]="1122" \
    ["b2"]="2222" \
    ["b3"]="3322" \
)

hostname="theboxrouter.guest.corp.microsoft.com"
user="pi"

declare -A thebox_local_ports=( \
    ["router"]="20000" \
    ["b1j1"]="21122" \
    ["b1p2"]="21222" \
    ["b1p3"]="21322" \
    ["b1p4"]="21422" \
    ["b2j1"]="22122" \
    ["b2p2"]="22222" \
    ["b2p3"]="22322" \
    ["b2p4"]="22422" \
)
declare -A thebox_remote_ports=( \
    ["router"]="192.168.1.1:80" \
    ["b1j1"]="192.168.1.111:22" \
    ["b1p2"]="192.168.1.112:22" \
    ["b1p3"]="192.168.1.113:22" \
    ["b1p4"]="192.168.1.114:22" \
    ["b2j1"]="192.168.1.121:22" \
    ["b2p2"]="192.168.1.122:22" \
    ["b2p3"]="192.168.1.123:22" \
    ["b2p4"]="192.168.1.124:22" \
)
declare -A thebox_remote_users=( \
    ["router"]="theboxrouter" \
    ["b1j1"]="mhhddev" \
    ["b1p2"]="pi" \
    ["b1p3"]="pi" \
    ["b1p4"]="pi" \
    ["b2j1"]="mhhddev" \
    ["b2p2"]="pi" \
    ["b2p3"]="pi" \
    ["b2p4"]="pi" \
)

# check type of connection
if [ "$1" = "" ]; then
    echo "Please specify the box to connect to:"
    echo "  e.g. b1, b2 or b3"
    echo "Once initial connection is made, you need to run this"
    echo "script againt to specify which server to connect to:"
    echo "  e.g. b1j1, j2p3"
    exit 1
fi

if [ "$1" = "b1" ] || [ "$1" = "b2" ] || [ "$1" = "b3" ]; then
    fwdparam=""
    for i in "${!thebox_local_ports[@]}"; do
        echo "key  : $i"
        #echo "value: ${array[$i]}"
        fwdparam="${fwdparam} -L ${thebox_local_ports[$i]}:${thebox_remote_ports[$i]}"
    done

    # Local port 20000 will be mapped to router UI
    echo "SSHing to ${hostname}:${thebox_fwd_ports[$1]}, and forwarding:"
    echo "${fwdparam}"
    ssh ${fwdparam} ${user}@${hostname} -p ${thebox_fwd_ports[$1]} -q
else
    echo "SSHing to forwarded port ${thebox_local_ports[$1]}"
    ssh ${thebox_remote_users[$1]}@localhost -p ${thebox_local_ports[$1]}
fi
