#!/bin/bash

#phone ip 
HOST=192.168.43.1
PORT=50000

#stop gpsd
echo "Stop processing..."
killall gpsd
sudo systemctl stop gpsd
sudo systemctl stop gpsd.socket

#start new process
echo "Start geting gps coordinates from $HOST:$PORT"
gpsd -N  "tcp://$HOST:$PORT"

