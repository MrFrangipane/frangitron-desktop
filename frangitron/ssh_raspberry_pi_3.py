from pexpect import pxssh, EOF


class SSHRaspberryPi3(object):
    """
    Handles SSH connexion to Raspberry Pi 3 and provides helper methods to monitor its status
    """

    def __init__(self, address, username='pi'):
        print('ssh login')
        self.connected = False
        self.cpu_count = None

        self.session = pxssh.pxssh()
        try:
            self.session.login(address, username)
            self.connected = True
            self.cpu_usage()  # Inits cpu_count
        except (EOF, pxssh.ExceptionPxssh) as e:
            pass

    def _command(self, command):
        """
        Runs a command
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

    def cpu_temperature(self):
        """
        CPU Temperature as a (value, unit) tuple (float, str)
        """
        result = self._command('cat /sys/class/thermal/thermal_zone0/temp')[-1]
        return float(result) / 1000.0, '°C'

    def cpu_usage(self):
        """
        CPU Usage as tuple of [0:100] float and a list of [0:100] float, one per core

        Example : (58.1, (57.1, 54.2, 58.6, 55.0))
        """
        info = self._command('mpstat -P ALL')
        self.cpu_count = len(info[5:])

        all = (100.0 - float(info[4].split()[-1]))
        per_cpu = [(100.0 - float(line.split()[-1])) for line in info[5:]]

        return all, per_cpu

    def memory(self):
        """
        Two (value, unit) tuples of total and free memory (int, str)
        """
        self.cpu_usage()
        info = self._command('cat /proc/meminfo')
        total = int(info[1].split()[1]), info[1].split()[2]
        free = int(info[2].split()[1]), info[2].split()[2]
        return total, free

    def ps_grep(self, name):
        """
        Performs a `ps -ef | grep "<name>"`, returns True if any process is found, False otherwise
        :param name:
        :return:
        """
        info = self._command('ps -ef | grep "{}"'.format(name))
        return len(info) > 2

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

    def __del__(self):
        if self.connected:
            print('ssh logout')
            self.session.logout()
