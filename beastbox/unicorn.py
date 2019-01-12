from pprint import pprint
import time
import logging

import unicornhat as unicorn

from beastbox.base import BaseLamp
from beastbox.utilities import hex_to_rgb, rgb_to_hex, fuzzybool

from beastbox.horns.unicorn import alsa


class UnicornLamp(BaseLamp):
    def __init__(self):

        BaseLamp.__init__(self)

        unicorn.set_layout(unicorn.AUTO)
        unicorn.rotation(0)

        # Get LED matrix dimensions
        self.width, self.height = unicorn.get_shape()

        # Add specific mods
        self.alsa = alsa.Worker(self)
        self.mods.append(self.alsa)


    # Clear all pixels
    def clear(self):
        unicorn.off()

    def show(self):
        unicorn.show()

    # Set a single pixel
    def set_pixel(self, *args, **kwargs):
        unicorn.set_pixel(*args, **kwargs)

    # Set maximum global brightness
    def set_brightness(self, val, sly=False):
        if 0 <= val <= 1:
            unicorn.brightness(val)  # Set brightness through unicornhat library
            if not sly:  # If we're not setting the brightness silently/on-the-sly
                self.brightness = val  # Log user-selected brightness to a variable
                unicorn.show()
        else:
            print("Brightness must be between 0 and 1")
