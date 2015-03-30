#!/bin/sh
# This script recompile libc for the current arch and place them

## To avoid ZIP_FALSE ERROR ?
date 0830145008.00
##

cd $1 # Goto the Lib dir

## RTPLIB
cd rtplib
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/rtplib.so ../../Python/libc/
cd ../

## ACKLIB
cd acklib
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/acklib.so ../../Python/libc/
cd ../

## PYHASHXX
cd pyhashxx
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/pyhashxx.so ../../Python/libc/
cd ../

## SUBPROCESS32 POPEN
cd subprocess32
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/* ../../Python/libc/
cd ../


## SIMPLEJSON
cd simplejson
rm -rf *.o *.so build
python2.7 setup.py build
cp -a build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/simplejson ../../Python/libc/
cd ../


## SPILIB
#cd spilib
#rm -rf *.o *.so build
#python2.7 setup.py build
#cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/spilib.so ../../Python/libc/
#cd ../

