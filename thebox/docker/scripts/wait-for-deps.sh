#!/bin/bash

IFS=';' read -ra ADDR <<< "$1"
for i in "${ADDR[@]}"; do
    echo "Waiting for dependency $i ..."
    wait-for-it $i -t 300
done
