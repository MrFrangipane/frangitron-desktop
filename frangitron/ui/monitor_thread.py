import time
from PySide2 import QtCore
from frangitron.raspberry_pi_3 import RaspberryPi3, Status


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

            # This takes at least 1s, no sleep needed
            try:
                self.updated.emit(self.raspberrypi.status())
            except Exception as e:
                import traceback
                traceback.print_exc()


def make_monitor_thread(address):
    thread = QtCore.QThread()
    monitor = Monitor(address)

    monitor.moveToThread(thread)
    thread.started.connect(monitor.run)
    thread.finished.connect(monitor.deleteLater)

    return monitor, thread
