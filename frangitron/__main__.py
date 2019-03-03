from PySide2.QtWidgets import QApplication
from frangitron.ui import Window


if __name__ == '__main__':
    app = QApplication([])

    window = Window(address='192.168.1.14')
    window.resize(600, 100)
    window.show()

    app.exec_()
