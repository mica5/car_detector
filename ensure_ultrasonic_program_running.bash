#!/usr/bin/env bash

ps aux | grep [u]ltrasonic_distance_reader.py || {
    /usr/bin/python3 /home/pi/git/car_detector/ultrasonic_distance_reader.py
}
