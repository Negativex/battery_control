import os
import sys

from PyQt5 import QtWidgets, QtGui, QtCore

import dialog_new_battery
import dialog_new_dive
import dialog_new_robot
from db import RobotsDB
from mainwindow import Ui_MainWindow


class NewRobotDialog(QtWidgets.QDialog):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.ui = dialog_new_robot.Ui_dialog()
        self.ui.setupUi(self)


class NewBatteryDialog(QtWidgets.QDialog):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.ui = dialog_new_battery.Ui_Dialog()
        self.ui.setupUi(self)


class LogDiveDialog(QtWidgets.QDialog):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.ui = dialog_new_dive.Ui_Dialog()
        self.ui.setupUi(self)


def show_error(message):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec()


def ask(q):
    msg = QtWidgets.QMessageBox.question(None, "Battery control", q, QtWidgets.QMessageBox.Yes,
                                         QtWidgets.QMessageBox.No)
    return msg == QtWidgets.QMessageBox.Yes


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.db = RobotsDB('home.me', 'ext', 'Qw123456_')
        self.ui.button_add_battery.clicked.connect(self.add_battery)
        self.ui.button_add_dive.clicked.connect(self.add_dive)
        self.ui.button_add_robot.clicked.connect(self.add_robot)
        self.ui.button_edit_battery.clicked.connect(self.edit_battery)
        self.ui.button_edit_dive.clicked.connect(self.edit_dive)
        self.ui.button_edit_robot.clicked.connect(self.edit_robot)

    def add_battery(self):
        d = NewBatteryDialog()
        res = d.exec()
        if res == QtWidgets.QDialog.Accepted:
            battery_name = str(d.ui.edit_name.text())
            battery_v = float(d.ui.edit_voltage.value())
            print(battery_name, battery_v)
            if not (battery_name == ''):
                self.db.insert_battery(battery_name, battery_v)
                self.reload()
            else:
                show_error("Battery name cannot be empty!")

    def add_dive(self):
        d = LogDiveDialog()
        batteries = self.load_batteries(d.ui.table_batteries)
        # Init list with robot names
        robots = self.db.get_robots()
        d.ui.edit_robot.addItems([r['name'] for r in robots])
        # Set table checkable
        for r in range(d.ui.table_batteries.rowCount()):
            item = d.ui.table_batteries.item(r, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        res = d.exec()

        if res == QtWidgets.QDialog.Accepted:
            robot_id = robots[d.ui.edit_robot.currentIndex()]['id']
            selected_batteries = [b['id'] for (i, b) in enumerate(batteries)
                                  if d.ui.table_batteries.item(i, 0).checkState() == QtCore.Qt.Checked]
            if len(selected_batteries) == 0:
                show_error("You should specify at least one battery!")
                return
            time_started = d.ui.edit_date_start.dateTime().toPyDateTime()
            time_finished = d.ui.edit_date_finish.dateTime().toPyDateTime()
            if time_started > time_finished:
                show_error("Start time should be earlier than finish time!")
                return
            self.db.insert_dive(robot_id, time_started, time_finished, selected_batteries)
            self.reload()
            print(selected_batteries, robot_id)

    def add_robot(self):
        d = NewRobotDialog()
        res = d.exec()
        if res == QtWidgets.QDialog.Accepted:
            robot_name = str(d.ui.edit_name.text())
            print(robot_name)
            if not (robot_name == ''):
                self.db.insert_robot(robot_name)
                self.reload()
            else:
                show_error("Robot name cannot be empty!")

    def edit_battery(self):
        pass

    def edit_dive(self):
        pass

    def edit_robot(self):
        pass

    def reload(self):
        self.ui.statusbar.showMessage("Connecting to {} as {}...".format(self.db.host, self.db.username))
        self.db.connect()
        self.load_robots(self.ui.table_robots)
        self.ui.statusbar.showMessage("Connected", 5000)
        self.load_batteries(self.ui.table_batteries)
        self.load_dives(self.ui.table_dives)
        self.resize_tables()

    def load_robots(self, table):
        data = self.db.get_robots()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            for col, (cn, v) in enumerate(r.items()):
                item = QtWidgets.QTableWidgetItem('{}'.format(v))
                table.setItem(row, col, item)
        return data

    def load_batteries(self, table):
        data = self.db.get_batteries()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            for col, (cn, v) in enumerate(r.items()):
                item = QtWidgets.QTableWidgetItem('{}'.format(v))
                table.setItem(row, col, item)
        return data

    def load_dives(self, table):
        data = self.db.get_dives()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            for col, (cn, v) in enumerate(r.items()):
                item = QtWidgets.QTableWidgetItem('{}'.format(v))
                table.setItem(row, col, item)
        bat = self.db.get_dives_batteries()
        for row, r in enumerate(bat):
            item = QtWidgets.QTableWidgetItem('{}'.format(r))
            table.setItem(row, table.columnCount() - 1, item)
        return data

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
