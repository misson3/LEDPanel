# Jan28, 2020, ms
# haya2InfoHandler.py

# UNDER CONSTRUCTION

import serial
import time
import json


def sendHaltingMessageToSerial():
    # dummy info for now
    info_dict = {"red": [1, "Halting...", "Bye."]}
    print(info_dict)

    # send the dict to serial
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
    time.sleep(2)
    json_string = json.dumps(info_dict) + '\n'
    ser.write(json_string.encode())
    ser.close()


if __name__ == '__main__':
    pass
