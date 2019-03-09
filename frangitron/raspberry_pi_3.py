import logging
from pexpect import pxssh, EOF


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
        self.cpu_count = 4
        self.session = pxssh.pxssh()
        try:
            self.session.login(address, username, login_timeout=1)
            self.connected = True
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
            return tuple()

        try:
            self.session.sendline(command)
            self.session.prompt()
        except EOF as e:
            self.connected = False
            return tuple()

        return self.session.before.decode().splitlines()

    #
    # Status
    def cpu_temperature(self):
        """
        CPU Temperature as a (value, unit) tuple (float, str)

        Example : (55, '°C')
        """
        result = self._command('cat /sys/class/thermal/thermal_zone0/temp')
        if not result:
            return 0.0, '°C'

        return float(result[-1]) / 1000.0, '°C'

    def cpu_usage(self):
        """
        CPU Usage as tuple of [0:100] float and a list of [0:100] float, one per core

        !!! warn
            This takes 1s to execute

        Example : (58.1, (57.1, 54.2, 58.6, 55.0))
        """
        data = self._command('mpstat -P ALL 1 1')
        if not data:
            all_ = 0.0
            per_cpu = [0.0 for _ in range(self.cpu_count)]
            return all_, per_cpu

        info = data[:3]

        # Only first block of values
        for line in data[3:]:
            if not line: break
            if line:
                info.append(line)

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
        info = self._command('cat /proc/meminfo')
        if not info:
            return ((0, 'kB'), (0, 'kB'))

        total = int(info[1].split()[1]), info[1].split()[2]
        used = total[0] - int(info[2].split()[1]), info[2].split()[2]
        return total, used

    def is_running(self):
        """
        Returns True if a Frangitron process is found
        """
        result = self._command('ps aux | grep "frangitron --platform linuxfb"')
        return len(result) > 2

    def status(self):
        """
        Returns a Status object

        !!! warn
            This takes a least 1s to execute
        """
        if not self.connected: return Status()
        status = Status()
        status.online = True

        all_, per_cpu = self.cpu_usage()

        status.cpu_load = all_
        status.core0_load = per_cpu[0]
        status.core1_load = per_cpu[1]
        status.core2_load = per_cpu[2]
        status.core3_load = per_cpu[3]

        status.cpu_temperature = self.cpu_temperature()

        status.memory_total, status.memory_used = self.memory()

        status.is_frangitron_running = self.is_running()

        return status

    #
    # Actions
    def start(self):
        """Starts the Frangitron service"""
        self._command("sudo systemctl start frangitron")

    def stop(self):
        """Stops the Frangitron service"""
        self._command("sudo systemctl stop frangitron")

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
