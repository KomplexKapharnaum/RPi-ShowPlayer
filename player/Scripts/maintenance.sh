#!/bin/bash
#############################
# MAINTENANCE // UPDATE
#############################
echo "MAINTENANCE" 

#############################
# Move old local settings file
#############################
mkdir -p ~/dnc_settings/
if [ -f ~/.dnc_settings.json ]; then
    if [ ! -f ~/dnc_settings/develop.json ]; then
        mv ~/.dnc_settings.json ~/dnc_settings/develop.json
    else
        rm ~/.dnc_settings.json
    fi
fi
#############################


#############################
# Install ALSAequal
#############################
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
#############################