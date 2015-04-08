#!/bin/bash
running=1

quit()
{
    running=0
}

trap quit SIGINT

while (( running )); do
	echo "ShowPlayer Start"
    /dnc/player/Python/run-show.py
    echo "ShowPlayer exited $?."
    if (( running ))
    	then
    		echo "Respawning.."
    fi
    sleep 2
done

