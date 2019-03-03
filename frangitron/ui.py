from PySide2 import QtWidgets
from PySide2 import QtCore
from .ssh_raspberry_pi_3 import SSHRaspberryPi3


class Window(QtWidgets.QWidget):

    def __init__(self, address, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setWindowTitle("Frangitron Monitor - {}".format(address))

        self.usage = QtWidgets.QProgressBar()
        self.usage.setMaximum(1000)

        self.temperature = QtWidgets.QProgressBar()
        self.temperature.setMinimum(300)
        self.temperature.setMaximum(700)

        self.memory = QtWidgets.QProgressBar()

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QtWidgets.QLabel('CPU Usage'), 0, 0)
        layout.addWidget(self.usage, 0, 1)
        layout.addWidget(QtWidgets.QLabel('CPU Temperature'), 1, 0)
        layout.addWidget(self.temperature, 1, 1)
        layout.addWidget(QtWidgets.QLabel('Memory'), 2, 0)
        layout.addWidget(self.memory, 2, 1)

        self.raspberry = SSHRaspberryPi3(address)

        self._update()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

    def _update(self):
        usage = self.raspberry.cpu_usage()
        self.usage.setValue(usage * 10)
        self.usage.setFormat("{:.1f} %".format(usage))

        temperature, unit = self.raspberry.cpu_temperature()
        self.temperature.setValue(temperature * 10)
        self.temperature.setFormat("{:.1f} {}".format(temperature, unit))

        total, free = self.raspberry.memory()
        self.memory.setMaximum(total[0])
        self.memory.setValue(total[0] - free[0])
        self.memory.setFormat("%v " + total[1])
