#!/bin/env python3

import asyncio
import argparse
import random
import json

import bleak
import sys
import time
import os.path

DEVICE_MAC = ""
OUTPUT_FILE = ""
ERROR_VALUE = 0


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
    global ERROR_VALUE
    if (data[0] == 0x10):
        heartrate = int(data[1])
        set_status("ok", heartrate)
        ERROR_VALUE = 0
    else:
        ERROR_VALUE += 1
        set_status("error", ERROR_VALUE)


def set_status(status, value):
    with open(OUTPUT_FILE, 'w') as ff:
        ff.write(f'{int(time.time())},{status},{value}')

    if args.verbosity > 1:
        print(f'{monitornumber}.{int(time.time())},{status},{value}')


async def run(client):
    set_status("connected", 0)
    if args.verbosity > 0:
        print("device", DEVICE_MAC, "connected", file=sys.stderr)

    services = await client.get_services()
    heartrate_service = find_heartrate_service(services)
    heartrate_measurement = find_heartrate_measurement_characteristic(heartrate_service)

    if args.verbosity > 1:
        print("asking for notifications from", heartrate_measurement, file=sys.stderr)

    await client.start_notify(heartrate_measurement, read_callback)

    while True:
        if not await client.is_connected():
            break
        await asyncio.sleep(1.0)


async def main():
    if args.verbosity > 0:
        print("Connecting to", DEVICE_MAC, file=sys.stderr)
    async with bleak.BleakClient(DEVICE_MAC) as client:
        tasks = [asyncio.ensure_future(run(client))]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Channel BTLE HRM data")
    parser.add_argument("device", help="Heart rate monitor MAC address", type=str)
    parser.add_argument("--number", help="monitor number", default=None, type=int)
    parser.add_argument("--verbosity", help="print much?", default=0, type=int)

    args = parser.parse_args()
    monitornumber = args.number
    DEVICE_MAC = args.device

    OUTPUT_FILE = "./data/sensor" + str(args.number) + ".txt"
    set_status("connecting", 0)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception as e:
        set_status("disconnected", 0)

