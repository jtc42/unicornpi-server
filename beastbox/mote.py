from pprint import pprint
import time
import logging

from mote import Mote

from beastbox.base import BaseLamp
from beastbox.utilities import hex_to_rgb, rgb_to_hex, fuzzybool


class MoteLamp(BaseLamp):
    def __init__(self, channels=4, correction=[1., 1., 1.]):

        self.mote = Mote()

        for c in range(channels):
            self.mote.configure_channel(c+1, 16, False)

        BaseLamp.__init__(self, correction=correction)

        self.channels = channels
        self.pixels = 16

        for channel in range(self.channels):
            self.mote.configure_channel(channel+1, self.pixels, False)

        self.width = self.channels
        self.height = self.pixels


    # Clear all pixels
    def clear(self):
        self.mote.clear()
        self.mote.show()

    def show(self):
        self.mote.show()

    # Set a single pixel
    def set_pixel(self, x, y, r, g, b):
        r, g, b = self.apply_correction(r, g, b)
        self.mote.set_pixel(x+1, y, r, g, b)

    # Set all pixels to RGB
    def set_all(self, r, g, b):
        self.color = (r, g, b)
        r, g, b = self.apply_correction(r, g, b)
        self.mote.set_all(r, g, b)

    # Set maximum global brightness
    def set_brightness(self, val):
        val = int(val)
        if 0 <= val <= 255:
            self.mote.set_brightness(val/255)  # Set brightness through unicornhat library
            self.brightness = val  # Log user-selected brightness to a variable
            self.mote.show()
        else:
            logging.error("Brightness must be between 0 and 255")