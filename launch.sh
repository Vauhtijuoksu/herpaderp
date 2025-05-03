#!/bin/bash

source $1/venv/bin/activate

mkdir $1/data
python3 $1/apisender.py --config-file $1/config.ini --verbosity=$2 --input-file $1/data/sensor1.txt $1/data/sensor2.txt $1/data/sensor3.txt $1/data/sensor4.txt $1/data/sensor5.txt &

python3 $1/monitor.py CD:44:02:18:7E:60 --format="{heartrate}" --data-dir="$1/data/" --number=1 --verbosity=$2 &
python3 $1/monitor.py EC:34:2B:4B:82:31 --format="{heartrate}" --data-dir="$1/data/" --number=2 --verbosity=$2 &
python3 $1/monitor.py EA:16:35:F9:58:B9 --format="{heartrate}" --data-dir="$1/data/" --number=3 --verbosity=$2 &
python3 $1/monitor.py E8:D8:C7:0B:3F:21 --format="{heartrate}" --data-dir="$1/data/" --number=4 --verbosity=$2 &
python3 $1/monitor.py CE:F5:71:BE:C3:C3 --format="{heartrate}" --data-dir="$1/data/" --number=5 --verbosity=$2 &
