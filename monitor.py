#!/bin/env python3

import asyncio
import argparse
import bleak
import sys

DEVICE_MAC = "CE:F5:71:BE:C3:C3"
OUTPUT_FMT = "{heartrate}, {ppi}ms"
OUTPUT_FILE = sys.stdout

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

        print(OUTPUT_FMT.format(heartrate=heartrate, ppi=peak_to_peak_ms), file=OUTPUT_FILE)

    else:
        print ("received unexpected data", file=sys.stderr)

async def run(client):
    while not client.is_connected:
        pass

    print ("device", DEVICE_MAC, "connected", file=sys.stderr)

    services = await client.get_services()
    heartrate_service = find_heartrate_service(services)
    heartrate_measurement = find_heartrate_measurement_characteristic(heartrate_service)

    print ("asking for notifications from", heartrate_measurement, file=sys.stderr)
    
    await client.start_notify(heartrate_measurement, read_callback)

    while(True):
        await asyncio.sleep(60)

    sys.exit(0)

async def main():
    print("Connecting to", DEVICE_MAC, file=sys.stderr)
    async with bleak.BleakClient(DEVICE_MAC) as client:
        tasks = [ asyncio.ensure_future(run(client)) ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Channel BTLE HRM data")
    parser.add_argument("device", help="Heart rate monitor MAC address", type=str)
    parser.add_argument("--format", help="Format string for output (use {heartrate}, {ppi})", default="{heartrate}", type=str)
    parser.add_argument("--output-file", help="file to output to (defaults to stdout)", default=None, type=str)

    args = parser.parse_args()

    DEVICE_MAC = args.device
    if args.format is not None:
        OUTPUT_FMT = args.format

    if args.output_file is not None:
        OUTPUT_FILE = args.output_file

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

