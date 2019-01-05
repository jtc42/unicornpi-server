from . import core
from . import horn

import time

class Worker(horn.Worker):

    def __init__(self, parent):

        self.rgb = [200,0,255]
        self.temp = 2800 #Partially redundant. Only used in web frontend, and used badly

        horn.Worker.__init__(self, parent, 'clamp')

    def setup(self):
        pass

    def loop(self):
        core.setall(self.rgb[0],self.rgb[1],self.rgb[2])
        time.sleep(0.1)