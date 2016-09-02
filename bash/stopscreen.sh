#!/bin/sh

cd /dnc

which screen
screen=$?
if [ $screen -eq 1 ]; then
    echo "nameserver 8.8.4.4" > /etc/resolv.conf
    pacman -Sy --noconfirm screen
    screen=$?
    echo "termcapinfo xterm* ti@:te@" > ~/.screenrc
fi

if [ $screen -eq 0 ]; then
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
            sleep 0.1
        fi
    fi
    if [ "$(screen -ls | grep netctl)" = "" ]; then
        sleep 0.1
    else
        echo "Stopping previous netctl session..."
        screen -X -S netctl quit
        sleep 0.1
    fi
fi

screen -ls

sleep 1
