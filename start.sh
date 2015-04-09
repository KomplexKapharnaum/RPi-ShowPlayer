#!/bin/bash
running=1

quit()
{
    running=0
}

trap quit SIGINT

while (( running )); do
	sudo fuser -k 1781/udp
	sudo pkill vlc && sudo pkill hardware
	echo "ShowPlayer Start"
    /dnc/player/Python/run-show.py
    echo "ShowPlayer exited $?."
    if (( running ))
    	then
    		echo "Respawning.."
    fi
    sleep 2
done

