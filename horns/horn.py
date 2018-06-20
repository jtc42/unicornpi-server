from . import core
from . import beast
from . import special
from threading import Thread

def override_warning():
    print("This should be overridden by the horn!")

#GENERIC_CLASS
class Worker:
    # GENERIC INIT
    def __init__(self):
        print("Setting {}._running".format(self))
        self._running = False

    # HORN METHODS
    def setup(self):
        override_warning()
    
    def loop(self):
        override_warning()

    # GENERIC METHODS
    def stop(self): #Stop and clear
        self._running = False #Set terminate command
        core.clear() #Initial clear

    def start(self): #Start and draw
        beast.stopall()
        special.ChkAlarmStart()
                        
        self._running = True #Set start command
        thread = Thread(target=self.main) #Define thread
        thread.daemon = True #Stop this thread when main thread closes
        thread.start() #Start thread
        
    def main(self):
        self.setup()
        while self._running==True: #While terminate command not sent
            special.ChkAlarmRun(self) #Check alarm sequence hasn't started
            self.loop()