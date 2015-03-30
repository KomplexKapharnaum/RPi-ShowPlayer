#!/bin/bash
# This script kill the current DNC scenario manager and relaunch rc.local
# $1 : classicport
# $2 : ackport

killall python2.7
fuser -k $1/udp
fuser -k $2/udp

/etc/rc.local &

exit 0
