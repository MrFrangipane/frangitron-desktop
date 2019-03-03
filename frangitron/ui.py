from PySide2 import QtWidgets
from PySide2 import QtCore
from .ssh_raspberry_pi_3 import SSHRaspberryPi3
from . import desktop_computer


_INTERVAL = 2.5
_CSS = """
QProgressBar::chunk { width: 1px; }
QProgressBar { text-align: center; }
"""


class Window(QtWidgets.QWidget):

    def __init__(self, address, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setWindowTitle("Frangitron Monitor - {}".format(address))
        self.setStyleSheet(_CSS)

        self.raspberry = SSHRaspberryPi3(address)
        if not self.raspberry.connected: return

        #
        ## Widgets

        self.usage = list()
        for i in range(self.raspberry.cpu_count + 1):
            new_progess_bar = QtWidgets.QProgressBar()
            new_progess_bar.setMaximum(1000)

            if i == 0:
                new_progess_bar.setStyleSheet("QProgressBar::chunk { background-color: grey; }")

            self.usage.append(new_progess_bar)

        self.temperature = QtWidgets.QProgressBar()
        self.temperature.setMinimum(100)
        self.temperature.setMaximum(700)

        self.memory = QtWidgets.QProgressBar()

        layout = QtWidgets.QGridLayout(self)

        for i in range(self.raspberry.cpu_count + 1):
            layout.addWidget(QtWidgets.QLabel('CPU Usage {}'.format(i)), i, 0)
            layout.addWidget(self.usage[i], i, 1)

        self.process_running = QtWidgets.QCheckBox('frangitron')
        self.process_running.setEnabled(False)

        self.commit_message = QtWidgets.QLineEdit()
        self.commit_message.setText('<commit message>')
        self.push = QtWidgets.QPushButton('Push and compile')
        self.push.clicked.connect(self._push_compile)

        self.shutdown = QtWidgets.QPushButton('Shutdown')
        self.shutdown.clicked.connect(self._shutdown)

        #
        ## Layout

        layout.addWidget(QtWidgets.QLabel(''), self.raspberry.cpu_count + 1, 0)

        layout.addWidget(QtWidgets.QLabel('CPU Temperature'), self.raspberry.cpu_count + 2, 0)
        layout.addWidget(self.temperature, self.raspberry.cpu_count + 2, 1)

        layout.addWidget(QtWidgets.QLabel(''), self.raspberry.cpu_count + 3, 0)

        layout.addWidget(QtWidgets.QLabel('Memory'), self.raspberry.cpu_count + 4, 0)
        layout.addWidget(self.memory, self.raspberry.cpu_count + 4, 1)

        layout.addWidget(QtWidgets.QLabel(''), self.raspberry.cpu_count + 5, 0)

        layout.addWidget(QtWidgets.QLabel('Running'), self.raspberry.cpu_count + 6, 0)
        layout.addWidget(self.process_running, self.raspberry.cpu_count+ 6, 1)

        layout.addWidget(QtWidgets.QLabel(''), self.raspberry.cpu_count + 7, 0)

        layout.addWidget(self.push, self.raspberry.cpu_count + 8, 0)
        layout.addWidget(self.commit_message, self.raspberry.cpu_count + 8, 1)

        layout.addWidget(self.shutdown, self.raspberry.cpu_count + 9, 0)

        self._update()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(int(_INTERVAL * 1000))

    def _update(self):
        if not self.raspberry.connected:
            return

        try:
            all, per_core = self.raspberry.cpu_usage()
            values = [all] + per_core
            for i, usage in enumerate(self.usage):
                usage.setValue(values[i] * 10)
                usage.setFormat("{:.1f} %".format(values[i]))

            temperature, unit = self.raspberry.cpu_temperature()
            self.temperature.setValue(temperature * 10)
            self.temperature.setFormat("{:.1f} {}".format(temperature, unit))

            total, free = self.raspberry.memory()
            self.memory.setMaximum(total[0])
            self.memory.setValue(total[0] - free[0])
            self.memory.setFormat("%v " + total[1])

            self.process_running.setChecked(self.raspberry.ps_grep('frangitron --platform'))

        except ConnectionAbortedError as e:
            pass

    def _shutdown(self):
        self.raspberry.shutdown()

    def _push_compile(self):
        desktop_computer.push_and_compile(self.commit_message.text())
