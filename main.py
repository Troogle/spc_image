#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog

import os
import serial
from PyQt5 import QtCore, QtGui
from mainwin import Ui_MainWindow
from process_spc import convert
from motor_control import cycle_move
from motor_control import init_port
from motor_control import move_all_to_default
from motor_control import move_relative

class UiMain(QMainWindow):
    update_progress = QtCore.pyqtSignal(int, int)
    spc_file = ""

    def __init__(self, ports):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        if ports=={}:
            self.ui.Init_Button.setEnabled(False)
            self.ui.Move_X_Button.setEnabled(False)
            self.ui.Move_Y_Button.setEnabled(False)
            self.ui.Scan_Button.setEnabled(False)
            self.serials=None
        else:
            self.x_ser = serial.Serial(ports["x"], 921600, timeout=1)
            self.y_ser = serial.Serial(ports["y"], 921600, timeout=1)
            self.serials = {"x": self.x_ser, "y": self.y_ser}
        self.update_progress.connect(self.update_progress_handler)
        self.ui.Init_Button.clicked.connect(self.reset_all)
        self.ui.Move_X_Button.clicked.connect(lambda: self.move_rel(True))
        self.ui.Move_Y_Button.clicked.connect(lambda: self.move_rel(False))
        self.ui.Open_SPC_Button.clicked.connect(self.open_spc)
        self.ui.Convert_Button.clicked.connect(self.start_convert)
        self.ui.Scan_Button.clicked.connect(self.start_scan)

    def update_progress_handler(self, cur, maximum):
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(maximum)
        self.ui.progressBar.setValue(cur)

    def closeEvent(self, *args, **kwargs):
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        if self.serials:
            self.x_ser.close()
            self.y_ser.close()

    def reset_all(self):
        move_all_to_default(self.serials)

    # set False to move y
    def move_rel(self, x=True):
        try:
            if x:
                distance = float(self.ui.X_distance.text())/1000.0
                ser = self.x_ser
            else:
                distance = float(self.ui.Y_distance.text())/1000.0
                ser = self.y_ser
        except ValueError:
            QMessageBox.critical(self, "Error", "Value invalid!")
            return
        move_relative(ser, distance)

    def open_spc(self):
        self.spc_file,_ = QFileDialog.getOpenFileName(self, 'Open scanned spc-file', os.curdir,
                                                          "SPC files (*.spc *.SPC)")

    def start_scan(self):
        try:
            width = float(self.ui.Scan_Table.item(0, 0).text())/1000.0
            height = float(self.ui.Scan_Table.item(1, 0).text())/1000.0
            delay = float(self.ui.Scan_Table.item(2, 0).text())
            step = float(self.ui.Scan_Table.item(3, 0).text())/1000.0
        except ValueError:
            QMessageBox.critical(self, "Error", "Value invalid!")
            return
        cycle_move(self.serials, width, height, delay, step, self.update_progress, self)

    def start_convert(self):
        try:
            width = int(self.ui.Scan_Table_2.item(0, 0).text())
            height = int(self.ui.Scan_Table_2.item(1, 0).text())
            omitdata = int(self.ui.Scan_Table_2.item(2, 0).text())
            size = int(self.ui.Scan_Table_2.item(3, 0).text())
            start = int(self.ui.Scan_Table_2.item(4, 0).text())
            end = int(self.ui.Scan_Table_2.item(5, 0).text())
            freqstep = int(self.ui.Scan_Table_2.item(6, 0).text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Value invalid!")
            return
        convert(self.spc_file, width, height, size, omitdata, start, end, freqstep, self.update_progress)


app = QApplication(sys.argv)
window = UiMain(init_port())
window.show()
sys.exit(app.exec_())
