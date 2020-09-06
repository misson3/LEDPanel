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
        for i, d in enumerate(res_dict['routes']):
            estimation = d['legs'][0]['duration_in_traffic']['text']
            estimation = estimation.split(' ')[0]
            summary = d['summary']
            estimations.append(estimation)
            summaries.append(summary)

    return estimations, summaries


def getInfoAndSendItToSerial2(routes):
    # for now, routes = ('r1', 'r2')
    key = credict['api_key']
    ori, dest1 = credict[routes[0]]
    dest1, dest2 = credict[routes[1]]

    estTimes1, summaries1 = getEstimations(key, ori, dest1)
    time.sleep(3)
    estTimes2, summaries2 = getEstimations(key, dest1, dest2)

    # {'route': [1,
    # ['RouteNow', 'r1'],
    # [min, summary], [min, summary], [min, summary],
    # [min, summary], [min, summary], [min, summary],
    # time]}
    info_dict = {"route": [
                            1,
                            ["RouteNow", "r1"],
                            # r1
                            ["--", "--"],
                            ["--", "--"],
                            ["--", "--"],
                            # r2
                            ["--", "--"],
                            ["--", "--"],
                            ["--", "--"],
                            timeStamp()
                            ]
                }

    for i in range(len(estTimes1)):
        info_dict["route"][i+2][0] = estTimes1[i]
        info_dict["route"][i+2][1] = summaries1[i]
        info_dict["route"][i+5][0] = estTimes2[i]
        info_dict["route"][i+5][1] = summaries2[i]

    print(info_dict)

    # send the dict to serial
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
    time.sleep(2)
    json_string = json.dumps(info_dict) + '\n'
    ser.write(json_string.encode())
    ser.close()


if __name__ == '__main__':
    getInfoAndSendItToSerial2('r1')
    # pass
