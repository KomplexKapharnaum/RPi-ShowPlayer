#!/bin/bash
fuser -k 1781/udp
fuser -k 1782/udp
pkill vlc
pkill hplayer-vlc
pkill hardware

