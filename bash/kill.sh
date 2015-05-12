#!/bin/bash

killall hardware6
killall hardware7

#Kill start.sh (avoid respawn)
killall start.sh
kill $(ps -ejH w |grep start.sh |grep -v grep  | cut -d" " -f 3)
kill $(ps -ejH w |grep start.sh |grep -v grep  | cut -d" " -f 2)
kill $(ps -ejH w |grep start.sh |grep -v grep  | cut -d" " -f 1)

#Kill python
killall python2
killall python2.7

fuser -k 1782/udp
fuser -k 1781/udp
fuser -k 2782/udp
fuser -k 2781/udp

exit 0



