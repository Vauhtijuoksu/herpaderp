#!/bin/env python3

import asyncio
import argparse
import random

import bleak
import sys
import time
import os.path

DEVICE_MAC = "CE:F5:71:BE:C3:C3"
OUTPUT_FMT = "{heartrate}, {ppi}ms"
OUTPUT_FILE = ""

def find_heartrate_service(services):
    for service in services:
        if (service.description == "Heart Rate"):
            return service

    return None

def find_heartrate_measurement_characteristic(service):
    for char in service.characteristics:
        if (char.description == "Heart Rate Measurement"):
            return char

    return None

def read_callback(source, data):
    if (data[0] == 0x10):
        heartrate = int(data[1])
        peak_to_peak_ms = int.from_bytes(data[2:3], byteorder='little') 

        with open(OUTPUT_FILE, 'w') as ff:
            ff.write(OUTPUT_FMT.format(heartrate=heartrate, ppi=peak_to_peak_ms))
        if args.verbosity > 2:
            print(f'{OUTPUT_FILE} {heartrate}')

    else:
        if args.verbosity > 0:
            print (f'{args.number} received unexpected data', file=sys.stderr)

async def run(client):
    if args.verbosity > 0:
        print ("device", DEVICE_MAC, "connected", file=sys.stderr)

    services = await client.get_services()
    heartrate_service = find_heartrate_service(services)
    heartrate_measurement = find_heartrate_measurement_characteristic(heartrate_service)

    if args.verbosity > 1:
        print ("asking for notifications from", heartrate_measurement, file=sys.stderr)
    
    await client.start_notify(heartrate_measurement, read_callback)

    while True:
        if not await client.is_connected():
            break
        await asyncio.sleep(1.0)

async def main():
    if args.verbosity > 0:
        print("Connecting to", DEVICE_MAC, file=sys.stderr)
    async with bleak.BleakClient(DEVICE_MAC) as client:
        tasks = [ asyncio.ensure_future(run(client)) ]
        await asyncio.gather(*tasks)

def join_que():
    try:
        with bleak.BleakClient(DEVICE_MAC) as client:
            client.disconnect()
    except Exception as ee:
        if args.verbosity > 2:
            print(ee, file=sys.stderr)

    if not os.path.isfile(QUEUE_FILE):
        with open(QUEUE_FILE, 'w') as f:
            f.write("")



def check_que():
    with open(QUEUE_FILE, 'r') as f:
        que = f.read()
    if args.verbosity > 1:
        print(f'{que} {args.number}')
    found = False
    i = 0
    for s in que:
        if int(s) == args.number:
            found = True
            if i == 0:
                que = que[1:]
                with open(QUEUE_FILE, 'w') as f:
                    f.write(que)
                return True
            break
        i += 1
    if not found:
        with open(QUEUE_FILE, 'w') as f:
            f.write(que + str(args.number))
    return False





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Channel BTLE HRM data")
    parser.add_argument("device", help="Heart rate monitor MAC address", type=str)
    parser.add_argument("--format", help="Format string for output (use {heartrate}, {ppi})", default="{heartrate}", type=str)
    parser.add_argument("--data-dir", help="file to output to (defaults to stdout)", default=None, type=str)
    parser.add_argument("--number", help="monitor number", default=None, type=int)
    parser.add_argument("--verbosity", help="print much?", default=0, type=int)

    args = parser.parse_args()

    DEVICE_MAC = args.device
    if args.format is not None:
        OUTPUT_FMT = args.format

    if args.data_dir is None or args.data_dir == "":
        print("pls gibe file to output")
        sys.exit(0)
    OUTPUT_FILE=args.data_dir + "sensor" + str(args.number) + ".txt"
    QUEUE_FILE=args.data_dir + "que.txt"


    join_que()
    while True:
        if check_que():
            with open(OUTPUT_FILE, 'w') as file:
                file.write("")
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(main())
            except Exception as e:
                if args.verbosity > 0:
                    print(e, file=sys.stderr)
                time.sleep(5+random.random())
            time.sleep(3+random.random())
        time.sleep(1+random.random())
