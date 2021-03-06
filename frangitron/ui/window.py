from PySide2 import QtWidgets
from frangitron.raspberry_pi_3 import RaspberryPi3, Status, Throttled
from .monitor_thread import make_monitor_thread
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

        self.address = address
        self.throttled = dict()

        #
        ## Widgets
        self.usage = list()
        for i in range(5):
            new_progess_bar = QtWidgets.QProgressBar()
            new_progess_bar.setMaximum(1000)

            if i == 0:
                new_progess_bar.setStyleSheet("QProgressBar::chunk { background-color: grey; }")

            self.usage.append(new_progess_bar)

        self.temperature = QtWidgets.QProgressBar()
        self.temperature.setMinimum(200)
        self.temperature.setMaximum(800)

        self.memory = QtWidgets.QProgressBar()
        self.memory.setInvertedAppearance(True)

        self.process_running = QtWidgets.QCheckBox('frangitron')
        self.process_running.setEnabled(False)

        self.recordings_destination = QtWidgets.QLineEdit()
        self.recordings_destination.setText('/home/frangi/frangitron/recordings')
        self.get_recordings = QtWidgets.QPushButton('Get recordings')
        self.get_recordings.clicked.connect(self._get_recordings)

        self.commit_message = QtWidgets.QLineEdit()
        self.commit_message.setText('<commit message>')
        self.push = QtWidgets.QPushButton('Push and compile')
        self.push.clicked.connect(self._push_compile)

        self.start = QtWidgets.QPushButton('Start service')
        self.start.clicked.connect(self._start)

        self.stop = QtWidgets.QPushButton('Stop service')
        self.stop.clicked.connect(self._stop)

        self.reboot = QtWidgets.QPushButton('Reboot Pi')
        self.reboot.clicked.connect(self._reboot)

        self.shutdown = QtWidgets.QPushButton('Shutdown Pi')
        self.shutdown.clicked.connect(self._shutdown)

        self.online_status = QtWidgets.QLabel('Connecting...')

        #
        ## Layout
        layout = QtWidgets.QGridLayout(self)

        for i in range(5):
            if i == 0:
                layout.addWidget(QtWidgets.QLabel('CPU Usage'), i, 0)
            else:
                layout.addWidget(QtWidgets.QLabel('Core {}'.format(i)), i, 0)
            layout.addWidget(self.usage[i], i, 1)

        layout.addWidget(QtWidgets.QLabel(''), 5, 0)

        layout.addWidget(QtWidgets.QLabel('CPU Temperature'), 6, 0)
        layout.addWidget(self.temperature, 6, 1)

        layout.addWidget(QtWidgets.QLabel(''), 7, 0)

        layout.addWidget(QtWidgets.QLabel('Memory Available'), 8, 0)
        layout.addWidget(self.memory, 8, 1)

        layout.addWidget(QtWidgets.QLabel(''), 9, 0)

        layout.addWidget(QtWidgets.QLabel('Running'), 10, 0)
        layout.addWidget(self.process_running, 10, 1)

        layout.addWidget(QtWidgets.QLabel(''), 11, 0)

        throttled = QtWidgets.QWidget()
        throttled_layout = QtWidgets.QVBoxLayout(throttled)
        throttled_layout.setContentsMargins(0, 0, 0, 0)
        for name in Throttled().__dict__.keys():
            new_checkbox = QtWidgets.QCheckBox(name)
            new_checkbox.setEnabled(False)
            throttled_layout.addWidget(new_checkbox)
            self.throttled[name] = new_checkbox
        layout.addWidget(QtWidgets.QLabel('Throttled'), 12, 0, 1, 2)
        layout.addWidget(throttled, 12, 1, 1, 2)

        layout.addWidget(QtWidgets.QLabel(), 13, 0)

        layout.addWidget(self.get_recordings, 14, 0)
        layout.addWidget(self.recordings_destination, 14, 1)

        layout.addWidget(self.push, 15, 0)
        layout.addWidget(self.commit_message, 15, 1)

        buttons = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addWidget(self.start)
        buttons_layout.addWidget(self.stop)
        buttons_layout.addWidget(self.reboot)
        buttons_layout.addWidget(self.shutdown)
        layout.addWidget(buttons, 16, 0, 1, 2)

        layout.addWidget(self.online_status, 17, 0, 1, 2)

        #
        # Monitor
        self.monitor, self.monitor_thread = make_monitor_thread(self.address)
        self.monitor.updated.connect(self._status_update)
        self.monitor_thread.start()

        self._status_update(Status())

    #
    # Slots
    def _status_update(self, status):
        """
        Updates the Ui, given a Status object
        """
        self.setEnabled(status.online)
        if status.online:
            self.online_status.setText('Frangitron is online ({})'.format(self.address))
            self.online_status.setStyleSheet("background-color: green; color: white; padding: 5px 5px 5px 5px")
        else:
            self.online_status.setText('Frangitron is offline ({})'.format(self.address))
            self.online_status.setStyleSheet("background-color: red; color: white; padding: 5px 5px 5px 5px")

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
        self.memory.setFormat(
            " ".join([str(i) for i in status.memory_used])
            + ' / ' +
            " ".join([str(i) for i in status.memory_total])
        )

        self.process_running.setChecked(status.is_frangitron_running)

        for name, value in status.throttled.__dict__.items():
            self.throttled[name].setChecked(value)

    def _start(self):
        raspberry = RaspberryPi3(self.address)
        if raspberry.connected:
            return raspberry.start()

    def _stop(self):
        raspberry = RaspberryPi3(self.address)
        if raspberry.connected:
            raspberry.stop()

    def _reboot(self):
        raspberry = RaspberryPi3(self.address)
        if raspberry.connected:
            raspberry.reboot()

    def _shutdown(self):
        raspberry = RaspberryPi3(self.address)
        if raspberry.connected:
            raspberry.shutdown()

    def _push_compile(self):
        desktop_computer.push_and_compile(self.commit_message.text())

    def _get_recordings(self):
        desktop_computer.retrieve_recordings(self.address, 'pi', self.recordings_destination.text())
