import argparse
import configparser
import time
import requests
import json

import subprocess
import sys
import os
import time

DEVICES = [
    {"number": "1", "mac": "CD:44:02:18:7E:60", "id":"91AA972C", "status": "ready", "process": None, "delay": 0, "value": 0},
    {"number": "2", "mac": "EC:34:2B:4B:82:31", "id":"91AA6521", "status": "ready", "process": None, "delay": 0, "value": 0},
    {"number": "3", "mac": "EA:16:35:F9:58:B9", "id":"91A9F92F", "status": "ready", "process": None, "delay": 0, "value": 0},
    {"number": "4", "mac": "E8:D8:C7:0B:3F:21", "id":"91A9ED20", "status": "ready", "process": None, "delay": 0, "value": 0},
    {"number": "5", "mac": "CE:F5:71:BE:C3:C3", "id":"91A9F127", "status": "ready", "process": None, "delay": 0, "value": 0}
]


def main():
    verbosity = args.verbosity
    connecting = -1
    if len(sys.argv) > 2:
        verbosity = sys.argv[2]
    heart_rates_latest = []
    heart_rates = []
    for device in DEVICES:
        with open(f'./data/sensor{device["number"]}.txt', 'w') as f:
            f.write(f'{int(time.time())},ready,0')
        heart_rates.append(0)
        heart_rates_latest.append(-1)
    while True:
        for device in DEVICES:
            if device["status"] in ["waiting", "ready"]:
                continue
            if isinstance(device["process"], subprocess.Popen):
                ret = device["process"].poll()
                if ret is None:
                    data = ""
                    with open(f'./data/sensor{device["number"]}.txt', 'r') as f:
                        data = f.read()
                    if data:
                        data = data.split(",")
                        if len(data) == 3:
                            device['delay'] = int(time.time()) - int(data[0])
                            device['status'] = data[1]
                            device['value'] = int(data[2])
                            if device['delay'] > 20:
                                device['status'] = "lagging"
                                if device['delay'] > 60:
                                    device['status'] = "dead"
                                continue
                            continue
                    device["status"] = "wrong data"
                    if device["value"] > 0:
                        device["value"] = -1
                    else:
                        device["value"] -= 1
                    if device["value"] < -15:
                        device['status'] = "dead"

                else:
                    if device["status"] in ["connecting"]:
                        device["value"] += 1
                        if device["value"] < 10:
                            continue
                    device["status"] = "closed"
        loopi = -1
        for device in DEVICES:
            loopi += 1
            if device["status"] in ["connecting"]:
                heart_rates[loopi] = 0

            if device["status"] in ["connected"]:
                if connecting == device["number"]:
                    connecting = -1

            if device["status"] in ["ok", "lagging"]:
                if connecting == device["number"]:
                    connecting = -1
                heart_rates[loopi] = device["value"]
                continue
            if device["status"] in ["wrong data"]:
                continue
            if device["status"] in ["error"]:
                if device["value"] > 20:
                    device["status"] = "dead"
                else:
                    continue
            if device["status"] in ["dead", "disconnected"]:
                device["process"].kill()
                device["status"] = "killed"
                heart_rates[loopi] = 0
                if connecting == device["number"]:
                    connecting = -1
                continue
            if device["status"] in ["closed"]:

                heart_rates[loopi] = 0
                if connecting == device["number"]:
                    connecting = -1
                device["value"] = 1
                for d in DEVICES:
                    if d["status"] in ["ready", "waiting"]:
                        device["value"] += 1
                device["status"] = "waiting"
                continue

            if device["status"] in ["waiting"]:
                heart_rates[loopi] = 0
                found = False
                for d in DEVICES:
                    if d["status"] in ["ready"] and device["value"] == 1:
                        found = True
                        break
                    if d["status"] in ["waiting"]:
                        if d["value"] == device["value"] -1:
                            found = True
                            break
                if found:
                    continue
                device["value"] -= 1
                if device["value"] <= 0:
                    device["status"] = "ready"
                continue

            if device["status"] in ["ready"]:
                heart_rates[loopi] = 0
                if connecting == -1 or connecting == device["number"]:
                    connecting = device["number"]
                    device["process"] = subprocess.Popen([f'python', './monitor.py', f'{device["mac"]}', f'--number={device["number"]}', f'--verbosity={verbosity}'])
                    device["status"] = "connecting"
                continue

        try:
            for i in range(len(heart_rates)):
                if heart_rates[i] != heart_rates_latest[i]:
                    patchStreamMetadata(config, {'heart_rates': heart_rates})
                    for i in range(len(heart_rates)):
                        heart_rates_latest[i] = heart_rates[i]
                    break

        except Exception as e:
            if verbosity > 0:
                print(e)
            time.sleep(15)
        time.sleep(1)

def patchStreamMetadata(config, value):
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.patch(f'{api_url}/stream-metadata/', json=value, auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        if args.verbosity > 0:
            print(r.status_code)
            print(r.content)


if __name__ == "__main__":

    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)

    parser = argparse.ArgumentParser(description="Do monitorings")
    parser.add_argument("--verbosity", help="print much?", default=0, type=int)

    args = parser.parse_args()

    configReader = configparser.ConfigParser()
    configReader.read("./config.ini")

    config = configReader['CONFIG']
    if not config:
        print('Please give config')
        quit()


    main()