from threading import *
import time


#CORE FUNCTIONS

import horns.core as core

def quit():
    stopall()
    exit()


#CLEANING UP
core.clear()
core.setbrightness(0.8)


#GENERIC_CLASS

class ThreadClass:

    def __init__(self, initfunction, startfunction, loopfunction):
        self._running=False
        
        self.initfunction=initfunction
        self.startfunction=startfunction
        self.loopfunction=loopfunction
        
        self.initfunction(self)

    def stop(self): #Stop and clear
        self._running=False #Set terminate command
        core.clear() #Initial clear

    def start(self): #Start and draw
        stopall()
        special.ChkAlarmStart()
                        
        self._running=True #Set start command
        thread1=Thread(target=self.main) #Define thread
        thread1.daemon=True #Stop this thread when main thread closes
        thread1.start() #Start thread
        
    def main(self):
        self.startfunction(self)
        while self._running==True: #While terminate command not sent
            special.ChkAlarmRun(self) #Check alarm sequence hasn't started
            self.loopfunction(self)


#special
import horns.special as special

def safesetbrightness(val): #Set brightness while considering running fades (part of horns.special)
    if special.fade._running==True:
        special.fade.stop()
    core.setbrightness(val)


#INSTALL HORN MODULES

modlist=[]

#Static

import horns.clamp
clamp=ThreadClass(horns.clamp.init,horns.clamp.start,horns.clamp.loop)
modlist.append(clamp)

#Dynamic

import horns.rainbow
rainbow=ThreadClass(horns.rainbow.init,horns.rainbow.start,horns.rainbow.loop)
modlist.append(rainbow)

import horns.alsa
alsa=ThreadClass(horns.alsa.init,horns.alsa.start,horns.alsa.loop)
modlist.append(alsa)



#Define StopAll function

def stopall():
    for mod in modlist:    
        mod.stop()
    if special.alarm.SequenceStarted==True: #If alarm sequence has started:
		special.alarm.AlarmOverride=True #Also kill alarm (without unsetting)