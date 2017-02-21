import core
import time

def init(self):

    self.rgb=[200,0,255]
    self.temp=2800 #Partially redundant. Only used in web frontend, and used badly


def start(self):
    
    pass


def loop(self):

    core.setall(self.rgb[0],self.rgb[1],self.rgb[2])
    time.sleep(0.1)