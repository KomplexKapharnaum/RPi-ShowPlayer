#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#
import subprocess
import time
import logging

# CONFIG
LOG_FILENAME = '/dnc/logs/netctl-watchdog.log'
SleepTimeNormal = 10        #Seconds between each check, in normal conditions
SleepTimeBad = 3            #Seconds between each check, in bad conditions
SleepTimeNone = 2           #Seconds between each check, in no signal condition
SleepTimeBroken = 5         #Seconds between each check, in no Netctl is Broken
SleepTimeNoDevice = 5        #Seconds between each check, in No Device detected
BrokenMaxTry = 3            #Number of time we retry to restart NetCtl before REBOOT
SignalTreshold = -80        #Treshold for bad signal detection
BadSigDead = 60             #Seconds before restarting for BAD SIGNAL (< SignalTreshold)
NoSigDead = 240             #Seconds before restarting for NO SIGNAL

# STATUS
S_INIT = -1
S_GOOD = 0
S_BAD = 1
S_NOSIG = 2
S_NODEV = 3

# INTERNAL VARS
DONE = False
connected = 0
mounted = 0
no_signal = 0
bad_signal = 0
sleeptime = SleepTimeNone
status = S_INIT
exec_error = 0


def log(msg):
    print "NETCTL-WATCHDOG: "+msg
    logging.info(msg)


def restart_netctl():
    global no_signal, bad_signal, sleeptime, status, exec_error, DONE
    try:
        subprocess.check_call("systemctl restart netctl-auto@wlan0.service", shell=True)
        time.sleep(10)
        no_signal = 0
        bad_signal = 0
        sleeptime = SleepTimeNone
        status = S_INIT
        exec_error = 0
    except subprocess.CalledProcessError as e:
        exec_error += 1
        if exec_error > BrokenMaxTry:
            log('ERROR too many fails while trying to restart NetCtl => Reboot !')
            DONE = True
            subprocess.check_call("reboot", shell=True)
        else:
            log('ERROR while trying to restart NetCtl {0}/{1}: {2}'.format(exec_error, BrokenMaxTry, e))
            time.sleep(SleepTimeBroken)
            restart_netctl()

    # OLD CMD: subprocess.Popen("systemctl restart netctl-auto@wlan0.service", shell=True)


def physicals():
    try:
        iwlist = subprocess.check_output("iw list", shell=True).split("\n")
        phy = []
        for line in iwlist:
            if line.startswith('Wi'):
                phy.append(line.split(' ', 1)[1])
        # log("interfaces found: {0}".format(phy))
        return phy
    except subprocess.CalledProcessError as e:
        log('ERROR while calling iw to get physical interface list: {0}'.format(e))
        return None
    # OLD CMD: return [x for x in subprocess.Popen("iw list | grep Wi", shell=True, stdout=subprocess.PIPE).stdout.read().split("\n") if x]


def devices():
    try:
        ifconfig = subprocess.check_output("ifconfig", shell=True).split("\n")
        dev = []
        for line in ifconfig:
            if line.startswith('wlan'):
                dev.append(line.split(' ', 1)[0][:-1])
        # log("devices found: {0}".format(dev))
        return dev
    except subprocess.CalledProcessError as e:
        log('ERROR while calling ifconfig to get mounted devices list: {0}'.format(e))
        return None
    # OLD CMD: return [x for x in subprocess.Popen("ifconfig | grep wlan | awk '{print $1}' | sed 's/.$//'", shell=True, stdout=subprocess.PIPE).stdout.read().split() if x]


def signal(iw='wlan0'):
    try:
        iw = subprocess.check_output("iw "+iw+" link | grep signal | awk '{print $2}'", shell=True)
        return iw
    except subprocess.CalledProcessError as e:
        log('ERROR while calling iw to get signal strength: {0}'.format(e.strerror))
        return 0
    # OLD CMD: return subprocess.Popen("iw wlan0 link | grep signal | awk '{print $2}'", shell=True, stdout=subprocess.PIPE).stdout.read()


def noDevice():
    global sleeptime, status
    sleeptime = SleepTimeNoDevice
    if status != S_NODEV:
        log('No Device ...')
        status = S_NODEV


def goodSignal(sig=None):
    global no_signal, bad_signal, sleeptime, status
    no_signal = 0
    bad_signal = 0
    sleeptime = SleepTimeNormal
    if sig is not None:
        sig = sig.strip()
    if status != S_GOOD:
        log('{0}: Signal is Good ! '.format(sig))
        status = S_GOOD


def badSignal(sig=None):
    global no_signal, bad_signal, sleeptime, status
    no_signal = 0
    bad_signal += 1
    sleeptime = SleepTimeBad
    if sig is not None:
        sig = sig.strip()
    if status != S_BAD:
        log('{0}: Signal is Bad.. (under {1})'.format(sig, SignalTreshold))
        status = S_BAD


def noSignal():
    global no_signal, bad_signal, sleeptime, status
    no_signal += 1
    sleeptime = SleepTimeNone
    if status != S_NOSIG:
        log('No Signal ...')
        status = S_NOSIG


##################
# BACKUP COPY OF PREVIOUS LOG
try:
    subprocess.check_call("cp "+LOG_FILENAME+" "+LOG_FILENAME+".bck", shell=True)
except subprocess.CalledProcessError as e:
    pass

# INIT LOG FILE
open(LOG_FILENAME, 'w').close()
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)


# START
log('STARTING Watchdog')
while not DONE:

    time.sleep(sleeptime)

    # Check mounted devices
    dev = devices()
    if dev is None:
        continue
    if mounted < len(dev):
        log('Device mounted')
    elif mounted > len(dev):
        log('Device unmounted')
        time.sleep(4)   # if just unmounted, we should wait before testing physical if
    mounted = len(dev)

    # Check physical interfaces
    phy = physicals()
    if phy is None:
        continue
    if connected < len(phy):
        log('Interface connected')
    elif connected > len(phy):
        log('Interface disconnected')
    connected = len(phy)

    # New interface to mount
    if connected > mounted:
        log('New device to mount, restart NetCTL')
        restart_netctl()

    # No Signal
    elif no_signal > (NoSigDead/SleepTimeBad):
        log('No signal for too long, restart NetCTL')
        restart_netctl()

    # Bad Signal
    elif bad_signal > (BadSigDead/SleepTimeBad):
        log('Bad signal for too long, restart NetCTL')
        restart_netctl()

    # Check Signal strength
    elif len(dev) > 0:
        for d in dev:
            pwr = signal(d)
            if pwr and int(pwr) < 0:
                if int(pwr) >= SignalTreshold:
                    goodSignal(pwr)
                    break
                else:
                    badSignal(pwr)
            else:
                noSignal()

    # No Device
    else:
        noDevice()


# EXIT
log('STOPPING Watchdog')
exit(0)
