import time
import logging

import unicornhat as unicorn

from beastbox.base import BaseLamp


class UnicornLamp(BaseLamp):
    def __init__(self, correction=[1., 1., 1.]):

        BaseLamp.__init__(self, correction=correction)

        unicorn.set_layout(unicorn.AUTO)
        unicorn.rotation(0)

        # Get LED matrix dimensions
        self.width, self.height = unicorn.get_shape()

    # Clear all pixels
    def clear(self):
        unicorn.off()

    def show(self):
        unicorn.show()

    # Set a single pixel
    def set_pixel(self, x, y, r, g, b):
        r, g, b = self.apply_correction(r, g, b)
        unicorn.set_pixel(x, y, r, g, b)

    # Set all pixels
    def set_all(self, r, g, b):
        self.color = (r, g, b)
        r, g, b = self.apply_correction(r, g, b)
        unicorn.set_all(r, g, b)

    # Set brightness
    def set_brightness(self, val):
        val = int(val)
        if 0 <= val <= 255:
            unicorn.brightness(val/255)  # Set brightness through unicornhat library
            self.brightness = val  # Log user-selected brightness to a variable
            unicorn.show()
        else:
            logging.error("Brightness must be between 0 and 255")
