#!/bin/bash
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
	pkill vlc
	pkill hardware-arm6
	pkill hardware-arm7
}

trap quit SIGINT

while (( running )); do
	kill_zombies
	echo "ShowPlayer Start"
    if ((DIRECT_INOUT)); then
    	./player/Python/main.py
    else
    	# mkdir -p /tmp/dnc
    	# echo '' > /tmp/dnc/stdin
    	echo '' > /dnc/logs/main.log
	./player/Python/main.py &> /dnc/logs/main.log
    	# ./player/Python/main.py < /tmp/dnc/stdin &> ./logs/main.log
    fi
    exitcode=$?
    if [ $exitcode -eq 2 ]; then
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

