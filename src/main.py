import datetime
import os
import sys

from PyQt5 import QtWidgets, QtGui, QtCore

import dialog_new_battery
import dialog_new_dive
import dialog_new_robot
import dialog_start_dive
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
        self.ui.edit_date_start.setDateTime(datetime.datetime.now() - datetime.timedelta(hours=1))
        self.ui.edit_date_finish.setDateTime(datetime.datetime.now())


class StartDiveDialog(QtWidgets.QDialog):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.ui = dialog_start_dive.Ui_Dialog()
        self.ui.setupUi(self)


def show_error(message):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec()


def show_info(message):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(message)
    msg.setWindowTitle("Info")
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
        self.db = RobotsDB('negative.ddns.net', 'ext', 'Qw123456_')
        self.connect_buttons()
        self.robot_ids = []
        self.battery_ids = []
        self.dive_ids = []

    def connect_buttons(self):
        self.ui.button_add_battery.clicked.connect(self.add_battery)
        self.ui.button_add_dive.clicked.connect(self.add_dive)
        self.ui.button_add_robot.clicked.connect(self.add_robot)
        self.ui.button_edit_battery.clicked.connect(self.edit_battery)
        self.ui.button_edit_robot.clicked.connect(self.edit_robot)
        self.ui.button_refresh.clicked.connect(self.reload)
        self.ui.button_remove_robot.clicked.connect(self.remove_robot)
        self.ui.button_remove_dive.clicked.connect(self.remove_dive)
        self.ui.button_remove_battery.clicked.connect(self.remove_battery)
        self.ui.button_start_dive.clicked.connect(self.start_new_dive)
        self.ui.button_stop_dive.clicked.connect(self.stop_dive)
        self.ui.button_charge_battery.clicked.connect(self.charge_battery)
        # TODO Settings {Json}
        # TODO Threading
        # TODO Release

    def charge_battery(self):
        battery_id = self.battery_ids[self.ui.table_batteries.currentIndex().row()]
        battery = self.db.get_batteries(ids=[battery_id])[0]
        d = NewBatteryDialog()
        d.ui.edit_voltage.setValue(float(battery['voltage']))
        d.ui.edit_name.setText(str(battery['name']))
        d.ui.edit_name.setEnabled(False)
        res = d.exec()
        if res == QtWidgets.QDialog.Accepted:
            if battery['charging']:
                self.db.stop_charge({
                    'battery_id': battery_id,
                    'voltage': d.ui.edit_voltage.value()
                })
            else:
                self.db.start_charge({
                    'battery_id': battery_id,
                    'time_start': datetime.datetime.now(),
                    'voltage_start': d.ui.edit_voltage.value()
                })
            self.reload()

    def stop_dive(self):
        if len(self.dive_ids) > 0:
            dive_id = self.dive_ids[self.ui.table_dives.currentIndex().row()]
            dive = self.db.get_dives(ids=[dive_id])[0]
            if dive['running']:
                show_info("Please update voltages on {}!".format(
                    [b for b in self.db.get_dives_batteries(dive_id, True)]))
                self.db.stop_dive(
                    dive_id,
                    [self.edit_battery(id=bid) for bid in self.db.get_dives_batteries(dive_id, False)])
                self.reload()

    def start_new_dive(self):
        self.add_dive(start=True)

    def remove_robot(self):
        if len(self.robot_ids) > 0:
            robot_id = self.robot_ids[self.ui.table_robots.currentIndex().row()]
            if ask("Are you sure to delete robot {}?".format(self.db.get_robots(ids=[robot_id])[0]['name'])):
                self.db.delete_robot(robot_id)
                self.reload()

    def remove_battery(self):
        if len(self.battery_ids) > 0:
            battery_id = self.battery_ids[self.ui.table_batteries.currentIndex().row()]
            if ask("Are you sure to delete battery {}?".format(self.db.get_batteries(ids=[battery_id])[0]['name'])):
                self.db.delete_battery(battery_id)
                self.reload()

    def remove_dive(self):
        if len(self.dive_ids) > 0:
            dive_id = self.dive_ids[self.ui.table_dives.currentIndex().row()]
            if ask("Are you sure to delete dive #{}?".format(self.db.get_dives(ids=[dive_id])[0]['id'])):
                self.db.delete_dive(dive_id)
                self.reload()

    def add_battery(self):
        d = NewBatteryDialog()
        res = d.exec()
        if res == QtWidgets.QDialog.Accepted:
            battery_name = str(d.ui.edit_name.text())
            battery_voltage = float(d.ui.edit_voltage.value())
            # print(battery_name, battery_voltage)
            if not (battery_name == ''):
                self.db.insert_battery({
                    'name': battery_name,
                    'voltage': battery_voltage
                })
                self.reload()
            else:
                show_error("Battery name cannot be empty!")

    def add_dive(self, start=False):
        if start:
            d = StartDiveDialog()
        else:
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
            if start:
                time_started = datetime.datetime.now() - datetime.timedelta(seconds=1)
                time_finished = None
            else:
                time_started = d.ui.edit_date_start.dateTime().toPyDateTime()
                time_finished = d.ui.edit_date_finish.dateTime().toPyDateTime()
                if time_started > time_finished:
                    show_error("Start time should be earlier than finish time!")
                    return
            self.db.insert_dive({
                'robot_id': robot_id,
                'time_started': time_started,
                'time_finished': time_finished,
                'batteries': selected_batteries
            })
            self.reload()
            # print(selected_batteries, robot_id)

    def add_robot(self):
        d = NewRobotDialog()
        res = d.exec()
        if res == QtWidgets.QDialog.Accepted:
            robot_name = str(d.ui.edit_name.text())
            # print(robot_name)
            if not (robot_name == ''):
                self.db.insert_robot({
                    'name': robot_name
                })
                self.reload()
            else:
                show_error("Robot name cannot be empty!")

    def edit_battery(self, id=None):
        if len(self.battery_ids) > 0:
            d = NewBatteryDialog()
            if id is not None:
                battery_id = id
            else:
                battery_id = self.battery_ids[self.ui.table_batteries.currentIndex().row()]
            battery = self.db.get_batteries(ids=[battery_id])[0]
            d.ui.edit_voltage.setValue(float(battery['voltage']))
            d.ui.edit_name.setText(str(battery['name']))
            if id is not None:
                d.ui.edit_name.setEnabled(False)
            res = d.exec()
            if res == QtWidgets.QDialog.Accepted or id is not None:
                battery_name = str(d.ui.edit_name.text())
                battery_voltage = float(d.ui.edit_voltage.value())
                # print(battery_name, battery_voltage)
                if not (battery_name == ''):
                    self.db.update_battery({
                        'id': battery_id,
                        'name': battery_name,
                        'voltage': battery_voltage,
                        'total_time': battery['total_time']
                    })
                    self.reload()
                else:
                    show_error("Battery name cannot be empty!")
                return battery_id, battery_voltage

    def edit_dive(self):
        pass

    def edit_robot(self):
        if len(self.robot_ids) > 0:
            d = NewRobotDialog()
            robot_id = self.robot_ids[self.ui.table_robots.currentIndex().row()]
            robot = self.db.get_robots(ids=[robot_id])[0]
            d.ui.edit_name.setText(str(robot['name']))
            res = d.exec()
            if res == QtWidgets.QDialog.Accepted:
                robot_name = str(d.ui.edit_name.text())
                print(robot_name)
                if not (robot_name == ''):
                    self.db.update_robot({
                        'id': robot_id,
                        'name': robot_name,
                        'total_time': robot['total_time']
                    })
                    self.reload()
                else:
                    show_error("Robot name cannot be empty!")

    def reload(self):
        self.ui.statusbar.showMessage("Connecting to {} as {}...".format(self.db.host, self.db.username))
        try:
            self.db.get_robots()
        except:
            self.db.connect()
        self.ui.statusbar.showMessage("Connected", 5000)
        self.robot_ids = [x['id'] for x in self.load_robots(self.ui.table_robots)]
        self.battery_ids = [x['id'] for x in self.load_batteries(self.ui.table_batteries)]
        self.dive_ids = [x['dive_id'] for x in self.load_dives(self.ui.table_dives)]
        self.resize_tables()

    def load_robots(self, table):
        data = self.db.get_robots()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            r['total_time'] = datetime.timedelta(seconds=r['total_time'])
        for col, name in enumerate(['id', 'name', 'total_time']):
            for row, r in enumerate(data):
                item = QtWidgets.QTableWidgetItem('{}'.format(r[name]))
                table.setItem(row, col, item)
        return data

    def load_batteries(self, table):
        data = self.db.get_batteries()
        table.setRowCount(len(data))
        for row, r in enumerate(data):
            r['total_time'] = datetime.timedelta(seconds=r['total_time'])
        for col, name in enumerate(['id', 'name', 'voltage', 'total_time']):
            for row, r in enumerate(data):
                item = QtWidgets.QTableWidgetItem('{}'.format(r[name]))
                table.setItem(row, col, item)
        for row, r in enumerate(data):
            if r['charging']:
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    item.setBackground(QtGui.QBrush(QtGui.QColor.fromRgb(163, 163, 255)))
        return data

    def load_dives(self, table):
        data = self.db.get_dives_table()
        table.setRowCount(len(data))
        for dive in data:
            if dive['robot_name'] is None:
                dive['robot_name'] = "DELETED"
            if dive['running']:
                dive['time_finished'] = ' --- '
                dive['duration'] = str((datetime.datetime.now() - dive['time_started'])).split('.', 2)[0]
            else:
                dive['duration'] = str((datetime.timedelta(seconds=dive['duration']))).split('.', 2)[0]
        for col, name in enumerate(
                ['dive_id', 'robot_name', 'time_started', 'time_finished', 'duration', 'batteries']):
            for row, r in enumerate(data):
                item = QtWidgets.QTableWidgetItem('{}'.format(r[name]))
                table.setItem(row, col, item)

        for row, r in enumerate(data):
            if r['running']:
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    item.setBackground(QtGui.QBrush(QtGui.QColor.fromRgb(163, 255, 163)))

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
