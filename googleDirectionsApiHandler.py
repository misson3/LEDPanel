# Sep 01,02, 2020, ms
# googleDirectionsApiHandler.py

import datetime
import json
# import serial
import time
import urllib.request

# get piece of credinfo
import myCreds  # my

credict = myCreds.myc()

# def sendToSerial(info_dict):
#     # send the dict to serial
#     ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
#     time.sleep(2)
#     json_string = json.dumps(info_dict) + '\n'
#     ser.write(json_string.encode())
#     ser.close()


def getInfoAndSendItToSerial2(route):
    key = credict['api_key']
    ori, dest = credict[route]

    # url construction
    # API  parameters
    url = 'https://maps.googleapis.com/maps/api/directions/json?'
    url += 'origin=place_id:' + ori
    url += '&destination=place_id:' + dest
    url += '&mode=driving&departure_time=now&alternatives=true'
    url += '&key=' + key

    req = urllib.request.Request(url, method='GET')

    with urllib.request.urlopen(req) as res:
        body1 = res.read()
        # print(type(body1))  # bytes
        decoded_body1 = body1.decode('utf8')
        # print(type(decoded_body1))  # str
        # decoded_body1_loadsed = json.loads(decoded_body1)
        # print(type(decoded_body1_loadsed))  # dict
        res_dict = json.loads(decoded_body1)

        # print(res_dict)

        for d in res_dict['routes']:
            print(d['legs'][0]['duration_in_traffic']['text'])
            print(d['summary'])


if __name__ == '__main__':
    getInfoAndSendItToSerial2('r1')
    # pass
