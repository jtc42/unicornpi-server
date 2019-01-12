import time
import logging

from abc import ABCMeta, abstractmethod

from beastbox.horns.generic import timers
from beastbox.horns.generic import clamp
from beastbox.horns.generic import rainbow

from beastbox.utilities import hex_to_rgb, rgb_to_hex, fuzzybool


class BaseLamp:
    __metaclass__ = ABCMeta

    def __init__(self):
        # Set initially zero dimensions
        self.width, self.height = (0, 0)

        # Clean start
        self.clear()
        self.brightness = 0.0
        self.set_brightness(0.8)

        # Default mode
        self.mode = 'clamp'

        # INSTALL MODULES
        self.mods = []
        self.timers = []

        # Static
        self.clamp = clamp.Worker(self)
        self.mods.append(self.clamp)

        # Dynamic
        self.rainbow = rainbow.Worker(self)
        self.mods.append(self.rainbow)

        # INSTALL TIMER MODULES
        self.alarm = timers.AlarmWorker(self)
        self.timers.append(self.alarm)
        self.fade = timers.FadeWorker(self)
        self.timers.append(self.fade)

    # Check if any horns are running
    @property
    def running(self):
        return not(all(not(mod._running) for mod in self.mods))

    # Define StopAll function
    def stop(self):
        print("Stopping all")
        for mod in self.mods:
            mod.stop()
        if self.alarm.SequenceStarted:  # If alarm sequence has started:
            self.alarm.AlarmOverride = True  # Also kill alarm (without unsetting)
        self.clear()

    # Clear all pixels
    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def show(self):
        pass

    # Set a single pixel
    @abstractmethod
    def set_pixel(self, *args, **kwargs):
        pass

    # Set all pixels to RGB
    def set_all(self, r, g, b):
        for x in range(self.width):
            for y in range(self.height):
                self.set_pixel(x, y, int(r), int(g), int(b))
        self.show()

    # Set maximum global brightness
    @abstractmethod
    def set_brightness(self, val, sly=False):
        pass

    # Set brightness while considering running fades (part of horns.special)
    def safe_set_brightness(self, val):
        if self.fade._running:
            self.fade.stop()
        self.set_brightness(val)

    # ALARM START PROCEDURE
    def check_alarm_started(self):  # If program is not yet running, it takes priority
        if self.alarm.SequenceStarted:  # If alarm sequence has already started
            self.alarm.AlarmOverride = True  # Override alarm

            self.set_brightness(self.brightness, sly=True)  # Set brightness back to user-set brightness
            self.alarm.AlarmBrightnessSet = False  # Tell the system we're no longer using forced brightness

    def check_alarm_running(self):  # If program is already running, alarm takes priority
        if self.alarm.SequenceStarted and not self.alarm.AlarmOverride:
            self.stop()

    @property
    def state(self):
        response = {
            'global_status': self.running,
            'global_mode': self.mode,
            'global_brightness_val': int(self.brightness * 100),
        }

        for timer in self.timers:
            response.update(timer.state)

        for mod in self.mods:
            response.update(mod.state)

        return response
    
    def start_mod_from_name(self, name):
        matches = [mod for mod in self.mods if mod.name == name]

        if len(matches) == 0:
            logging.warning("No matching mods found.")

        elif len(matches) != 1:
            logging.warning("Multiple matching mods found.")

        else:
            matches[0].start()

    def set_state(self, state_dict):
        logging.debug(state_dict)

        # STATUS
        if 'global_status' in state_dict:
            if fuzzybool(state_dict['global_status']):
                self.start_mod_from_name(self.mode)
            else:
                self.stop()

        # MODE
        if 'global_mode' in state_dict:
            # If name matches a loaded mod
            if state_dict['global_mode'] in [mod.name for mod in self.mods]:
                self.mode = state_dict['global_mode']

                # If already running, switch to the new mode
                if self.running:
                    self.start_mod_from_name(self.mode)

        # BRIGHTNESS
        if 'global_brightness_val' in state_dict:
            brightness = int(state_dict['global_brightness_val'])/100.0
            self.safe_set_brightness(brightness)
        
        # MOD STATES
        for mod in self.mods:
            mod.set_state(state_dict)

        for timer in self.timers:
            timer.set_state(state_dict)
