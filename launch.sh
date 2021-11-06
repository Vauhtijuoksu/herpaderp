#!/bin/bash

source $1/venv/bin/activate

mkdir $1/html
python3 $1/WebServer.py 8000 $1/html/ &

python3 $1/monitor.py DB:6B:EA:95:D0:AE --format="{heartrate}" --output-file="$1/html/sensor1.txt" &
python3 $1/monitor.py E0:3E:9B:CF:AC:80 --format="{heartrate}" --output-file="$1/html/sensor2.txt" &
python3 $1/monitor.py EA:16:35:F9:58:B9 --format="{heartrate}" --output-file="$1/html/sensor3.txt" &
python3 $1/monitor.py E8:D8:C7:0B:3F:21 --format="{heartrate}" --output-file="$1/html/sensor4.txt" &
python3 $1/monitor.py CE:F5:71:BE:C3:C3 --format="{heartrate}" --output-file="$1/html/sensor5.txt" &
