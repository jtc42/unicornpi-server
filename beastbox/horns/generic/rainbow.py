from beastbox.horns.generic import generic

import time
import math
import colorsys as col

# TODO: A better 1D rainbow based on https://github.com/pimoroni/mote-phat/blob/master/examples/rainbow.py

class Worker(generic.Worker):

    def __init__(self, parent):

        self.speed = 0.2
        self.mode = 0

        generic.Worker.__init__(self, parent, 'rainbow')

    @property
    def state(self):

        response = {
            'dynamic_rainbow_speed': self.speed,
            'dynamic_rainbow_mode': self.mode,
        }

        return response

    def set_state(self, state_dict):
        if 'dynamic_rainbow_mode' in state_dict:
            self.mode = int(state_dict['dynamic_rainbow_mode'])

        if 'dynamic_rainbow_speed' in state_dict:
            self.speed = float(state_dict['dynamic_rainbow_speed'])

    def setup(self):
        self.i = 0.0
        self.offset = 30

    def loop(self):
        if self.mode == 0:

            self.i += self.speed

            for y in range(self.parent.height):
                for x in range(self.parent.width):
                    r = (math.cos((x+self.i)/2.0) + math.cos((y+self.i)/2.0)) * 64.0 + 128.0
                    g = (math.sin((x+self.i)/1.5) + math.sin((y+self.i)/2.0)) * 64.0 + 128.0
                    b = (math.sin((x+self.i)/2.0) + math.cos((y+self.i)/1.5)) * 64.0 + 128.0
                    r = max(0, min(255, r + self.offset))
                    g = max(0, min(255, g + self.offset))
                    b = max(0, min(255, b + self.offset))
                    self.parent.set_pixel(x, y, int(r), int(g), int(b))
            self.parent.show()
            time.sleep(0.01)
            
        elif self.mode==1:
            rgb = col.hsv_to_rgb(self.i,1,1)
            self.parent.set_all(rgb[0]*255,rgb[1]*255,rgb[2]*255)
        
            self.i += self.speed/250
            if self.i >= 1.0:
                self.i = 0.0
            time.sleep(0.01)