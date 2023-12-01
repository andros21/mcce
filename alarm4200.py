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

import gpiod


def software_pwm(line, frequency, duty_cycle):
    """Software PWM until API availability for hardware PWM"""
    period = 1 / frequency
    on_time = period * (duty_cycle / 100)

    for i in range(10):
        line.set_value(1)
        time.sleep(on_time)

        line.set_value(0)
        time.sleep(period - on_time)


if __name__ == "__main__":
    chip = gpiod.Chip("gpiochip0")

    # Set up lines
    dc_line = chip.get_line(17)
    dc_line.request(consumer="my_consumer", type=gpiod.LINE_REQ_DIR_OUT)

    dc_line.set_value(1)  # DC Power on

    freq = 5000
    pwm_line = chip.get_line(18)
    pwm_line.request(consumer="my_consumer", type=gpiod.LINE_REQ_DIR_OUT)

    # Do alarm ring
    for step in range(0, 10):
        for i in range(0, 100):
            software_pwm(pwm_line, freq + (1250 * i), 50)
        for i in range(0, 100):
            software_pwm(pwm_line, freq + (1250 * 100) - (1000 * i), 50)

    # Cleanup
    dc_line.release()
    pwm_line.release()
    chip.close()
