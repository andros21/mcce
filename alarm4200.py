#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ..................................................
#            __                     __ __
#     ____ _/ /___ __________ ___  / // /
#    / __ `/ / __ `/ ___/ __ `__ \/ // /_
#   / /_/ / / /_/ / /  / / / / / /__  __/
#   \__,_/_/\__,_/_/  /_/ /_/ /_/  /_/
#
#   Author: Andrea Rossoni
#   Scope:  Simple script to pilot a mini buzzer
#           using a driver connected with Rpi's PWM
# ..................................................

import time

import RPi.GPIO as GPIO

if __name__ == "__main__":

    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(11, GPIO.OUT)  # DC line
    GPIO.setup(12, GPIO.OUT)  # PWM signal

    GPIO.output(11, 1)  # DC Power on
    freq = 7000
    p = GPIO.PWM(12, freq)  # PWM setup

    # Do alarm ring
    p.start(1)
    for step in range(0, 3):
        i = 0
        for i in range(0, 100):
            p.ChangeFrequency(freq + (125 * i))
            time.sleep(0.005)
        i = 0
        for i in range(0, 100):
            p.ChangeFrequency(freq + (125 * 100) - (100 * i))
            time.sleep(0.005)
    p.stop()

    GPIO.cleanup()  # Flush values
