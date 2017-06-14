#!/bin/sh
# This script recompile libs for the current arch and place them

## To avoid ZIP_FALSE ERROR ?
date 0830145008.00
##

cd $1 # Goto the Lib dir

## RTPLIB
cd rtplib
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/rtplib.so ../../Python/libs/
cd ../

## ACKLIB
cd acklib
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/acklib.so ../../Python/libs/
cd ../

## PYHASHXX
cd pyhashxx
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/pyhashxx.so ../../Python/libs/
cd ../

## SUBPROCESS32 POPEN
cd subprocess32
rm -rf *.o *.so build
python2.7 setup.py build
cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/* ../../Python/libs/
cd ../


## SIMPLEJSON
cd simplejson
rm -rf *.o *.so build
python2.7 setup.py build
cp -a build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/simplejson ../../Python/libs/
cd ../


## SPILIB
#cd spilib
#rm -rf *.o *.so build
#python2.7 setup.py build
#cp build/lib.linux-$(lscpu | grep Architecture | cut -d":" -f 2 | sed -e 's/^[ \t]*//')-2.7/spilib.so ../../Python/libs/
#cd ../


