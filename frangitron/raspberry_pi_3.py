import logging
from pexpect import pxssh, EOF


_FRANGITRON_COMMAND_LINE = '/home/pi/frangitron/frangitron --platform linuxfb'
_POST_COMPILE_COMMAND_LINE = './frangitron --platform linuxfb'
_IS_RUNNING_PATTERN = 'frangitron --platform linuxfb'


class Status(object):
    """
    Holds info about Frangitron's Raspberry Pi 3
    """

    def __init__(self):
        self.online = False

        self.cpu_load = 0
        self.core0_load = 0
        self.core1_load = 0
        self.core2_load = 0
        self.core3_load = 0

        self.cpu_temperature = 0, 'Unit'

        self.memory_total = 0, 'Unit'
        self.memory_used = 0, 'Unit'

        self.is_frangitron_running = False


class RaspberryPi3(object):
    """
    Handles SSH connexion to Raspberry Pi 3 and provides helper methods to monitor its status

    !!! note
        mpstat needs to be installed on the Pi
    """

    def __init__(self, address, username='pi'):
        logging.info('ssh login')
        self.connected = False
        self.cpu_count = None

        self.session = pxssh.pxssh()
        try:
            self.session.login(address, username)
            self.connected = True
            self.cpu_usage()  # Inits cpu_count
        except (EOF, pxssh.ExceptionPxssh) as e:
            pass

    def __del__(self):
        if self.connected:
            logging.info('ssh logout')
            self.session.logout()

    def _command(self, command):
        """
        Runs a command through ssh on the Pi

        :param command: string of the command to execute
        :return: whole prompt splitted in lines of strings
        """
        if not self.connected:
            raise ConnectionAbortedError('Pi is not connected')

        self.session.sendline(command)

        try:
            self.session.prompt()
        except EOF as e:
            self.connected = False
            raise ConnectionAbortedError('Pi was disconnected')

        return self.session.before.decode().splitlines()

    def _ps_grep(self, name):
        """
        Performs a `ps -ef | grep "<name>"`, returns True if any process is found, False otherwise
        """
        info = self._command('ps -ef | grep "{}"'.format(name))
        return len(info) > 2

    def _run(self, command, cwd=None, background=True):
        """
        Runs a command, returns result in splitted lines
        """
        if cwd is not None:
            self._command('cd ' + cwd)

        if background and not command.endswith('&'):
            command += ' &'

        info = self._command(command)
        return info[1:]

    def _kill(self, command):
        """
        Kills process matching given command line pattern
        """
        self._command('pkill -f "{}"'.format(command))

    #
    # Status
    def cpu_temperature(self):
        """
        CPU Temperature as a (value, unit) tuple (float, str)

        Example : (55, '°C')
        """
        result = self._command('cat /sys/class/thermal/thermal_zone0/temp')[-1]
        return float(result) / 1000.0, '°C'

    def cpu_usage(self):
        """
        CPU Usage as tuple of [0:100] float and a list of [0:100] float, one per core

        !!! warn
            This takes 1s to execute

        Example : (58.1, (57.1, 54.2, 58.6, 55.0))
        """
        data = self._command('mpstat -P ALL 1 1')
        info = data[:3]

        # Only first block of values
        for line in data[3:]:
            if not line: break
            if line:
                info.append(line)

        self.cpu_count = len(info[5:])
        try:
            all_ = (100.0 - float(info[4].split()[-1]))
            per_cpu = [(100.0 - float(line.split()[-1])) for line in info[5:]]
        except ValueError as e:
            all_ = 0.0
            per_cpu = [0.0 for _ in range(self.cpu_count)]

        return all_, per_cpu

    def memory(self):
        """
        Two (value, unit) tuples of total and used memory (int, str)

        Example : ((101557 'kB'), (51535, 'kB'))
        """
        self.cpu_usage()
        info = self._command('cat /proc/meminfo')
        total = int(info[1].split()[1]), info[1].split()[2]
        used = int(total[0] - info[2].split()[1]), info[2].split()[2]
        return total, used

    def is_running(self):
        """
        Returns True if a Frangitron process is found
        """
        return self._ps_grep(_IS_RUNNING_PATTERN)

    def status(self):
        """
        Returns a Status object

        !!! warn
            This takes a least 1s to execute
        """
        if not self.connected: return Status()

        status = Status()

        all_, per_cpu = self.cpu_usage()
        status.cpu_load = all_
        status.core0_load = per_cpu[0]
        status.core1_load = per_cpu[1]
        status.core2_load = per_cpu[2]
        status.core3_load = per_cpu[3]

        status.cpu_temperature = self.cpu_temperature()

        status.memory_total, status.memory_used = self.cpu_temperature()

        status.is_frangitron_running = self.is_running()

        return status

    #
    # Actions
    def start(self):
        """Starts the Frangitron process"""
        self._run(_FRANGITRON_COMMAND_LINE)

    def kill(self):
        """Kills the Frangitron process"""
        self._kill(_FRANGITRON_COMMAND_LINE)
        self._kill(_POST_COMPILE_COMMAND_LINE)

    def shutdown(self):
        """
        Shuts down the raspberry pi
        """
        self._command('sudo shutdown now')

    def reboot(self):
        """
        Reboots the raspberry pi
        """
        self._command('sudo reboot now')