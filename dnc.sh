#!/bin/bash

if [ $(ps -ejH w | grep dnc.sh | grep -v grep | wc -l ) -eq 3 ]; then
    echo "DNC starter begin .."
else
    echo "An instance is already running .. "$(ps -ejH w | grep dnc.sh | grep -v grep | wc -l ) > /tmp/dnc_l
    echo "EXIT because already running"
    exit 0
fi


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
	echo "Kill zombies"
	#/dnc/bash/kill.sh
	pkill python2
	#Free sockets
	fuser -k 1783/udp
	fuser -k 1782/udp
	fuser -k 1781/udp
	fuser -k 2782/udp
	fuser -k 2781/udp
	#Remove others
	pkill vlc
	pkill hplayer-vlc
	pkill hardware6
	pkill hardware7
}

trap quit SIGINT

while (( running )); do
	kill_zombies

    # Maintenance
    echo "Run Update / Maintenance"
    /dnc/update.sh
    cd /dnc

    # MAIN
	echo "ShowPlayer Start"
    if ((DIRECT_INOUT)); then
    	nice -n -20 ./player/Python/main.py
    else
        # MAIN PROGRAM
        echo "."; sleep 1; echo "."; sleep 1; echo "."
    	mkdir -p /tmp/dnc
    	touch /tmp/dnc/main.log
	    nice -n -20 ./player/Python/main.py &> /tmp/dnc/main.log

    fi
    exitcode=$?
    if [ $exitcode -eq 0 ]; then
        quit
    elif [ $exitcode -eq 2 ]; then
        sleep 7     # Time for threads and others things to quit properly
        quit
        poweroff
    elif [ $exitcode -eq 3 ]; then
        sleep 7     # Time for threads and others things to quit properly
        quit
        reboot
    fi
    echo "ShowPlayer exited $exitcode"
    if (( running )); then
    		echo "Respawning.."
    fi
    sleep 1
done
kill_zombies

