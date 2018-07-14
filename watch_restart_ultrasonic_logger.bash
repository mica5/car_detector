#!/usr/bin/env bash

if [ ! -e last_checkup.fifo ] ; then
    mkfifo last_checkup.fifo
fi

while true ; do

    ping_seconds_ago=$(( $(date +%s) - $(cat last_checkup.fifo ) ))

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
                # send INT to allow it to clean up resources.
                # it's equivalent to KeyboardInterrupt (control-c).
                kill -INT $(echo $line|cut -d" " -f2)
            done
    fi

    if $restart ; then
        nohup bash -c '/usr/bin/python3 ultrasonic_distance_reader.py --send-checkups' &
    fi

    sleep 20
done
