#!/bin/bash

# Change HOSTNAME
#################

#Get current hostname
hostn=$(cat /etc/hostname)

#Ask for new hostname $newhost
echo "Enter new hostname (empty to ignore): "
read newhost

if [ -n "$newhost" ]; then
	#change hostname in /etc/hosts & /etc/hostname
	sudo sed -i "s/$hostn/$newhost/g" /etc/hosts
	sudo sed -i "s/$hostn/$newhost/g" /etc/hostname

	#display new hostname
	echo "The new will be is $newhost"
	echo ""
fi

# Change STATIC IP
##################
echo "Enter new static ip (empty to ignore): "
read newip

if [ -n "$newip" ]; then
	#change static IP in netctl profiles
	grep -l "Address=" /etc/netctl/profile_* | xargs sed -i "s/Address=\b\([0-9]\{1,3\}\.\)\{1,3\}[0-9]\{1,3\}\b/Address=$newip/g"

	#display new hostname
	echo "The new static IP will be $newip"
	echo ""
fi


# Install dependencies
######################

# TODO


# Check if /dnc exist : clone it or update
#################################
if [ ! -d "/dnc" ]; then
	git clone git@github.com:KomplexKapharnaum/RPi-ShowPlayer.git /dnc
fi

cd /dnc
echo "Choose branch (empty to ignore): "
read newbranch
if [ -n "$newbranch" ]; then
	git checkout $newbranch
fi
git pull

# Recompile embedded components
###############################
cd /dnc/player/Libs
./recompile.sh ./


# Reboot
########
echo ""
if [ -n "$newhost" ]; then
	echo "The new static HostName will be $newhost"
fi
if [ -n "$newip" ]; then
	echo "The new static IP will be $newip"
fi
if [ -n "$newbranch" ]; then
	branch=`git branch | grep \*`
	echo "Project in branch $branch"
fi
echo ""
echo "Reboot ? [y/n] "
read newip
sudo reboot
