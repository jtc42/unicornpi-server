import time
import logging
from pprint import pprint

from abc import ABCMeta, abstractmethod

from beastbox.utilities import hex_to_rgb, rgb_to_hex, fuzzybool, apply_correction


class BaseLamp:
    __metaclass__ = ABCMeta

    def __init__(self, correction=[1., 1., 1.]):
        # Set initially zero dimensions
        self.width, self.height = (0, 0)

        self.correction = correction

        self.brightness = 255
        self.state = False
        self.color = (255, 0, 255)

        # Clean start
        self.clear()
        self.set_brightness(self.brightness)
        self.set_state(self.state)
        self.set_color(self.color)

        # Colour correction
        self.correction = correction

    # Apply correction
    def apply_correction(self, r, g, b):
        corrected = [apply_correction(val, contrast) for val, contrast in zip([r, g, b], self.correction)]
        return corrected

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

    # Set brightness (0-255)
    @abstractmethod
    def set_brightness(self, val):
        pass

    # Set on/off
    def set_state(self, state):
        state = fuzzybool(state)
        if state:
            self.set_all(*self.color)
            self.show()
        else:
            self.clear()
            self.show()
        self.state = bool(state)

    # Set RGB color
    def set_color(self, color):
        color = [int(c) for c in color]
        if not len(color) == 3:
            logging.error("color must be a 3-element list (r, g, b)")
        else:
            self.set_all(*color)
            self.color = color
        
        # If lamp is on, update
        if self.state:
            self.show()

    def get_representation(self):
        return {
            "state": self.state,
            "color": self.color,
            "brightness": self.brightness
        }

    def set_representation(self, rep):
        pprint(rep)
        if "state" in rep:
            self.set_state(rep.get("state"))
        if "brightness" in rep:
            self.set_brightness(rep.get("brightness"))
        if "color" in rep:
            self.set_color(rep.get("color"))