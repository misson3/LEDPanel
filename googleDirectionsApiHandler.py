# Sep 01,02, 2020, ms
# googleDirectionsApiHandler.py

import datetime
import json
import serial
import time
import urllib.request

# get piece of credinfo
import myCreds  # my

credict = myCreds.myc()


def timeStamp():
    now = datetime.datetime.now()
    return now.strftime('%H:%M')


def getEstimations(key, point1, point2):
    # url construction
    # API  parameters
    url = 'https://maps.googleapis.com/maps/api/directions/json?'
    url += 'origin=place_id:' + point1
    url += '&destination=place_id:' + point2
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

        estimations = []
        summaries = []
        for d in res_dict['routes']:
            estimation = d['legs'][0]['duration_in_traffic']['text']
            estimation = estimation.split(' ')[0]
            summary = d['summary']
            estimations.append(estimation)
            summaries.append(summary)
    # print('estimations', estimations)
    # print('summaries', summaries)

    return estimations, summaries


def getInfoAndSendItToSerial2(routes):
    # for now, routes = ('s1', 's2')  # stretch(stop)1, stretch(stop)2
    key = credict['api_key']
    ori, dest1 = credict[routes[0]]
    dest1, dest2 = credict[routes[1]]

    estTimes1, summaries1 = getEstimations(key, ori, dest1)
    time.sleep(3)
    estTimes2, summaries2 = getEstimations(key, dest1, dest2)

    # === I KNOW summaries ARE NOT USES ===
    # === LEAVE IT FOR NEXT VERSION ===

    row_1 = ["RouteNow", "r1"]
    row_2 = "1:" + ','.join(estTimes1)
    row_3 = "2:" + ','.join(estTimes2)
    row_4 = timeStamp()

    info_dict = {"route": [1, row_1, row_2, row_3, row_4]}

    print(info_dict)

    # send the dict to serial
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
    time.sleep(2)
    json_string = json.dumps(info_dict) + '\n'
    ser.write(json_string.encode())
    ser.close()


if __name__ == '__main__':
    getInfoAndSendItToSerial2(('s1', 's2'))
    #
    #key = credict['api_key']
    #ori, dest1 = credict['s1']
    #dest1, dest2 = credict['s2']
    #getEstimations(key, ori, dest1)
    #getEstimations(key, dest1, dest2)
    # pass
