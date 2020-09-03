# Sep02, 2020, ms
# move all creds to separate file (myCreds.py)

# Jan28, 2020, ms
# Feb09, 2020, ms  # add before(aft ut station) and after bus stops
# Feb15, 2020, ms  # change line drawing rule
# Feb22, 2022, ms  # create program green: stop0, stop-1, stop-2
# busInfoHandler.py

# ref codes from my previous work
# myPredict2.py
# myLEDBoard2.py
# credentials file: myLEDBoard_credentials.txt

# previous code is still confusing.
# some says, urllib.request is enough for most of works
# try with this
# ref: https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217


import urllib.request
import json
import datetime
import serial
import time

# get piece of credinfo
import myCreds  # my

credict = myCreds.myc()


# helper function
def busTimeStr_to_WaitingTime(time_str):
    # str example
    # 2019-05-26T14:24:38+08:00
    ymd, hms = time_str.split('T')
    y, mon, d = ymd.split('-')
    h, m, s = hms.split('+')[0].split(':')
    # create datetime obj
    dt_obj = datetime.datetime(int(y), int(mon), int(d),
                               int(h), int(m), int(s))
    dt_now = datetime.datetime.now()
    # take diff ==> timedelta object
    td = dt_obj - dt_now
    days = td.days
    hours = td.seconds//3600
    minutes = (td.seconds//60)
    if days < 0:
        # waiting_time = 'Left'
        waiting_time = 'Le'
    else:
        if minutes == 0:
            # waiting_time = 'Arriving'
            waiting_time = 'Ar'
        else:
            waiting_time = str(minutes).zfill(2)  # + ' min'
            '''
            if minutes != 1:
                waiting_time += 's'
            '''
    return waiting_time


def getBusInfo(bus_stop, bus_service):
    # Auth params
    headers = {'AccountKey': credict['AccountKey'],
               'accept': 'application/json'}
    # API  parameters
    url = 'http://datamall2.mytransport.sg'
    url += '/ltaodataservice/BusArrivalv2?'
    url += 'BusStopCode=' + bus_stop
    url += '&ServiceNo=' + bus_service

    req = urllib.request.Request(url, headers=headers, method='GET')

    with urllib.request.urlopen(req) as res:
        body1 = res.read()
        # print(type(body1))  # bytes
        decoded_body1 = body1.decode('utf8')
        # print(type(decoded_body1))  # str
        # decoded_body1_loadsed = json.loads(decoded_body1)
        # print(type(decoded_body1_loadsed))  # dict
        res_dict = json.loads(decoded_body1)

    waiting_times = []
    for bus in ['NextBus', 'NextBus2', 'NextBus3']:
        arrTime = res_dict['Services'][0][bus]['EstimatedArrival']
        load = res_dict['Services'][0][bus]['Load']
        waiting_min = busTimeStr_to_WaitingTime(arrTime)
        waiting_times.append((waiting_min, load))
    print(bus_stop, waiting_times)

    return waiting_times


def sendToSerial(info_dict):
    # send the dict to serial
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)  # this is on raspi
    time.sleep(2)
    json_string = json.dumps(info_dict) + '\n'
    ser.write(json_string.encode())
    ser.close()


def makeBusStopInfoList(predictions):
    # predictions = [('Left', 'SEA'), ('06 mins', 'SEA'), ('17 mins', 'SEA')]
    # waiting min and color part
    info_list = []
    for waiting_min, load in predictions:
        col = 'W'  # only OGYR is specified in arduino code. W will give white
        # if waiting_min == 'Left':
        # if waiting_min == 'Le':
        #    col = "O"
        # else:
        if load == 'SEA':  # Seats Available
            col = "G"
        elif load == 'SDA':  # Standing Available
            col = "Y"
        elif load == 'LSD':  # Limited Standing
            col = "R"
        info_list.append(waiting_min)
        info_list.append(col)
    return info_list


def convertToInt(s):
    i = 0
    if s == 'Ar':
        i = 0
    elif s == 'Le':
        i = -1
    else:
        i = int(s)
    return i


def compare3(L1, L2, L3, R1, diff):
    # L1,2,3, and R1 are: 'Le', 'Ar' or int-able str
    # convert 'Le' as -1, 'Ar' as 0 and int any int-able str
    connector = 0
    if L1 - R1 > diff:
        connector = 3  # dash
    elif L2 - R1 > diff:
        connector = 2  # slash
    elif L3 - R1 > diff:
        connector = 1
    else:
        connector = 0
    return connector


def getInfoAndSendItToSerial2(gray_or_green):
    '''
    |<--- gray --------------->|
                |<--- green ----------->|
    Next --- target --- aft sttn --- sttn
    stop1    stop0      stop-1       stop-2
    '''
    # this is what I want to construct
    # {'bus': [2, 'BusNow', 'DP1|DP2',  # display 1 (gray), display 2 (green)
    #              ['01', 'G', '08', 'G', '12', 'G'],  # stop0: CENTER
    #              ['Ar', 'G', '15', 'Y', '18', 'R'],  # Before: RIGHT
    #              ['03', 'O', '09', 'G', '14', 'Y'],  # After: LEFT
    #              ['slash2', 'dash3']]}  # // or ---
    bus_service = credict['bus_service1']
    if gray_or_green == 'gray':
        pred_L = getBusInfo(credict['stop1'], bus_service)
        pred_C = getBusInfo(credict['stop0'], bus_service)
        pred_R = getBusInfo(credict['stop-1'], bus_service)
        L_C_diff = 0
        C_R_diff = 4
        DP = 'DP1'
    elif gray_or_green == 'green':
        pred_L = getBusInfo(credict['stop0'], bus_service)
        pred_C = getBusInfo(credict['stop-1'], bus_service)
        pred_R = getBusInfo(credict['stop-2'], bus_service)
        L_C_diff = 4
        C_R_diff = 2  # ---------------- NEED TO BE ADJUSTED #################
        DP = 'DP2'
    # pred is list of tuples something like;
    # [('Left', 'SEA'), ('06 mins', 'SEA'), ('17 mins', 'SEA')]

    # dict construction
    info_dict = {"bus": [2, "BusNow", DP]}

    info_L = makeBusStopInfoList(pred_L)
    info_C = makeBusStopInfoList(pred_C)
    info_R = makeBusStopInfoList(pred_R)

    # dash, slash, or long line.  connection line
    # between stop1 and stop0, between stop0 and stop-1 or stop-2
    L1 = convertToInt(info_L[0])
    L2 = convertToInt(info_L[2])
    L3 = convertToInt(info_L[4])
    C1 = convertToInt(info_C[0])
    C2 = convertToInt(info_C[2])
    C3 = convertToInt(info_C[4])
    R1 = convertToInt(info_R[0])

    L_C_con = compare3(L1, L2, L3, C1, L_C_diff)
    C_R_con = compare3(C1, C2, C3, R1, C_R_diff)

    info_dict["bus"].append(info_C)
    info_dict["bus"].append(info_R)
    info_dict["bus"].append(info_L)
    info_dict["bus"].append([L_C_con, C_R_con])

    # info_dict is ready. send it to serial
    print("infodict:", info_dict)
    sendToSerial(info_dict)


if __name__ == '__main__':
    # getBusInfo(credict['stop1'], credict['bus_service'])
    # getInfoAndSendItToSerial(credict['stop0'], credict['bus_service'])
    pass
