#!/usr/bin/env bash

this_dir="$(dirname "$(readlink -e $0)")"

source "$this_dir"/config.bash

ps aux | grep [${LOCALHOST_PORT:0:1}]${LOCALHOST_PORT:1:99} >/dev/null || {
    ssh -R $LOCALHOST_PORT:localhost:22 $REMOTE_USERNAME@$REMOTE_HOSTNAME -N -T -f
}
