"""
original setup/code credits to https://www.modmypi.com/blog/hc-sr04-ultrasonic-range-sensor-on-the-raspberry-pi

"""
import RPi.GPIO as GPIO
import time
import numpy as np
import subprocess
import datetime

from config import (
    TRIG,
    ECHO,
    max_distance_cm
)

a = np.zeros(10)

GPIO.setmode(GPIO.BCM)
# print "Distance Measurement In Progress"
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)

# print "Waiting For Sensor To Settle"
time.sleep(2)

# handle KeyboardInterrupt (control-C on the command line)

car = False
last_checkup = datetime.datetime.now()

try:
    i = 0
    while True:
        if (datetime.datetime.now() - last_checkup).total_seconds() > 10:
            with open('last_checkup.txt', 'w') as fa:
                now = datetime.datetime.now()
                print(now.strftime('%s'), file=fa, flush=True)
                last_checkup = now
        GPIO.output(TRIG, True)

        # we don't need to check that often..
        # time.sleep(0.00001)
        time.sleep(0.01)

        GPIO.output(TRIG, False)
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        distance = round((pulse_end - pulse_start) * 17150, 2)
        if distance < max_distance_cm:
            a[i] = distance
            i += 1
            print('{:> 7.2f} {:>3.2f} {:>3.2f}'.format(distance, a.mean(), a.std()), flush=True)
            i %= len(a)

            if distance < 50:
                car = True
            if distance > 50 and car == True:
                car = False
                subprocess.call('bash sensor', shell=True)

except KeyboardInterrupt:
    GPIO.cleanup()
    raise
