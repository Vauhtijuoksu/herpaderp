#!/bin/bash

source venv/bin/activate

python3 WebServer.py &

python3 monitor.py DB:6B:EA:95:D0:AE --format="{heartrate}" --output-file="sensor1.txt" &
python3 monitor.py E0:3E:9B:CF:AC:80 --format="{heartrate}" --output-file="sensor2.txt" &
python3 monitor.py EA:16:35:F9:58:B9 --format="{heartrate}" --output-file="sensor3.txt" &
python3 monitor.py E8:D8:C7:0B:3F:21 --format="{heartrate}" --output-file="sensor4.txt" &
python3 monitor.py CE:F5:71:BE:C3:C3 --format="{heartrate}" --output-file="sensor5.txt" &
