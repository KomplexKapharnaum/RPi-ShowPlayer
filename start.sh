#!/bin/bash

./bash/kill.sh

running=1
DIRECT_INOUT=0

# NAMED ARGUMENTS
while getopts "o" opt; do
    case "$opt" in
    o)  DIRECT_INOUT=1
        ;;
    esac
done

quit()
{
    running=0
}

kill_zombies()
{
	fuser -k 1781/udp
	fuser -k 1782/udp
	fuser -k 8080/tcp
	fuser -k 8080/udp
	pkill vlc
	pkill hardware-arm6
	pkill hardware-arm7
}

trap quit SIGINT

while (( running )); do
	kill_zombies
	echo "ShowPlayer Start"
    if ((DIRECT_INOUT)); then
    	renice -n -20 ./player/Python/main.py
    else
        echo "wait before start"
        sleep 15
    	mkdir -p /tmp/dnc
    	# echo '' > /tmp/dnc/stdin
    	touch /tmp/dnc/main.log
	    renice -n -20 ./player/Python/main.py &> /tmp/dnc/main.log
    	# ./player/Python/main.py < /tmp/dnc/stdin &> ./logs/main.log
    fi
    exitcode=$?
    if [ $exitcode -eq 0 ]; then
        echo "Exiting ... POWEROFF == 0"
        break
    elif [ $exitcode -eq 2 ]; then
        quit
        poweroff
    elif [ $exitcode -eq 3 ]; then
        quit
        reboot
    fi
    echo "ShowPlayer exited $exitcode"
    if (( running ))
    	then
    		echo "Respawning.."
    fi
    sleep 2
done
kill_zombies

