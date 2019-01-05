from . import core
from . import special
from threading import Thread


def override_warning():
    print("This should be overridden by the horn!")


# GENERIC_CLASS
class Worker:
    # GENERIC INIT
    def __init__(self, parent, name):
        print("Attaching to parent {}".format(parent))
        self.parent = parent

        self.name = name

        print("Setting {}._running".format(self.name))
        self._running = False

    # HORN METHODS
    def setup(self):
        override_warning()

    def loop(self):
        override_warning()

    # GENERIC METHODS
    def stop(self):  # Stop and clear
        self._running = False  # Set terminate command
        core.clear()  # Initial clear

    def start(self):  # Start and draw
        self.parent.stop()
        self.parent.ChkAlarmStart()

        # Set parent mode
        self.parent.mode = self.name

        self._running = True  # Set start command
        thread = Thread(target=self.main)  # Define thread
        thread.daemon = True  # Stop this thread when main thread closes
        thread.start()  # Start thread

    def main(self):
        self.setup()
        while self._running:  # While terminate command not sent
            self.parent.ChkAlarmRun()  # Check alarm sequence hasn't started
            self.loop()
