# Sep01, 2020
# 7_LED_button_with_threading_for_LED_matrix.py
# previous name: 6_LED_button_with_threading_for_LED_matrix.py
# to add estimated duration from google map directions api.

# jan27,28, Feb01, 2020, ms
# Feb22, 2020, ms  # bus display 1 (gray) and 2 (green)
# template-6_LED_button_with_threading_for_LED_matrix.py

# ref: https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/

import RPi.GPIO as GPIO
import sys
import threading
import time

import busInfoHandler  # my
import haya2InfoHandler  # my
import haltingInfoHandler  # my
import googleDirectionsApiHandler  # my


class CallBack:
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # GPIO pin number

        # button reading pin setup
        self.gray_btn_pin = 19
        self.blue_btn_pin = 16
        self.green_btn_pin = 21
        self.red_btn_pin = 6
        GPIO.setup(self.gray_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.blue_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.green_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.red_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # detect button press (High to Low)
        GPIO.add_event_detect(self.gray_btn_pin, GPIO.FALLING, bouncetime=1000)
        GPIO.add_event_detect(self.blue_btn_pin, GPIO.FALLING, bouncetime=1000)
        GPIO.add_event_detect(self.green_btn_pin, GPIO.FALLING, bouncetime=1000)
        GPIO.add_event_detect(self.red_btn_pin, GPIO.FALLING, bouncetime=1000)
        # connect callback
        GPIO.add_event_callback(self.gray_btn_pin, self.setProgramStatus)
        GPIO.add_event_callback(self.blue_btn_pin, self.setProgramStatus)
        GPIO.add_event_callback(self.green_btn_pin, self.setProgramStatus)
        GPIO.add_event_callback(self.red_btn_pin, self.setProgramStatus)
        # initialize program status: keep only 1 is active all the time
        self.gray_active = 0
        self.blue_active = 0
        self.green_active = 1
        self.red_active = 0

        # LED pin setup
        self.gray_LED_pin = 13
        self.blue_LED_pin = 12
        self.green_LED_pin = 20
        self.red_LED_pin = 5
        GPIO.setup(self.gray_LED_pin, GPIO.OUT, initial=GPIO.LOW)  # Bus
        GPIO.setup(self.blue_LED_pin, GPIO.OUT, initial=GPIO.LOW)  # Haya2
        GPIO.setup(self.green_LED_pin, GPIO.OUT, initial=GPIO.LOW)  # Green
        GPIO.setup(self.red_LED_pin, GPIO.OUT, initial=GPIO.LOW)  # Red

    # -----------------------------------------------------------------------
    # callback functions
    # translate button event to var values
    # self.gray_active, self.blue_active, self.green_active, self.red_active
    # -----------------------------------------------------------------------
    def resetProgramStatuses(self):
        self.gray_active = 0
        self.blue_active = 0
        self.green_active = 0
        self.red_active = 0

    def setProgramStatus(self, channel):
        self.resetProgramStatuses()  # reset all first
        if channel == self.gray_btn_pin:
            btn_col = 'gray'
            self.gray_active += 1
        elif channel == self.blue_btn_pin:
            btn_col = 'blue'
            self.blue_active += 1
        elif channel == self.green_btn_pin:
            btn_col = 'green'
            self.green_active += 1
        elif channel == self.red_btn_pin:
            btn_col = 'red'
            self.red_active += 1
        print(btn_col + ' button press detected.')

    # ---------------------------------------
    # functions called from monitoringLoop()
    # those will be run as separate thread
    # ---------------------------------------
    def offAllLEDs(self):
        # just turn off all LEDs
        pins = [self.gray_LED_pin, self.blue_LED_pin,
                self.green_LED_pin, self.red_LED_pin]
        for pin in pins:
            GPIO.output(pin, GPIO.LOW)

    def shortBlinkAndOn(self, channel):
        for i in range(2):
            GPIO.output(channel, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(channel, GPIO.LOW)
            time.sleep(0.5)
        GPIO.output(channel, GPIO.HIGH)

    def programGray(self, stop):
        """ google Directions """
        # stop is given as a lambda function which simply returns stop signal
        # in bool

        # off LED first
        self.offAllLEDs()
        self.shortBlinkAndOn(self.gray_LED_pin)
        print("Program Gray while loop Starts")

        i = 0
        while True:
            if i % 60 == 0:  # alternative way to execute every 60 sec
                # was to call bus info ('gray'), display pattern
                # busInfoHandler.getInfoAndSendItToSerial2('gray')
                # call googleDirections
                googleDirectionsApiHandler.getInfoAndSendItToSerial('r1')

            time.sleep(1)
            i += 1
            if stop():
                break
        print("Program Gray while loop exited")

    def programBlue(self, stop):
        # stop is given as a lambda function which simply returns stop signal
        # in bool
        # LED
        # off all
        self.offAllLEDs()
        self.shortBlinkAndOn(self.blue_LED_pin)
        print("Program Blue while loop Starts")

        i = 0
        while True:
            if i % 1800 == 0:  # every 30 min
                # ToDo: run Haya2 web scraping program here ---------
                haya2InfoHandler.getHaya2WebInfoAndSendItToSerial()
            time.sleep(1)
            i += 1
            if stop():
                break
        print("Program Blue while loop exited")

    def programGreen(self, stop):
        """ bus display 2 """
        # stop is given as a lambda function which simply returns stop signal
        # in bool

        # off LED first
        self.offAllLEDs()
        self.shortBlinkAndOn(self.green_LED_pin)
        print("Program Geen while loop Starts")

        i = 0
        while True:
            if i % 60 == 0:  # alternative way to execute every 60 sec
                # ToDo: run bus info retrieval program here -----------
                busInfoHandler.getInfoAndSendItToSerial2('green')
            time.sleep(1)
            i += 1
            if stop():
                break
        print("Program Green while loop exited")

    def shortBlinkRedLED(self, channel):
        for i in range(5):
            GPIO.output(channel, GPIO.HIGH)
            time.sleep(0.25)
            GPIO.output(channel, GPIO.LOW)
            time.sleep(0.25)
        for i in range(3):
            GPIO.output(channel, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(channel, GPIO.LOW)
            time.sleep(0.5)

    def programRed(self):
        # halting msg display
        haltingInfoHandler.sendHaltingMessageToSerial()
        # LED
        self.shortBlinkRedLED(self.red_LED_pin)
        # off all
        self.offAllLEDs()
        print("Program Red activated.")

    # -----------------------------------------------------------
    # monitoring loop
    # 1. when button is pressed, program status vars are changed
    # 2. the change will be captured in this loop and
    # 3. corresponding event is activated in a separate thread
    # while the separate thread is running, this main loop keep
    # turning
    # -----------------------------------------------------------
    def monitoringLoop(self):
        # vars to hold thread
        th_gray = None
        th_blue = None
        th_green = None
        # stop signals to break while loop in threads
        stop_th_gray = False
        stop_th_blue = False
        stop_th_green = False

        # loop: break when self.red_active is changed to 1
        while True:
            print('gray, blue, green, red: ',
                  self.gray_active, self.blue_active,
                  self.green_active, self.red_active)

            # check program status vars and do something accordingly
            # --- GRAY ---
            if self.gray_active == 1:
                self.gray_active += 1  # this is to prevent repeating
                # if other thread is running,
                # terminate them and let main stream handle it by .join()
                if th_blue is not None:
                    stop_th_blue = True
                    th_blue.join()
                if th_green is not None:
                    stop_th_green = True
                    th_green.join()
                # activate gray program thread
                stop_th_gray = False
                th_gray = threading.Thread(target=self.programGray,
                                           args=(lambda: stop_th_gray,))
                th_gray.start()
                print('programGray thread started')
            # --- BLUE ---
            elif self.blue_active == 1:
                self.blue_active += 1  # this is to prevent repeating
                # if other thread is running,
                # terminate them and let main stream handle it by .join()
                if th_gray is not None:
                    stop_th_gray = True
                    th_gray.join()
                if th_green is not None:
                    stop_th_green = True
                    th_green.join()
                # activate blue program thread
                stop_th_blue = False
                th_blue = threading.Thread(target=self.programBlue,
                                           args=(lambda: stop_th_blue,))
                th_blue.start()
                print('programBlue thread started')
            # --- GREEN ---
            elif self.green_active == 1:
                self.green_active += 1  # this is to prevent repeating
                # if other thread is running,
                # terminate them and let main stream handle it by .join()
                if th_gray is not None:
                    stop_th_gray = True
                    th_gray.join()
                if th_blue is not None:
                    stop_th_blue = True
                    th_blue.join()
                # activate blue program thread
                stop_th_green = False
                th_green = threading.Thread(target=self.programGreen,
                                            args=(lambda: stop_th_green,))
                th_green.start()
                print('programGeen thread started')
            # --- RED for termination ---
            elif self.red_active == 1:
                # I realized sys.exit() will handle all of this...
                # but just leave them for now.
                # terminate running thread
                # can not tell which is alive, set stop to all first
                stop_th_gray = True
                stop_th_blue = True
                stop_th_green = True
                # check th and merge to main
                if th_gray is not None:
                    th_gray.join()
                if th_blue is not None:
                    th_blue.join()
                if th_green is not None:
                    th_green.join()

                # blink Red LED
                self.programRed()
                # then,
                break

            time.sleep(1)
        sys.exit()


if __name__ == '__main__':
    cb = CallBack()
    cb.monitoringLoop()
