from pprint import pprint
import time
import logging

from mote import Mote

from beastbox.base import BaseLamp
from beastbox.utilities import hex_to_rgb, rgb_to_hex, fuzzybool


class MoteLamp(BaseLamp):
    def __init__(self, channels=4, vertical=False, correction=[1., 1., 1.]):

        self.mote = Mote()

        for c in range(channels):
            self.mote.configure_channel(c+1, 16, False)

        BaseLamp.__init__(self)

        self.channels = channels
        self.pixels = 16

        self.correction = correction

        for channel in range(self.channels):
            self.mote.configure_channel(channel+1, self.pixels, False)

        self.vertical = vertical

        if self.vertical:
            self.width = self.channels
            self.height = self.pixels

        else:
            self.width = self.channels * self.pixels
            self.height = 1

    # Apply correction
    def apply_correction(self, r, g, b):
        return [a*b for a, b in zip(self.correction, [r, g, b])]

    # Clear all pixels
    def clear(self):
        self.mote.clear()
        self.mote.show()

    def show(self):
        self.mote.show()

    # Set a single pixel
    def set_pixel(self, x, y, r, g, b):
        r, g, b = self.apply_correction(r, g, b)
        if self.vertical:
            self.mote.set_pixel(x, y, r, g, b)
        else:
            channel = x//self.pixels
            pixel = x%self.pixels
            self.mote.set_pixel(channel, pixel, r, g, b)

    # Set all pixels to RGB
    def set_all(self, r, g, b):
        r, g, b = self.apply_correction(r, g, b)
        self.mote.set_all(r, g, b)
        self.show()

    # Set maximum global brightness
    def set_brightness(self, val, sly=False):
        if 0 <= val <= 1:
            self.mote.set_brightness(val)  # Set brightness through unicornhat library
            if not sly:  # If we're not setting the brightness silently/on-the-sly
                self.brightness = val  # Log user-selected brightness to a variable
                self.mote.show()
        else:
            print("Brightness must be between 0 and 1")
