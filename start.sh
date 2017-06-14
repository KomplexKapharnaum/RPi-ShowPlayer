#!/bin/bash
# Raplace old start.sh to avoid changing rc.local
# This script run old start.sh (now dnc.sh) on a detached GNU screen session

####TEMP
#bash /dnc/change_mac.sh
###


which screen
screen=$?
if [ $screen -eq 1 ]; then       # There isn't the GNU screen binary, try to install it
    echo "nameserver 8.8.4.4" > /etc/resolv.conf
    pacman -Sy --noconfirm screen
    screen=$?
    echo "termcapinfo xterm* ti@:te@" > ~/.screenrc
fi

USER_START=0
while getopts "o" opt; do
    case "$opt" in
    o)  USER_START=1
        ;;
    esac
done

if [ $screen -eq 0 ]; then      # There is the GNU screen binary
    echo "Using GNU screen.."
    
    # DNC Already Running
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
            sleep 5
            pkill python2
        fi
    fi

    # DNC Start
    echo "Start in a GNU screen session named 'dnc'"
    if ((USER_START)); then
        screen -S dnc -d -m /dnc/dnc.sh -o -u
    else
        screen -S dnc -d -m /dnc/dnc.sh -o
    fi

#    # NETCTL-WD Already Running
#    if [ "$(screen -ls | grep netctl)" = "" ]; then
#        sleep 0.2
#    else
#        echo "Stopping previous netctl session..."
#        screen -X -S netctl quit
#        sleep 3
#    fi

#    # NETCTL-WD Start
#    echo "Start in a GNU screen session named 'netctl'"
#    screen -S netctl -d -m /dnc/bash/netctl-watchdog-connman.py

else
    echo "Start in a classic shell so without the -o option"
#    /dnc/bash/netctl-watchdog.py &
    /dnc/dnc.sh &
fi

screen -ls

if ((USER_START)); then
    screen -r dnc
fi

exit $?

