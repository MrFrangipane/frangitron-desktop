import time
from PySide2 import QtCore
from frangitron.raspberry_pi_3 import RaspberryPi3, Status


INTERVAL = 2.5


class Monitor(QtCore.QObject):
    updated = QtCore.Signal(Status)

    def __init__(self, address, parent=None):
        QtCore.QObject.__init__(self, parent)

        self._is_running = False
        self.address = address
        self.raspberrypi = None

    def run(self):
        self._is_running = True

        while self._is_running:
            if self.raspberrypi is None or not self.raspberrypi.connected:
                self.raspberrypi = RaspberryPi3(self.address)

            if self.raspberrypi.connected:
                status = self.raspberrypi.status()
                self.updated.emit(status)

            time.sleep(INTERVAL)


def make_monitor_thread(address):
    thread = QtCore.QThread()
    monitor = Monitor(address)

    monitor.moveToThread(thread)
    thread.started.connect(monitor.run)
    thread.finished.connect(monitor.deleteLater)

    return monitor, thread
