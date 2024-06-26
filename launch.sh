#!/bin/bash

source $1/venv/bin/activate

mkdir $1/html
python3 $1/apisender.py --config-file $1/config.ini --input-file $1/html/sensor1.txt $1/html/sensor2.txt $1/html/sensor3.txt $1/html/sensor4.txt $1/html/sensor5.txt &

python3 $1/monitor.py CD:44:02:18:7E:60 --format="{heartrate}" --output-file="$1/html/sensor1.txt" &
python3 $1/monitor.py E0:3E:9B:CF:AC:80 --format="{heartrate}" --output-file="$1/html/sensor2.txt" &
python3 $1/monitor.py EA:16:35:F9:58:B9 --format="{heartrate}" --output-file="$1/html/sensor3.txt" &
python3 $1/monitor.py E8:D8:C7:0B:3F:21 --format="{heartrate}" --output-file="$1/html/sensor4.txt" &
python3 $1/monitor.py CE:F5:71:BE:C3:C3 --format="{heartrate}" --output-file="$1/html/sensor5.txt" &
