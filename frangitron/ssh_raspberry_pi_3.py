from pexpect import pxssh


class SSHRaspberryPi3(object):
    """
    Handles SSH connexion to Raspberry Pi 3 and provides helper methods to monitor its status
    """

    def __init__(self, address, username='pi'):
        print('ssh login')
        self.session = pxssh.pxssh()
        self.session.login(address, username)

    def _command(self, command):
        """
        Runs a command
        :param command: string of the command to execute
        :return: whole prompt splitted in lines of strings
        """
        self.session.sendline(command)
        self.session.prompt()
        return self.session.before.decode().splitlines()

    def cpu_temperature(self):
        """
        CPU Temperature as a (value, unit) tuple (float, str)
        """
        result = self._command('cat /sys/class/thermal/thermal_zone0/temp')[-1]
        return float(result) / 1000.0, '°C'

    def cpu_usage(self):
        """
        CPU Usage as a float 0.0 - 100.0
        """
        info = self._command('top -b | head -n 5')
        cpu = info[3].split()
        idle = float(cpu[7])
        return 100.0 - idle

    def memory(self):
        """
        Two (value, unit) tuples of total and free memory (int, str)
        """
        self.cpu_usage()
        info = self._command('cat /proc/meminfo')
        total = int(info[1].split()[1]), info[1].split()[2]
        free = int(info[2].split()[1]), info[2].split()[2]
        return total, free

    def __del__(self):
        print('ssh logout')
        self.session.logout()
