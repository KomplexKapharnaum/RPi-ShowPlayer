#!/bin/bash
#############################
# CONFIGURE // UPDATE
#############################
 

#############################
# Move old local settings file
#############################
mkdir -p ~/dnc_settings/
if [ -f ~/.dnc_settings.json ]; then
	mv ~/.dnc_settings.json ~/dnc_settings/develop.json
	echo "CONFIG: moved old local config file to new local settings folder"
fi
#############################


#############################
# Install ALSAequal && ALSAplugins
#############################
RPI=$(uname -m)
echo "RPI"
if [RPI != "armv6l"]; then

x=`pacman -Qs alsa-plugins`
if [ -n "$x" ];  then
    echo "ALSAplugins Installed";
else
    echo "Install ALSAplugins";
    pacman -S --noconfirm alsa-plugins
fi
x=`pacman -Qs alsaequal`
if [ -n "$x" ];  then 
    echo "ALSAequal Installed";  
else 
    echo "Install ALSAequal from AUR"; 
    cd /tmp
    wget https://aur.archlinux.org/packages/al/alsaequal/alsaequal.tar.gz --no-check-certificate
    tar -xvf alsaequal.tar.gz
    chmod 777 -R alsaequal/
    cd alsaequal
    runuser -l pi -c 'cd /tmp/alsaequal; makepkg -s'
    pacman -U alsaequal-0.6-12-armv7h.pkg.tar.xz --noconfirm
fi

else
    echo "abort install of ALSAequal on rpiA+ / B+"

fi
#############################


#############################
# Select ALSA config profile
#############################
numaudio=`cat /proc/asound/cards | grep '^ [0-9]' | wc -l`
cp /dnc/settings/asoundrc ~/.asoundrc
if [ $numaudio -eq 2 ]; then
        sed -i 's/#DUAL//g' ~/.asoundrc
        echo "AUDIO: Dual Output Internal+External"
else
        sed -i 's/#INTERNAL//g' ~/.asoundrc
	echo "AUDIO: Internal Output"
fi
#############################
