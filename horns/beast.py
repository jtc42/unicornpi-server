from threading import *
import time
import logging

from . import core
from . import special

import horns.clamp
import horns.rainbow
import horns.alsa


def hex_to_rgb(value):
    h = value.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def rgb_to_hex(rgb):
    rgb=tuple(rgb)
    return '%02x%02x%02x' % rgb

class BeastLamp:
    def __init__(self):
        # Clean start
        core.clear()
        core.setbrightness(0.8)

        # Default mode
        self.mode = 'clamp'

        # INSTALL HORN MODULES
        self.modlist = []

        # Static
        self.clamp = horns.clamp.Worker(self)
        self.modlist.append(self.clamp)

        # Dynamic
        self.rainbow = horns.rainbow.Worker(self)
        self.modlist.append(self.rainbow)

        self.alsa = horns.alsa.Worker(self)
        self.modlist.append(self.alsa)

        # INSTALL SPECIAL MODULES
        self.alarm = special.AlarmWorker(self)
        self.fade = special.FadeWorker(self)

    # Check if any horns are running
    @property
    def running(self):
        return not(all(not(mod._running) for mod in self.modlist))

    # Define StopAll function
    def stop(self):
        print("Stopping all")
        for mod in self.modlist:
            mod.stop()
        if self.alarm.SequenceStarted:  # If alarm sequence has started:
            self.alarm.AlarmOverride = True  # Also kill alarm (without unsetting)
        core.clear()

    # Set brightness while considering running fades (part of horns.special)
    def safesetbrightness(self, val):
        if self.fade._running:
            self.fade.stop()
        core.setbrightness(val)

    # ALARM START PROCEDURE
    def ChkAlarmStart(self):  # If program is not yet running, it takes priority
        if self.alarm.SequenceStarted:  # If alarm sequence has already started
            self.alarm.AlarmOverride = True  # Override alarm

            unicorn.brightness(core.user_brightness)  # Set brightness back to user-set brightness
            self.alarm.AlarmBrightnessSet = False  # Tell the system we're no longer using forced brightness

    def ChkAlarmRun(self):  # If program is already running, alarm takes priority
        if self.alarm.SequenceStarted and not self.alarm.AlarmOverride:
            self.stop()

    # PROPERTIES
    @property
    def brightness(self):
        return core.getbrightness() * 100

    @property
    def state(self):
        response = {
            'global_status': self.running,
            'global_mode': self.mode,
            'global_brightness_val': int(core.getbrightness() * 100),
            'static_clamp_hex': str(rgb_to_hex(self.clamp.rgb)),
            'dynamic_rainbow_speed': self.rainbow.speed,
            'dynamic_rainbow_mode': self.rainbow.mode,
            'special_fade_status': self.fade._running,
            'special_fade_minutes': self.fade.fademins,
            'special_fade_target': self.fade.scalefinal,
            'special_alarm_status': self.alarm._running,
            'special_alarm_time': str(self.alarm.h) + ':' + str(self.alarm.m) + ':' + str(self.alarm.s),
            'special_alarm_lead': self.alarm.leadmin,
            'special_alarm_tail': self.alarm.outmin,
            'special_alarm_active': self.alarm.SequenceStarted
        }

        response.update(self.alsa.state)

        return response
    
    def start_mod_from_name(self, name):
        matches = [mod for mod in self.modlist if mod.name == name]

        if len(matches) == 0:
            logging.warning("No matching mods found.")

        elif len(matches) != 1:
            logging.warning("Multiple matching mods found.")

        else:
            matches[0].start()

    def set_state(self, state_dict):
        # STATUS
        if 'global_status' in state_dict:
            if state_dict['global_status'] == True:
                self.start_mod_from_name(self.mode)
            else:
                self.stop()

        # MODE
        if 'global_mode' in state_dict:
            # If name matches a loaded mod
            if state_dict['global_mode'] in [mod.name for mod in self.modlist]:
                self.mode = state_dict['global_mode']

                # If already running, switch to the new mode
                if self.running:
                    self.start_mod_from_name(self.mode)

        # BRIGHTNESS
        if 'global_brightness_val' in state_dict:
            brightness = int(state_dict['global_brightness_val'])/100.0
            self.safesetbrightness(brightness)
        
        # CLAMP
        if 'static_clamp_hex' in state_dict:
            rgb = hex_to_rgb(state_dict['static_clamp_hex'])
            if all(c<=255 for c in rgb):  # If all values are within RGB range
                self.clamp.rgb = rgb  # Update colour


        # RAINBOW
        if 'dynamic_rainbow_mode' in state_dict:
            self.rainbow.mode = int(state_dict['dynamic_rainbow_mode'])

        if 'dynamic_rainbow_speed' in state_dict:
            self.rainbow.speed = float(state_dict['dynamic_rainbow_speed'])

        # ALSA
        if self.alsa.enabled:
            if 'dynamic_alsa_mode' in state_dict:
                self.alsa.colormode = int(state_dict['dynamic_alsa_mode'])
            
            if 'dynamic_alsa_monitor' in state_dict:
                self.alsa.micmix.setvolume(int(state_dict['dynamic_alsa_monitor']))

            if 'dynamic_alsa_volume' in state_dict:
                self.alsa.volmix.setvolume(int(state_dict['dynamic_alsa_volume']))

            if 'dynamic_alsa_sensitivity' in state_dict:
                self.alsa.multiplier = float(state_dict['dynamic_alsa_sensitivity'])

        # FADE
        if 'special_fade_status' in state_dict:
            status = bool(state_dict['special_fade_status'])
            if status and not self.fade._running:
                self.fade.start()
            elif not status and self.fade._running:
                self.fade.stop()

        if 'special_fade_minutes' in state_dict:
            self.fade.fademins = int(state_dict['special_fade_minutes'])
        
        if 'special_fade_target' in state_dict:
            self.fade.scalefinal = float(state_dict['special_fade_target'])

        # ALARM
        if 'special_alarm_status' in state_dict:
            status = bool(state_dict['special_alarm_status'])
            if status and not self.alarm._running:
                self.alarm.start()
            elif not status and self.alarm._running:
                self.alarm.stop()
        
        if 'special_alarm_lead' in state_dict:
            self.alarm.leadmin = int(state_dict['special_alarm_lead'])
        
        if 'special_alarm_tail' in state_dict:
            self.alarm.outmin = int(state_dict['special_alarm_tail'])
        
        if 'special_alarm_time' in state_dict:
            # Split string into list
            time = str(state_dict['special_alarm_time']).split(":")
            if len(time) >= 2:
                self.alarm.h = int(time[0])
                self.alarm.m = int(time[1])
            else:
                logging.warning("Invalid time code.")