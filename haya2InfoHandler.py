# Jan28, Feb01, 2020, ms
# haya2InfoHandler.py

# web scraping after javascript rendering is needed.
# I asked question on this qiita page and got an anwer!!!

# UNDER CONSTRUCTION

import serial
import time
import json
import urllib.request
import myCreds  # my

credict = myCreds.myc()

# https://requests.readthedocs.io/projects/requests-html/en/latest/


def getDataFromWeb():
    # web scraping is done on 3B1 as
    # it takes toooooo long sometimes if it is done on raspi zero w...
    # flask_for_Haya2_webscraping.py
    # flask server must be run to use this.
    # make sure it is running.
    url = credict['raspi_port_haya2']
    req = urllib.request.Request(url, method='GET')

    with urllib.request.urlopen(req) as res:
        body = res.read()
        decoded_body = body.decode('utf8')
        resp = json.loads(decoded_body)
        print('this is resp:', resp)
        time_since_launch = resp['time_since_launch']
        earth_to_haya2 = resp['earth_to_hayabusa']

    return time_since_launch, earth_to_haya2


def getHaya2WebInfoAndSendItToSerial():
    time_since_launch, earth_to_haya2 = getDataFromWeb()

    # info_dict
    # {"haya2":[1, "+1879d", "251571.33", "x1000 km"]}
    info_dict = {"haya2": [1, time_since_launch, earth_to_haya2, "x1000 km"]}
    print(info_dict)

    # send the dict to serial
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
    time.sleep(2)
    json_string = json.dumps(info_dict) + '\n'
    ser.write(json_string.encode())
    ser.close()


if __name__ == '__main__':
    print('test')
    tsl, eth = getDataFromWeb()  # test
