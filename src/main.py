import sys
import time

from PyQt5 import QtWidgets

from mainwindow import Ui_MainWindow

batteries_v = []
drones = []
dives = []


class Dive:
    def __init__(self, id, drone, batteries):
        self.batteries = batteries
        self.drone = drone
        self.id = id
        self.time_start = 0
        self.time_stop = 0
        self.total_time = 0
        self.started = False

    def start(self):
        self.started = True
        self.time_start = time.time()

    def stop(self):
        self.started = False
        self.time_stop = time.time()
        self.total_time = round(self.time_stop - self.time_start)
        log_dive(self.drone, self.batteries, self.total_time)


def log_dive(drone, batteries_ids, total_time):
    print('Dive completed, Drone: {}, Batteries: {}, Total time: {}s'.format(drone,
                                                                             batteries_ids,
                                                                             total_time))


def load_config():
    drones.append('K1')
    drones.append('K2')
    for _ in range(12):
        batteries_v.append(12.0)
    print('Config loaded.')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_battery_table()
        self.ui.button_start.clicked.connect(self.button_start_clicked)
        self.ui.button_stop.clicked.connect(self.button_stop_clicked)
        self.current_dive_id = 1

    def load_battery_table(self):
        for i, v in enumerate(batteries_v):
            table_batteries = self.ui.table_batteries
            table_batteries.insertRow(table_batteries.rowCount())
            item_id = QtWidgets.QTableWidgetItem('{}'.format(i))
            table_batteries.setItem(table_batteries.rowCount() - 1, 0, item_id)
            item_v = QtWidgets.QTableWidgetItem('{} V'.format(v))
            table_batteries.setItem(table_batteries.rowCount() - 1, 1, item_v)

    def add_dive_into_table(self, dive):
        table_dives = self.ui.table_dives
        table_dives.insertRow(table_dives.rowCount())
        for i, v in enumerate([dive.id, dive.drone, dive.batteries, dive.total_time]):
            item = QtWidgets.QTableWidgetItem('{}'.format(v))
            table_dives.setItem(table_dives.rowCount() - 1, i, item)

    def button_start_clicked(self):
        dive = Dive(self.current_dive_id, drones[0], [0, 1])
        self.current_dive_id += 1
        dives.append(dive)
        self.add_dive_into_table(dive)
        dive.start()

    def button_stop_clicked(self):
        dives[0].stop()


if __name__ == '__main__':
    load_config()
    app = QtWidgets.QApplication([])
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
