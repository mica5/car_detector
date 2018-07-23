#!/usr/bin/env bash

pid=$(ps aux | grep [u]ltrasonic | grep -v ensure | xargs echo | cut -d' ' -f2)
if [ -n "$pid" ] ; then
    kill $pid
fi
python ultrasonic_distance_reader.py --print-distances --print-plus-1s
