# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/dialog_new_dive.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(418, 410)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.edit_robot = QtWidgets.QComboBox(Dialog)
        self.edit_robot.setObjectName("edit_robot")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.edit_robot)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.edit_date_start = QtWidgets.QDateTimeEdit(Dialog)
        self.edit_date_start.setDateTime(QtCore.QDateTime(QtCore.QDate(2019, 9, 14), QtCore.QTime(0, 0, 0)))
        self.edit_date_start.setMinimumDateTime(QtCore.QDateTime(QtCore.QDate(2019, 1, 1), QtCore.QTime(0, 0, 0)))
        self.edit_date_start.setObjectName("edit_date_start")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.edit_date_start)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.edit_date_finish = QtWidgets.QDateTimeEdit(Dialog)
        self.edit_date_finish.setObjectName("edit_date_finish")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.edit_date_finish)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.verticalLayout.addLayout(self.formLayout)
        self.table_batteries = QtWidgets.QTableWidget(Dialog)
        self.table_batteries.setEnabled(True)
        self.table_batteries.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_batteries.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table_batteries.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_batteries.setColumnCount(4)
        self.table_batteries.setObjectName("table_batteries")
        self.table_batteries.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table_batteries.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_batteries.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_batteries.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_batteries.setHorizontalHeaderItem(3, item)
        self.table_batteries.horizontalHeader().setVisible(True)
        self.table_batteries.horizontalHeader().setCascadingSectionResizes(True)
        self.table_batteries.horizontalHeader().setDefaultSectionSize(60)
        self.table_batteries.horizontalHeader().setHighlightSections(False)
        self.table_batteries.horizontalHeader().setMinimumSectionSize(0)
        self.table_batteries.horizontalHeader().setStretchLastSection(True)
        self.table_batteries.verticalHeader().setVisible(False)
        self.table_batteries.verticalHeader().setDefaultSectionSize(24)
        self.verticalLayout.addWidget(self.table_batteries)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_3.setText(_translate("Dialog", "Robot:"))
        self.label.setText(_translate("Dialog", "Start time:"))
        self.label_2.setText(_translate("Dialog", "Finish time:"))
        self.label_4.setText(_translate("Dialog", "Battery pack:"))
        item = self.table_batteries.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Battery ID"))
        item = self.table_batteries.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Name"))
        item = self.table_batteries.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Voltage"))
        item = self.table_batteries.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Total time used"))
