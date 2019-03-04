from PySide2 import QtCore
from frangitron.raspberry_pi_3 import RaspberryPi3


class Monitor(object):

    def __init__(self, address):
        self.raspberrypi = RaspberryPi3(address=address)

    def run(self):


def make_monitor_thread(address):
    thread = QtCore.QThread()
    monitor = Monitor(address)

    return thread, monitor