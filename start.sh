#!/bin/bash
# Raplace old start.sh to avoid changing rc.local
# This script run old start.sh (now dnc.sh) on a detached GNU screen session

which screen
screen=$?
if [ $screen -eq 1 ]; then       # There isn't the GNU screen binary, try to install it
    echo "nameserver 8.8.4.4" > /etc/resolv.conf
    pacman -Sy --noconfirm screen
    screen=$?
    echo "termcapinfo xterm* ti@:te@" > ~/.screenrc
fi

if [ $screen -eq 0 ]; then      # There is the GNU screen binary

    echo "Start in a GNU screen session named 'dnc'"
    if [ "$(screen -ls | grep dnc)" = "" ]; then
        sleep 0.01
    else
        screen -S dnc -X stuff "q$(printf \\r)"
        sleep 10
        screen -X -S netctl quit
        sleep 1
    fi
    screen -S dnc -d -m /dnc/dnc.sh -o
    if [ "$(screen -ls | grep netctl)" = "" ]; then
        sleep 0.01
    else
        screen -X -S netctl quit
        sleep 1
    fi
    screen -S netctl -d -m /dnc/bash/netctl-watchdog.py
else
    echo "Start in a classic shell so without the -o option"
    netctl -d -m /dnc/bash/netctl-watchdog.py &
    /dnc/dnc.sh &
fi

exit $?

