#!/bin/env python3

import asyncio
import bleak
import sys

DEVICE_MAC = "CE:F5:71:BE:C3:C3"

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
    print ("♥", data[1])
    sys.stdout.flush()

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
    async with bleak.BleakClient(DEVICE_MAC) as client:
        tasks = [ asyncio.ensure_future(run(client)) ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
