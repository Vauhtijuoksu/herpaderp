import argparse
import configparser
import time
import requests
import json


def patchStreamMetadata(config, value):
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.patch(f'{api_url}/stream-metadata/', json=value, auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        print(r.status_code)
        print(r.content)


if __name__ == "__main__":
    configReader = configparser.ConfigParser()
    configReader.read('config.ini')

    config = configReader['CONFIG']
    if not config:
        print('Please give config')
        quit()

    parser = argparse.ArgumentParser(description="apisender")
    parser.add_argument("--input-file",  nargs='+', help="filenames(s) to input to ", required=True, type=str)

    args = parser.parse_args()

    while True:
        heart_rates = []
        for input_file in args.input_file:
            try:
                with open(input_file, 'r') as file:
                    heart_rate = file.readline()
                    if not heart_rate:
                        heart_rates.append(0)
                    else:
                        heart_rates.append(int(heart_rate.strip()))
            except FileNotFoundError:
                heart_rates.append(0)

        patchStreamMetadata(config, {'heart_rates': heart_rates})
        time.sleep(1)