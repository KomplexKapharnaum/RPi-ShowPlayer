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
    ./player/Python/main.py
    exitcode=$?
    if [ exitcode -eq 2 ]; then
        quit()
        poweroff
    elif [ exitcode -eq 3 ]; then
        quit()
        reboot
    fi
    echo "ShowPlayer exited $?."
    if (( running ))
    	then
    		echo "Respawning.."
    fi
    sleep 2
done

