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
        self.parent.clear()  # Initial clear

    def start(self):  # Start and draw
        # If not already running
        if not self._running:
            self.parent.stop()
            self.parent.check_alarm_started()

            # Set parent mode
            self.parent.mode = self.name

            self._running = True  # Set start command
            thread = Thread(target=self.main)  # Define thread
            thread.daemon = True  # Stop this thread when main thread closes
            thread.start()  # Start thread

    def main(self):
        self.setup()
        while self._running:  # While terminate command not sent
            self.parent.check_alarm_running()  # Check alarm sequence hasn't started
            self.loop()
