from threading import Thread
import unicornhat as unicorn
import numpy as np

import datetime
import time
from . import core


#ALARM

class AlarmWorker:
    # Set this alarms override to initially false    
    AlarmOverride = False

    # Assume brightness is user-set, not alarms forced brightness
    AlarmBrightnessSet = False 
    
    # Initial sequence started
    SequenceStarted = False
    
    # Set lead-in time
    leadmin = 60 # Minutes
    leadsec = leadmin*60 # Lead in converted to seconds
    
    # Set lead-out time
    outmin = 20 # Minutes
    outsec = outmin*60 # Lead in converted to seconds
    
    # Declare fade in and fadeout
    linearfade = 0 
    linearfadeout = 0
    
    
    # Choose alarm time
    h = 7
    m = 0
    s = 0
    

    # Define initial now
    now=datetime.datetime.now()
    
    # Define initial alarm time string (for web display)
    timestring=str(h).zfill(2)+':'+str(m).zfill(2)
    
    # Define initial alarm datetime
    alarmdt=datetime.datetime(now.year, now.month, now.day, h, m, s)

    # Define initial alarm start time (alarm time minus lead in time)
    alarmstart = alarmdt - datetime.timedelta(minutes=leadmin)
    

    def __init__(self):
        self._running = False

    def stop(self): # Stop and clear
        self._running = False # Set terminate command
        self.AlarmOverride = False
        self.SequenceStarted = False
                        
        core.clear() # Clear, maybe not necesarry, but safe

    def start(self): # Start and draw
        if self._running == True:
            self.stop()
        self._running = True # Set start command
                        
        altimerthread = Thread(target=self.control) # Define thread
        aldrawthread = Thread(target=self.draw) # Define thread
        altimerthread.daemon = True
        aldrawthread.daemon = True
        altimerthread.start() # Start thread
        aldrawthread.start() # Start thread
            
    def control(self): # Control method
        
        now = datetime.datetime.now() # Set initial now
        
        while self._running == True: # While terminate command not sent
        
            self.timestring = str(self.h).zfill(2)+':'+str(self.m).zfill(2)
            
            now = datetime.datetime.now() # Set new current time
            
            self.alarmdt = datetime.datetime(now.year, now.month, now.day, self.h, self.m, self.s)
            self.alarmstart = self.alarmdt - datetime.timedelta(minutes=self.leadmin)
    
            self.secstoalarm = (self.alarmdt-now).seconds # Seconds left until alarm sounds
            
            self.secssincealarm = (now-self.alarmdt).seconds # Seconds since alarm sounded

            self.leadsec = self.leadmin*60 # Define new lead time
            self.outsec = self.outmin*60  # Define new out time
    
            if self.secstoalarm<=self.leadsec: # If lead in has begun
                self.SequenceStarted=True
                self.linearfade = (self.leadsec-self.secstoalarm)/float(self.leadsec) 
                self.linearfade = np.clip(self.linearfade,0,1) #Safety
                    
            elif self.secssincealarm<=self.outsec: # Or if the time is way before the lead in, if the time since the alarm is within the lead out
                self.linearfadeout = (self.outsec-self.secssincealarm)/float(self.outsec)
                self.linearfadeout = np.clip(self.linearfadeout,0,1) # Safety

            elif self.secssincealarm>self.outsec and self.secstoalarm>self.leadsec: # If neither within lead in or lead out
                self.linearfade = 0 # Reset fades
                self.linearfadeout = 0
                self.SequenceStarted=False # Flag sequence as not running
                self.AlarmOverride=False # Reset override

            time.sleep(1)


    def draw(self): # Draw method
   
        while self._running == True:
            
            if self._running == True and self.AlarmOverride == False and self.SequenceStarted == True: # While terminate command not sent
                    
                if self.secstoalarm<=self.leadsec: # If lead in has begun
                        
                    # Temperature range from 1500K to 3600K
                    alarmtemp = 2100*self.linearfade + 1500 # Change with linearfade

                    core.setall(self.linearfade*core.temptorgb(alarmtemp)[0], self.linearfade*core.temptorgb(alarmtemp)[1], self.linearfade*core.temptorgb(alarmtemp)[2])
                    unicorn.show()
                        
                elif self.secssincealarm <= self.outsec:
                       
                    core.setall(self.linearfadeout*core.temptorgb(3600)[0], self.linearfadeout*core.temptorgb(3600)[1], self.linearfadeout*core.temptorgb(3600)[2])
                    unicorn.show()

                # After first changing colours
                unicorn.brightness(0.8) # Force brightness to 0.8 without changing user-set brightness
                self.AlarmBrightnessSet=True # Tell the system we are using the forced brightness
            
            else: # If alarm draw is not running for any reason (not time or overridden)
                if self.AlarmBrightnessSet == True: # If we are currently using the forced brightness
                    unicorn.brightness(core.user_brightness) # Set brightness back to user-set brightness
                    self.AlarmBrightnessSet = False # Tell the system we're no longer using forced brightness
                                    
            time.sleep(1)

alarm = AlarmWorker()


#ALARM START PROCEDURE
def ChkAlarmStart(): # If program is not yet running, it takes priority
    global alarm
    if alarm.SequenceStarted == True: # If alarm sequence has already started
        alarm.AlarmOverride = True # Override alarm

        unicorn.brightness(core.user_brightness) # Set brightness back to user-set brightness
        alarm.AlarmBrightnessSet = False # Tell the system we're no longer using forced brightness

def ChkAlarmRun(self): # If program is already running, alarm takes priority
    global alarm
    if alarm.SequenceStarted==True and alarm.AlarmOverride == False:
        self.stop()


#FADER

class FadeWorker:

    fademins = 2
    fadesecs = fademins*60.0

    scalefinal = 0.0 # Target brightness

    t = 0 # Initial time? Damnit past-Joel, why do you not comment stuff?
    
    
    global alarm
    stopbrightscale = core.user_brightness # Reset brightness to user-defined when fade stops
    
    def __init__(self):
        self._running = False


    def stop(self): # Stop and clear
        self._running = False # Set terminate command

        core.setbrightness(self.stopbrightscale) # Sets the brightness slider to the fader brightness stopped at, regardless of stop method


    def start(self): # Start and draw
        ChkAlarmStart()

        self.t = 0
                        
        self._running = True # Set start command
        fadethread = Thread(target=self.main) # Define thread
        fadethread.daemon = True # Stop this thread when main thread closes
        fadethread.start() # Start thread


    def main(self):
        while self._running == True: #While terminate command not sent

            self.fadesecs = self.fademins*60.0

            if alarm.SequenceStarted == True:
                self.stop()

            elif self.t <= self.fadesecs: # If fade is still running
                brightinitial = float(core.user_brightness)
                brightfinal = float(self.scalefinal*brightinitial)

                brightness = brightinitial-(self.t/float(self.fadesecs))*(brightinitial-brightfinal)

                #Sets the current "stopping value" for setbrightness
                self.stopbrightscale = brightness
                
                unicorn.brightness(brightness) # Force brightness without changing user-set brightness

                self.t+=1
                time.sleep(1)

            elif self.t>self.fadesecs:
                self.stop()
        
fade=FadeWorker()
