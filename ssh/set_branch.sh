WORKED="yes"
echo "Change branch to @1 "
cd /dnc
git fetch --all
if [ $? -ne 0 ]; then
WORKED="no";
fi
git checkout @1
if [ $? -ne 0 ]; then
WORKED="no";
fi
git pull
if [ $? -ne 0 ]; then
WORKED="no";
fi
which screen
if [ $? -eq 1 ]; then
    echo "nameserver 8.8.4.4" > /etc/resolv.conf
    pacman -Sy --noconfirm screen
    screen=$?
    if [ $screen -ne 0 ]; then
	WORKED="no";
	fi
    echo "termcapinfo xterm* ti@:te@" > ~/.screenrc
fi
if [ "$WORKED" = "yes" ]; then
	echo "Do on .. OK for this device !"
fi
if [ "@2" = "start" ]; then
	echo "Auto start .."
	/dnc/start.sh
elif [ "@2" = "reboot" ]; then
	echo "Reboot in 1 sec..."
	sleep 1
	reboot
else
	echo "Do not auto start"
fi

