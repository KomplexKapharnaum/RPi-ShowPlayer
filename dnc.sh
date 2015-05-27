#!/bin/bash

if [ $(ps -ejH w | grep dnc.sh | grep -v grep | wc -l ) -eq 3 ]; then
sleep 1
echo "
                    ___                    ___           ___                                  ___                         ___           ___           ___     
     _____         /\  \                  /\  \         /\  \                                /\__\                       /\__\         /\  \         /\  \    
    /::\  \       /::\  \                 \:\  \       /::\  \         ___                  /:/  /                      /:/ _/_       /::\  \        \:\  \   
   /:/\:\  \     /:/\:\  \                 \:\  \     /:/\:\  \       /\__\                /:/  /                      /:/ /\__\     /:/\:\  \        \:\  \  
  /:/  \:\__\   /:/  \:\  \            _____\:\  \   /:/  \:\  \     /:/  /               /:/  /  ___   ___     ___   /:/ /:/ _/_   /:/ /::\  \   _____\:\  \ 
 /:/__/ \:|__| /:/__/ \:\__\          /::::::::\__\ /:/__/ \:\__\   /:/__/               /:/__/  /\__\ /\  \   /\__\ /:/_/:/ /\__\ /:/_/:/\:\__\ /::::::::\__\ 
 \:\  \ /:/  / \:\  \ /:/  /          \:\~~\~~\/__/ \:\  \ /:/  /  /::\  \               \:\  \ /:/  / \:\  \ /:/  / \:\/:/ /:/  / \:\/:/  \/__/ \:\~~\~~\/__/
  \:\  /:/  /   \:\  /:/  /            \:\  \        \:\  /:/  /  /:/\:\  \               \:\  /:/  /   \:\  /:/  /   \::/_/:/  /   \::/__/       \:\  \      
   \:\/:/  /     \:\/:/  /              \:\  \        \:\/:/  /   \/__\:\  \               \:\/:/  /     \:\/:/  /     \:\/:/  /     \:\  \        \:\  \     
    \::/  /       \::/  /                \:\__\        \::/  /         \:\__\               \::/  /       \::/  /       \::/  /       \:\__\        \:\__\    
     \/__/         \/__/                  \/__/         \/__/           \/__/                \/__/         \/__/         \/__/         \/__/         \/__/    
"
else
    echo "An instance is already running .. "$(ps -ejH w | grep dnc.sh | grep -v grep | wc -l ) > /tmp/dnc_l
    echo "EXIT because already running"
    exit 0
fi

running=1
DIRECT_INOUT=0
AUTO_START=1

# NAMED ARGUMENTS
while getopts "ou" opt; do
    case "$opt" in
    o)  DIRECT_INOUT=1
        ;;
    u)  AUTO_START=0
        ;;
    esac
done

# Wait for other process to start on boot
if ((AUTO_START)); then
    echo "= DNC Loading"
    sleep 5
fi

quit()
{
    running=0
}

kill_zombies()
{
	echo "= DNC Clear"
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
    echo ""
    echo "= DNC Update"
    /dnc/update.sh | sed -e 's/^/    /'
    cd /dnc

    # MAIN
    echo ""
	echo "= DNC Start"
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
            echo ""
            echo ""
            sleep 1
    fi
done
kill_zombies

