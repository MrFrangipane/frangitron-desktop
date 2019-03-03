from time import sleep
from frangitron import SSHRaspberryPi3


if __name__ == '__main__':
    frangitron = SSHRaspberryPi3('192.168.1.14')

    while True:
        temp, temp_unit = frangitron.cpu_temperature()
        mem_total, meme_free = frangitron.memory()

        print("Temperature {}{} | Memory total : {} {} free : {} {}".format(
            temp, temp_unit,
            *mem_total,
            *meme_free
        ))

        sleep(5)
