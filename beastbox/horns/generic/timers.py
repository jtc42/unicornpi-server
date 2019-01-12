from threading import Thread
import numpy as np
import logging
import datetime
import time

from beastbox.utilities import temptorgb, fuzzybool

# ALARM

class AlarmWorker:

    def __init__(self, parent):
        # Basic setup
        self._running = False
        self.parent = parent

        # Specific setup
        # Set this alarms override to initially false
        self.AlarmOverride = False
        # Assume brightness is user-set, not alarms forced brightness
        self.AlarmBrightnessSet = False
        # Initial sequence started
        self.SequenceStarted = False

        # Set lead-in time
        self.leadmin = 60  # Minutes
        self.leadsec = self.leadmin * 60  # Lead in converted to seconds

        # Set lead-out time
        self.outmin = 20  # Minutes
        self.outsec = self.outmin * 60  # Lead in converted to seconds

        # Declare fade in and fadeout
        self.linearfade = 0
        self.linearfadeout = 0

        # Choose alarm time
        self.h = 7
        self.m = 0
        self.s = 0

        # Define initial now
        self.now = datetime.datetime.now()

        # Define initial alarm time string (for web display)
        self.timestring = str(self.h).zfill(2) + ':' + str(self.m).zfill(2)
        # Define initial alarm datetime
        self.alarmdt = datetime.datetime(self.now.year, self.now.month, self.now.day, self.h, self.m, self.s)
        # Define initial alarm start time (alarm time minus lead in time)
        self.alarmstart = self.alarmdt - datetime.timedelta(minutes=self.leadmin)

    @property
    def state(self):

        response = {
            'special_alarm_status': self._running,
            'special_alarm_time': str(self.h) + ':' + str(self.m) + ':' + str(self.s),
            'special_alarm_lead': self.leadmin,
            'special_alarm_tail': self.outmin,
            'special_alarm_active': self.SequenceStarted
        }

        return response

    def set_state(self, state_dict):
        if 'special_alarm_status' in state_dict:
            status = fuzzybool(state_dict['special_alarm_status'])
            if status and not self._running:
                self.start()
            elif not status and self._running:
                self.stop()
        
        if 'special_alarm_lead' in state_dict:
            self.leadmin = int(state_dict['special_alarm_lead'])
        
        if 'special_alarm_tail' in state_dict:
            self.outmin = int(state_dict['special_alarm_tail'])
        
        if 'special_alarm_time' in state_dict:
            # Split string into list
            time = str(state_dict['special_alarm_time']).split(":")
            if len(time) >= 2:
                self.h = int(time[0])
                self.m = int(time[1])
            else:
                logging.warning("Invalid time code.")

    def stop(self):  # Stop and clear
        self._running = False  # Set terminate command
        self.AlarmOverride = False
        self.SequenceStarted = False

        self.parent.clear()  # Clear, maybe not necesarry, but safe

    def start(self):  # Start and draw
        if self._running:
            self.stop()
        self._running = True  # Set start command

        altimerthread = Thread(target=self.control)  # Define thread
        aldrawthread = Thread(target=self.draw)  # Define thread
        altimerthread.daemon = True
        aldrawthread.daemon = True
        altimerthread.start()  # Start thread
        aldrawthread.start()  # Start thread

    def control(self):  # Control method

        now = datetime.datetime.now()  # Set initial now

        while self._running:  # While terminate command not sent

            self.timestring = str(self.h).zfill(2) + ':' + str(self.m).zfill(2)

            now = datetime.datetime.now()  # Set new current time

            self.alarmdt = datetime.datetime(now.year, now.month, now.day, self.h, self.m, self.s)
            self.alarmstart = self.alarmdt - datetime.timedelta(minutes=self.leadmin)

            self.secstoalarm = (self.alarmdt - now).seconds  # Seconds left until alarm sounds

            self.secssincealarm = (now - self.alarmdt).seconds  # Seconds since alarm sounded

            self.leadsec = self.leadmin * 60  # Define new lead time
            self.outsec = self.outmin * 60  # Define new out time

            if self.secstoalarm <= self.leadsec:  # If lead in has begun
                self.SequenceStarted = True
                self.linearfade = (self.leadsec - self.secstoalarm) / float(self.leadsec)
                self.linearfade = np.clip(self.linearfade, 0, 1)  # Safety

            elif self.secssincealarm <= self.outsec:  # Or if the time is way before the lead in, if the time since the alarm is within the lead out
                self.linearfadeout = (self.outsec - self.secssincealarm) / float(self.outsec)
                self.linearfadeout = np.clip(self.linearfadeout, 0, 1)  # Safety

            elif self.secssincealarm > self.outsec and self.secstoalarm > self.leadsec:  # If neither within lead in or lead out
                self.linearfade = 0  # Reset fades
                self.linearfadeout = 0
                self.SequenceStarted = False  # Flag sequence as not running
                self.AlarmOverride = False  # Reset override

            time.sleep(1)

    def draw(self):  # Draw method

        while self._running:

            if self._running and not self.AlarmOverride and self.SequenceStarted:  # While terminate command not sent

                if self.secstoalarm <= self.leadsec:  # If lead in has begun

                    # Temperature range from 1500K to 3600K
                    alarmtemp = 2100 * self.linearfade + 1500  # Change with linearfade

                    self.parent.set_all(
                        self.linearfade * temptorgb(alarmtemp)[0],
                        self.linearfade * temptorgb(alarmtemp)[1],
                        self.linearfade * temptorgb(alarmtemp)[2]
                    )
                    self.parent.show()

                elif self.secssincealarm <= self.outsec:

                    self.parent.set_all(
                        self.linearfadeout * temptorgb(3600)[0],
                        self.linearfadeout * temptorgb(3600)[1],
                        self.linearfadeout * temptorgb(3600)[2]
                    )
                    self.parent.show()

                # After first changing colours
                self.parent.set_brightness(0.8, sly=True)  # Force brightness to 0.8 without changing user-set brightness
                self.AlarmBrightnessSet = True  # Tell the system we are using the forced brightness

            else:  # If alarm draw is not running for any reason (not time or overridden)
                if self.AlarmBrightnessSet:  # If we are currently using the forced brightness
                    self.parent.set_brightness(self.parent.brightness, sly=True)  # Set brightness back to user-set brightness
                    self.AlarmBrightnessSet = False  # Tell the system we're no longer using forced brightness

            time.sleep(1)


