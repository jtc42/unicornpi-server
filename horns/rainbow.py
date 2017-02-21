import unicornhat as unicorn
import core

import time
import math
import colorsys as col

def init(self):

    self.speed=0.2
    self.mode=0


def start(self):
    
    self.i = 0.0
    self.offset = 30
    
    
def loop(self):

    if self.mode==0:
        self.i += self.speed
        for y in range(8):
            for x in range(8):
                r = (math.cos((x+self.i)/2.0) + math.cos((y+self.i)/2.0)) * 64.0 + 128.0
                g = (math.sin((x+self.i)/1.5) + math.sin((y+self.i)/2.0)) * 64.0 + 128.0
                b = (math.sin((x+self.i)/2.0) + math.cos((y+self.i)/1.5)) * 64.0 + 128.0
                r = max(0, min(255, r + self.offset))
                g = max(0, min(255, g + self.offset))
                b = max(0, min(255, b + self.offset))
                unicorn.set_pixel(x,y,int(r),int(g),int(b))
        unicorn.show()
        time.sleep(0.01)
        
    elif self.mode==1:
        rgb=col.hsv_to_rgb(self.i,1,1)
        core.setall(rgb[0]*255,rgb[1]*255,rgb[2]*255)
    
        self.i += self.speed/250
        if self.i>=1.0:
            self.i=0.0
        time.sleep(0.01)