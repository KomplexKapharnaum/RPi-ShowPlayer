#!/bin/bash

kxkm_fs_config_rw

MAC=$(ip link|grep wlan0 -A 1|grep link/ether|cut -d" " -f 6|sed s/://g)

cd /var/lib/connman

cp -a wifi_e8de271d6bd4_6b786b6d444e43_managed_none wifi_"$MAC"_6b786b6d444e43_managed_none
sed -i "s/e8de271d6bd4/$MAC/g" wifi_"$MAC"_6b786b6d444e43_managed_none/settings

cp -a wifi_e8de271d6bd4_6b786b6d4c5445_managed_none wifi_"$MAC"_6b786b6d4c5445_managed_none
sed -i "s/e8de271d6bd4/$MAC/g" wifi_"$MAC"_6b786b6d4c5445_managed_none/settings

kxkm_fs_config_ro
kxkm_fs_root_rw

#unlink /etc/connman/kxkmDNC
#ln -s /var/lib/connman/wifi_e8de271d6bd4_6b786b6d444e43_managed_none/settings /etc/connman/kxkmDNC

kxkm_fs_root_ro

exit 0

