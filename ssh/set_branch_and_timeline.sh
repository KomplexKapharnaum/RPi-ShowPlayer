WORKED="yes"
echo "Change branch to @1 and timeline to @2"
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
rm ~/.dnc_settings.json
echo "{
	\"current_timeline\": \"@2\"
}" > ~/.dnc_settings.json
if [ $? -ne 0 ]; then 
WORKED="no";
fi
tar -cf /root/auto_change_save__active.tar /dnc/scenario/__active
if [ $? -ne 0 ]; then 
	WORKED="no";
	echo "Do on .. ERROR DURRING SAVING __ACTIVE DIR"
else
	rm /dnc/scenario/__active/*
fi
tar -cf /root/auto_change_save_@2.tar /dnc/scenario/@2
if [ "@2" = "" ]; then
	echo "do not remove empty 2 arg"
else
	rm -rf /dnc/scenario/@2
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
if [ "@3" = "start" ]; then
	echo "Auto start .."
	/dnc/start.sh
elif [ "@3" = "reboot" ]; then
	echo "Reboot in 1 sec..."
	sleep 1
	reboot
else
	echo "Do not auto start"
fi

