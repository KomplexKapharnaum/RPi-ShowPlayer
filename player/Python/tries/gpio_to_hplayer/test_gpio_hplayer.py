#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv

import liblo
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# GPIO 23 & 24 set up as inputs. One pulled up, the other down.
# 23 will go to GND when button pressed and 24 will go to 3V3 (3.3V)
# this enables us to demonstrate both rising and falling edge detection
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# now we'll define the threaded callback function
# this will run in another thread when our event is detected
def pause(channel):
    liblo.send(liblo.Address("2.0.0.205", 9000), liblo.Message("/pause"))

def next(channel):
    liblo.send(liblo.Address("2.0.0.205", 9000), liblo.Message("/next"))

def prev(channel):
    liblo.send(liblo.Address("2.0.0.205", 9000), liblo.Message("/prev"))


# The GPIO.add_event_detect() line below set things up so that
# when a rising edge is detected on port 24, regardless of whatever 
# else is happening in the program, the function "my_callback" will be run
# It will happen even while the program is waiting for
# a falling edge on the other button.
GPIO.add_event_detect(26, GPIO.RISING, callback=pause, bouncetime=500)
GPIO.add_event_detect(20, GPIO.RISING, callback=next, bouncetime=500)
GPIO.add_event_detect(21, GPIO.RISING, callback=prev, bouncetime=500)

try:
    raw_input("Press to quit")
except KeyboardError:
    GPIO.cleanup()
GPIO.cleanup()           # clean up GPIO on normal exit

