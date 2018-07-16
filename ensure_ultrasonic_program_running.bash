#!/usr/bin/env bash

ps aux | grep -v grep | grep [u]ltrasonic_distance_reader.py >/dev/null || {
    /usr/bin/python3 /home/pi/git/car_detector/ultrasonic_distance_reader.py
}
