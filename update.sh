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
# Install ALSAequal
#############################
x=`pacman -Qs alsaequal`
if 
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
#############################


#############################
# Select ALSA config profile
#############################
numaudio=`cat /proc/asound/cards | grep '^ [0-9]' | wc -l`
cp /dnc/settings/asoundrc ~/.asoundrc
if [ $numaudio -eq 2 ]; then
        sed -i 's/slave internal/slave both/g' ~/.asoundrc
        echo "AUDIO: Dual Output Internal+External"
else
        echo "AUDIO: Internal Output"
fi
#############################
