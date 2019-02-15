import os
import sys

from PyQt5 import QtWidgets, QtGui

from db import RobotsDB
from mainwindow import Ui_MainWindow

db = RobotsDB('home.me', 'ext', 'Qw123456_')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.button_add_battery.clicked.connect(self.add_battery)
        self.ui.button_add_dive.clicked.connect(self.add_dive)
        self.ui.button_add_robot.clicked.connect(self.add_robot)
        self.ui.button_edit_battery.clicked.connect(self.edit_battery)
        self.ui.button_edit_dive.clicked.connect(self.edit_dive)
        self.ui.button_edit_robot.clicked.connect(self.edit_robot)

    def add_battery(self):
        pass

    def add_dive(self):
        pass

    def add_robot(self):
        pass

    def edit_battery(self):
        pass

    def edit_dive(self):
        pass

    def edit_robot(self):
        pass

    def reload(self):
        self.ui.statusbar.showMessage("Connecting to {} as {}...".format(db.host, db.username))
        db.connect()
        self.load_robots()
        self.ui.statusbar.showMessage("Connected", 5000)
        self.load_batteries()
        self.load_dives()
        self.resize_tables()

    def load_robots(self):
        table = self.ui.table_robots
        data = db.get_robots()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            for col, (cn, v) in enumerate(r.items()):
                item = QtWidgets.QTableWidgetItem('{}'.format(v))
                table.setItem(row, col, item)

    def load_batteries(self):
        table = self.ui.table_batteries
        data = db.get_batteries()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            for col, (cn, v) in enumerate(r.items()):
                item = QtWidgets.QTableWidgetItem('{}'.format(v))
                table.setItem(row, col, item)

    def load_dives(self):
        table = self.ui.table_dives
        data = db.get_dives()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            for col, (cn, v) in enumerate(r.items()):
                item = QtWidgets.QTableWidgetItem('{}'.format(v))
                table.setItem(row, col, item)
        bat = db.get_dives_batteries()
        for row, r in enumerate(bat):
            item = QtWidgets.QTableWidgetItem('{}'.format(r))
            table.setItem(row, table.columnCount() - 1, item)

    def resize_tables(self):
        for t in [self.ui.table_dives, self.ui.table_batteries, self.ui.table_robots]:
            t.setVisible(False)
            t.resizeColumnsToContents()
            t.setVisible(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    current_path = os.getcwd()
    icon_path = os.path.join(current_path, 'assert', 'quadcopter.png')
    print(icon_path, os.path.exists(icon_path))
    app.setWindowIcon(QtGui.QIcon(icon_path))
    w = MainWindow()
    w.show()
    w.reload()
    sys.exit(app.exec())
