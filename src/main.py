import sys

from PyQt5 import QtWidgets

from db import RobotsDB
from mainwindow import Ui_MainWindow

db = RobotsDB('home.me', 'ext', 'Qw123456_')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.button_start.clicked.connect(self.button_start_clicked)
        self.ui.button_stop.clicked.connect(self.button_stop_clicked)

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

    def resize_tables(self):
        for t in [self.ui.table_dives, self.ui.table_batteries, self.ui.table_robots]:
            t.setVisible(False)
            t.resizeColumnsToContents()
            t.setVisible(True)

    def button_start_clicked(self):
        pass

    def button_stop_clicked(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = MainWindow()
    w.show()
    w.reload()
    sys.exit(app.exec())
