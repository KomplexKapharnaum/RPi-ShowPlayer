#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#
import subprocess
import time
import logging

LOG_FILENAME = '/dnc/logs/netctl-watchdog.log'
open(LOG_FILENAME, 'w').close()
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

SleepTimeNormal = 30	    #Seconds between each check, in normal conditions
SleepTimeBad = 2			#Seconds between each check, in bad conditions
SignalTreshold = -80		#Treshold for bad signal detection
BadSigDead = 60				#Seconds before restarting for BAD SIGNAL (< SignalTreshold)
NoSigDead = 240				#Seconds before restarting for NO SIGNAL

DONE=False
connected=0
mounted=0
no_signal=0
bad_signal=0
sleeptime=SleepTimeNormal

def log(msg):
	print "NETCTL-WATCHDOG: "+msg
	logging.info(msg)
	

def restart_netctl():
	global no_signal, bad_signal, sleeptime
	subprocess.Popen("systemctl restart netctl-auto@wlan0.service", shell=True)      # TODO replace POPEN by check_output to avoid defunct
	time.sleep(15)
	no_signal=0
	bad_signal=0
	sleeptime=SleepTimeNormal
	
def physicals():    # TODO replace POPEN by check_output to avoid defunct
	return [x for x in subprocess.Popen("iw list | grep Wi", shell=True, stdout=subprocess.PIPE).stdout.read().split("\n") if x]
	
def devices():      # TODO replace POPEN by check_output to avoid defunct
	return [x for x in subprocess.Popen("ifconfig | grep wlan | awk '{print $1}' | sed 's/.$//'", shell=True, stdout=subprocess.PIPE).stdout.read().split() if x]

def goodSignal():
	global no_signal, bad_signal, sleeptime
	no_signal=0
	bad_signal=0
	sleeptime=SleepTimeNormal
	#log('good signal')
	
def badSignal():
	global no_signal, bad_signal, sleeptime
	no_signal=0
	bad_signal+=1
	sleeptime=SleepTimeBad
	#log('bad signal')
	
def noSignal():
	global no_signal, bad_signal, sleeptime
	no_signal+=1
	sleeptime=SleepTimeBad
	#log('no signal')


log('STARTING Watchdog')
while not DONE:

	time.sleep(sleeptime)
	
	phy = physicals()
	dev = devices()
	
	# Check physical interfaces
	if connected < len(phy):
		log('interface connected')
	elif connected > len(phy):
		log('interface disconnected')
	connected = len(phy)
	
	# Check mounted devices
	if mounted < len(dev):
		log('device mounted')
	elif mounted > len(dev):
		log('device unmounted')	
		# refresh physicals
		time.sleep(4)
		phy = physicals()
		connected = len(phy)
	mounted = len(dev)
	
	# Restart Netctl to mount new interfaces
	if connected > mounted:
		log('new device to mount, restart NetCTL')
		restart_netctl()
		
	# No Signal
	elif no_signal > (NoSigDead/SleepTimeBad):
		log('no signal for too long, restart NetCTL')
		#log('{0} {1}'.format(bad_signal, (BadSigDead/SleepTimeBad)))
		restart_netctl()
		
	# Bad Signal
	elif bad_signal > (BadSigDead/SleepTimeBad):
		log('bad signal for too long, restart NetCTL')
		restart_netctl()
		
	# Check SIGNAL
	else:
		for d in dev:
			signal = subprocess.Popen("iw wlan0 link | grep signal | awk '{print $2}'", shell=True, stdout=subprocess.PIPE).stdout.read()  # TODO replace POPEN by check_output to avoid defunct
			if signal and int(signal) < 0:
				if int(signal) >= SignalTreshold:
					goodSignal()
				else:
					badSignal()
			else:
				noSignal()
	
exit(0)

