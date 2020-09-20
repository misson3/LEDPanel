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


def timeStampFull():
    now = datetime.datetime.now()
    return now.strftime('%d%b%Y-%H:%M:%S')


def writeLog(t1, s1, t2, s2, mode):
    log_file = './googleDirections_log_ver2.csv'
    # fill element if the lists are shorter
    # t1 and s1, t2 and s2 should have the same lengths
    for _ in range(4 - len(t1)):
        t1.append('')  # just append blank
        s1.append('')
    # do the same for the set 2
    for _ in range(4 - len(t2)):
        t2.append('')  # just append blank
        s2.append('')

    # print
    # full ts, ts, t1 (3 cells), s1 (3 cells), t2 (3 cells), s2 (3 cells)
    # line construction
    line = [timeStampFull(), timeStamp(), mode]
    for list_ in (t1, s1, t2, s2):
        line.append('\t'.join(list_))

    with open(log_file, mode='a') as LOG:
        LOG.write('\t'.join(line) + '\n')


def getEstimations(key, point1, point2, mode):
    # url construction
    # API  parameters
    url = 'https://maps.googleapis.com/maps/api/directions/json?'
    url += 'origin=place_id:' + point1
    url += '&destination=place_id:' + point2
    url += '&mode=' + mode
    url += '&departure_time=now&alternatives=true'
    url += '&key=' + key

    print(url)

    req = urllib.request.Request(url, method='GET')

    # parse key control
    if mode == 'driving':
        key_to_see = 'duration_in_traffic'
    else:  # transit
        key_to_see = 'duration'

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
            estimation = d['legs'][0][key_to_see]['text']
            estimation = estimation.split(' ')[0]
            summary = d['summary']
            estimations.append(estimation)
            summaries.append(summary)
    print('estimations', estimations)
    print('summaries', summaries)

    return estimations, summaries


def getInfoAndSendItToSerial2(routes, heads, driving):
    key = credict['api_key']
    ori1, dest1 = credict[routes[0]]
    ori2, dest2 = credict[routes[1]]
    print("bool driving:", driving)
    if driving:
        mode = 'driving'
    else:
        mode = 'transit'

    estTimes1, summaries1 = getEstimations(key, ori1, dest1, mode)
    time.sleep(3)
    estTimes2, summaries2 = getEstimations(key, ori2, dest2, mode)

    if driving:
        code = 'dr'
    else:
        code = 'tr'
    row_1 = ['ETA Now', code]
    row_2 = heads[0] + ','.join(estTimes1)
    row_3 = heads[1] + ','.join(estTimes2)
    row_4 = timeStamp()

    info_dict = {"route": [1, row_1, row_2, row_3, row_4]}

    print(info_dict)

    # send the dict to serial
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
    time.sleep(2)
    json_string = json.dumps(info_dict) + '\n'
    ser.write(json_string.encode())
    ser.close()

    # take a log (the file name is fixed)
    writeLog(estTimes1, summaries1, estTimes2, summaries2, mode)


if __name__ == '__main__':
    # getInfoAndSendItToSerial2(('s1', 's2'))
    getInfoAndSendItToSerial2(('s3', 's4'), ('B:', 'L:'), False)
    #
    # key = credict['api_key']
    # ori, dest1 = credict['s1']
    # dest1, dest2 = credict['s2']
    # getEstimations(key, ori, dest1)
    # getEstimations(key, dest1, dest2)
    # pass