# FADER

class FadeWorker:

    def __init__(self, parent):
        # Basic setup
        self._running = False
        self.parent = parent

        # Specific setup
        self.fademins = 2
        self.fadesecs = self.fademins * 60.0
        self.scalefinal = 0.0  # Target brightness
        self.t = 0  # Initial time? Damnit past-Joel, why do you not comment stuff?
        self.stopbrightscale = self.parent.brightness  # Reset brightness to user-defined when fade stops

    @property
    def state(self):

        response = {
            'special_fade_status': self._running,
            'special_fade_minutes': self.fademins,
            'special_fade_target': self.scalefinal,
        }

        return response

    def set_state(self, state_dict):
        if 'special_fade_status' in state_dict:
            status = fuzzybool(state_dict['special_fade_status'])
            if status and not self._running:
                self.start()
            elif not status and self._running:
                self.stop()

        if 'special_fade_minutes' in state_dict:
            self.fademins = int(state_dict['special_fade_minutes'])
        
        if 'special_fade_target' in state_dict:
            self.scalefinal = float(state_dict['special_fade_target'])

    def stop(self):  # Stop and clear
        self._running = False  # Set terminate command

        self.parent.set_brightness(self.stopbrightscale)  # Sets the brightness slider to the fader brightness stopped at, regardless of stop method

    def start(self):  # Start and draw
        self.parent.check_alarm_started()

        self.t = 0

        self._running = True  # Set start command
        fadethread = Thread(target=self.main)  # Define thread
        fadethread.daemon = True  # Stop this thread when main thread closes
        fadethread.start()  # Start thread

    def main(self):
        while self._running:  # While terminate command not sent

            self.fadesecs = self.fademins * 60.0

            if self.parent.alarm.SequenceStarted:
                self.stop()

            elif self.t <= self.fadesecs:  # If fade is still running
                brightinitial = float(self.parent.brightness)
                brightfinal = float(self.scalefinal * brightinitial)

                brightness = brightinitial - (self.t / float(self.fadesecs)) * (brightinitial - brightfinal)

                # Sets the current "stopping value" for setbrightness
                self.stopbrightscale = brightness

                self.parent.set_brightness(brightness, sly=True)  # Force brightness without changing user-set brightness

                self.t += 1
                time.sleep(1)

            elif self.t > self.fadesecs:
                self.stop()
