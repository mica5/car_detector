#!/usr/bin/env bash

while true ; do

    ping_seconds_ago=$(( $(date +%s) - $(cat last_checkup.txt ) ))

    running=true
    ps aux | grep [u]ltrasonic_distance_reader.py >/dev/null || running=false

    restart=false

    # it's not running, so start it
    if ! $running ; then
        restart=true

    # it's frozen, so kill it and restart it
    elif [ $ping_seconds_ago -gt 10 ] ; then
        restart=true
        ps aux | grep -v grep | grep [u]ltrasonic_distance_reader.py \
            | while read line ; do
                kill $(echo $line|cut -d" " -f2)
            done
    fi

    if $restart ; then
        echo restarting
        nohup bash -c '/usr/bin/python3 ultrasonic_distance_reader.py | nc localhost 53134' &
    else
        echo not restarting
    fi

    sleep 20
done
