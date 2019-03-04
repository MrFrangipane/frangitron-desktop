from PySide2 import QtWidgets
from frangitron.raspberry_pi_3 import RaspberryPi3, Status
from frangitron import desktop_computer


_CSS = """
QProgressBar::chunk { width: 1px; }
QProgressBar { text-align: center; }
"""
_INTERVAL = 2.5


class Window(QtWidgets.QWidget):

    def __init__(self, address, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setWindowTitle("Frangitron Monitor - {}".format(address))
        self.setStyleSheet(_CSS)

        self.raspberry = RaspberryPi3(address)
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
        self.temperature.setMinimum(200)
        self.temperature.setMaximum(800)

        self.memory = QtWidgets.QProgressBar()

        self.process_running = QtWidgets.QCheckBox('frangitron')
        self.process_running.setEnabled(False)

        self.commit_message = QtWidgets.QLineEdit()
        self.commit_message.setText('<commit message>')
        self.push = QtWidgets.QPushButton('Push and compile')
        self.push.clicked.connect(self._push_compile)

        self.start = QtWidgets.QPushButton('Start Frangitron')
        self.start.clicked.connect(self._start)

        self.kill = QtWidgets.QPushButton('Kill Frangitron')
        self.kill.clicked.connect(self._kill)

        self.reboot = QtWidgets.QPushButton('Reboot Pi')
        self.reboot.clicked.connect(self._reboot)

        self.shutdown = QtWidgets.QPushButton('Shutdown Pi')
        self.shutdown.clicked.connect(self._shutdown)

        self.offline_label = QtWidgets.QLabel('Frangitron is offline ({})'.format(address))
        self.offline_label.setStyleSheet("background-color: red; color: white; padding: 5px 5px 5px 5px")
        self.offline_label.setVisible(False)

        #
        ## Layout
        layout = QtWidgets.QGridLayout(self)

        for i in range(self.raspberry.cpu_count + 1):
            if i == 0:
                layout.addWidget(QtWidgets.QLabel('CPU Usage'), i, 0)
            else:
                layout.addWidget(QtWidgets.QLabel('Core {}'.format(i)), i, 0)
            layout.addWidget(self.usage[i], i, 1)

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

        buttons = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addWidget(self.start)
        buttons_layout.addWidget(self.kill)
        buttons_layout.addWidget(self.reboot)
        buttons_layout.addWidget(self.shutdown)
        layout.addWidget(buttons, self.raspberry.cpu_count + 9, 0, 1, 2)

        layout.addWidget(self.offline_label, self.raspberry.cpu_count + 10, 0, 1, 2)

        #
        # Monitor
        self._status_update(Status())

    #
    # Slots
    def _status_update(self, status):
        """
        Updates the Ui, given a Status object
        """
        self.setEnabled(status.online)
        self.offline_label.setVisible(not status.online)

        self.usage[0].setValue(status.cpu_load * 10)
        self.usage[0].setFormat("{:.1f} %".format(status.cpu_load))
        self.usage[1].setValue(status.core0_load * 10)
        self.usage[1].setFormat("{:.1f} %".format(status.core0_load))
        self.usage[2].setValue(status.core1_load * 10)
        self.usage[2].setFormat("{:.1f} %".format(status.core1_load))
        self.usage[3].setValue(status.core2_load * 10)
        self.usage[3].setFormat("{:.1f} %".format(status.core2_load))
        self.usage[4].setValue(status.core3_load * 10)
        self.usage[4].setFormat("{:.1f} %".format(status.core3_load))

        temperature, unit = status.cpu_temperature
        self.temperature.setValue(temperature * 10)
        self.temperature.setFormat("{:.1f} {}".format(temperature, unit))

        self.memory.setMaximum(status.memory_total[0])
        self.memory.setValue(status.memory_used[0])
        self.memory.setFormat(" ".join([str(i) for i in status.memory_used]))

        self.process_running.setChecked(status.is_frangitron_running)

    def _start(self):
        return self.raspberry.start()

    def _kill(self):
        self.raspberry.kill()

    def _reboot(self):
        self.raspberry.reboot()

    def _shutdown(self):
        self.raspberry.shutdown()

    def _push_compile(self):
        desktop_computer.push_and_compile(self.commit_message.text())
