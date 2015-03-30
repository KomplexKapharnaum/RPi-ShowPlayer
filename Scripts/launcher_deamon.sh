#!/bin/bash
# 



#while true; do
	while read x < $1; do
		echo "fuser -k $x/udp"
		fuser -k $x/udp
		killall python2.7
		/etc/rc.local &
	done
#done

exit 0
