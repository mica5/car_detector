"""
original setup/code credits to https://www.modmypi.com/blog/hc-sr04-ultrasonic-range-sensor-on-the-raspberry-pi

"""
import time
import subprocess
import datetime
import argparse
from os.path import join, abspath, dirname

import RPi.GPIO as GPIO
import numpy as np

from config import (
    TRIG,
    ECHO,
    max_distance_cm
)

a = np.zeros(10)
default_count = -1

def rolling_average(val, new_val):
    final_val = val
    if val == 0:
        final_val = new_val
    final_val += .01 * (new_val - val)
    return final_val

def run_main():
    args = parse_cl_args()
    sleep_seconds = args.seconds
    do_send_plus_1 = not args.dont_send
    print_distances = args.print_distances
    max_distance_cm = args.max_distance
    send_checkups = args.send_checkups
    max_distance_in_seconds = max_distance_cm / 17150
    print_plus_1s = args.print_plus_1s

    using_count = args.count != default_count
    count = args.count

    # keep rolling mean/standard deviation
    a = np.zeros(10)

    GPIO.setmode(GPIO.BCM)
    # print("Distance Measurement In Progress")
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG, False)

    car = False
    last_checkup = datetime.datetime.now() - datetime.timedelta(seconds=10)
    exit_now = False
    this_dir = dirname(abspath(__file__))

    if send_checkups:
        last_checkup_fifo = join(this_dir, 'last_checkup.fifo')
        subprocess.call('mkfifo "{}"'.format(last_checkup_fifo), shell=True)
        send_checkup_command = 'date +%s >> "{}" &'.format(last_checkup_fifo)

    send_plus_1_command = 'bash {}'.format(join(this_dir, 'sensor'))
    wall_dist = 6

    # print("Waiting For Sensor To Settle")
    time.sleep(2)
    try:
        array_index = 0
        while True:

            # keep sending pings so that the watcher
            # knows this process isn't frozen.
            if send_checkups:
                if (datetime.datetime.now() - last_checkup).total_seconds() >= 10:
                    last_checkup = datetime.datetime.now()
                    subprocess.call(send_checkup_command, shell=True)

            # limit to the number of recordings
            # the user asked for
            if using_count:
                count -= 1
                if count <= 0:
                    break
            if exit_now:
                break

            ## get sensor distance data
            time.sleep(sleep_seconds)

            # create the trigger pulse by turning TRIG on for 10 microseconds.
            GPIO.output(TRIG, True)
            time.sleep(.00001)
            GPIO.output(TRIG, False)

            # see how long it takes for pulse to reach back to sensor.
            # handle the case when we never get any input.
            time_before_loops = time.time()
            while GPIO.input(ECHO) == 0:
                # maximum 13 feet
                if time.time() - time_before_loops > max_distance_in_seconds:
                    break
            # front of wave hits input sensor
            pulse_start = time.time()
            while GPIO.input(ECHO) == 1:
                # maximum 13 feet
                if time.time() - time_before_loops > max_distance_in_seconds:
                    break
            # end of wave stops hitting input sensor
            pulse_end = time.time()

            # we finally have a distance measurement and
            # can do interesting stuff with it.
            distance = round((pulse_end - pulse_start) * 17150, 2)
            a[array_index] = distance
            array_index += 1
            if print_distances:
                print('{:> 7.2f} {:>3.2f} {:>3.2f}'.format(distance, a.mean(), a.std()))
            array_index %= len(a)

            distance_feet = distance / 2.54 / 12
            wall_dist = rolling_average(wall_dist, distance_feet)
            # count objects
            if distance_feet < wall_dist - 1:
                car = True
            elif distance_feet > (wall_dist - 1) and car:
                car = False
                if do_send_plus_1:
                    subprocess.call(send_plus_1_command, shell=True)
                if print_plus_1s:
                    print('+1')

    # handle KeyboardInterrupt (control-C on the command line)
    except KeyboardInterrupt:
        raise

    # clean up whether an error occurred or not
    finally:
        # TODO should this be done after every sensor reading??
        print('cleaning up')
        GPIO.cleanup()


def parse_cl_args():
    argParser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    argParser.add_argument(
        '-c', '--count', type=int, default=default_count,
        help='number of data points to collect'
    )
    argParser.add_argument(
        '-s', '--seconds', type=float, default=.01,
        help='number of seconds between data points, default %(default)s'
    )
    argParser.add_argument(
        '--dont-send', default=False, action='store_true',
        help="don't send +1s to the database"
    )
    argParser.add_argument(
        '--print-distances', default=False, action='store_true',
        help="print the distances to stdout; default, don't print"
    )
    argParser.add_argument(
        '--print-plus-1s', default=False, action='store_true',
    )
    argParser.add_argument(
        '--max-distance', default=max_distance_cm, type=float,
        help="consider this to be the max allowed detectable distance, and any reading greater than this will be ignored. default from the config.py is %(default)s"
    )
    argParser.add_argument(
        '--send-checkups', default=False, action='store_true',
        help="every 10 seconds, write current timestamp to named pipe 'last_checkup.fifo', so that watcher program can detect if this program freezes"
    )

    args = argParser.parse_args()
    return args


if __name__ == '__main__':
    success = run_main()
    exit_code = 0 if success else 1
    exit(exit_code)
