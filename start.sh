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
    echo "Using GNU screen.."
    if [ "$(screen -ls | grep dnc)" = "" ]; then
        sleep 0.01
    else
        echo "Stopping previous dnc prog..."
        screen -S dnc -X stuff "q$(printf \\r)"
        sleep 7
        if [ "$(screen -ls | grep dnc)" = "" ]; then
            sleep 0.01
        else
            echo "Stopping previous dnc screen session..."
            screen -X -S dnc quit
            sleep 3
        fi
    fi
    echo "Start in a GNU screen session named 'dnc'"
    screen -S dnc -d -m /dnc/dnc.sh -o
    if [ "$(screen -ls | grep netctl)" = "" ]; then
        sleep 0.2
    else
        echo "Stopping previous netctl session..."
        screen -X -S netctl quit
        sleep 3
    fi
    echo "Start in a GNU screen session named 'netctl'"
    screen -S netctl -d -m /dnc/bash/netctl-watchdog.py
else
    echo "Start in a classic shell so without the -o option"
    netctl -d -m /dnc/bash/netctl-watchdog.py &
    /dnc/dnc.sh &
fi

screen -ls

while getopts "o" opt; do
    case "$opt" in
    o)  screen -r dnc
        ;;
    esac
done

exit $?

