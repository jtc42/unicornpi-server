from horns.generic import generic
from horns.utilities import rgb_to_hex, hex_to_rgb

import time

class Worker(generic.Worker):

    def __init__(self, parent):

        self.rgb = [200,0,255]
        self.temp = 2800 #Partially redundant. Only used in web frontend, and used badly

        generic.Worker.__init__(self, parent, 'clamp')

    def setup(self):
        pass

    @property
    def state(self):

        response = {
            'static_clamp_hex': str(rgb_to_hex(self.rgb))
        }

        return response

    def set_state(self, state_dict):
        if 'static_clamp_hex' in state_dict:
            rgb = hex_to_rgb(state_dict['static_clamp_hex'])
            if all(c<=255 for c in rgb):  # If all values are within RGB range
                self.rgb = rgb  # Update colour

    def loop(self):
        self.parent.set_all(self.rgb[0],self.rgb[1],self.rgb[2])
        time.sleep(0.1)