from threading import *
import time

from . import core
from . import special

# CORE FUNCTIONS
def quit():
    stopall()
    exit()

# CLEANING UP
core.clear()
core.setbrightness(0.8)

# Set brightness while considering running fades (part of horns.special)
def safesetbrightness(val):  
    if special.fade._running==True:
        special.fade.stop()
    core.setbrightness(val)

#INSTALL HORN MODULES
modlist=[]

#Static
import horns.clamp
clamp = horns.clamp.Worker()
modlist.append(clamp)

#Dynamic
import horns.rainbow
rainbow = horns.rainbow.Worker()
modlist.append(rainbow)

import horns.alsa
alsa = horns.alsa.Worker()
modlist.append(alsa)


# Define StopAll function
def stopall():
    print("Stopping all")
    for mod in modlist:    
        mod.stop()
    if special.alarm.SequenceStarted==True: #If alarm sequence has started:
        special.alarm.AlarmOverride=True #Also kill alarm (without unsetting)