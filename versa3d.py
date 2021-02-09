# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:47:41 2018

@author: inst
"""

import sys
import os
from PyQt5 import QtWidgets
from versa3d.main_window import MainWindow
from versa3d.controller import Versa3dController

def set_up_app(main_win : MainWindow, control : Versa3dController) -> None:
    CONTROLLER.settings.add_setting_signal.connect(
        main_win.populate_printer_drop_down
    )
    CONTROLLER.load_settings()

if __name__ == "__main__":
    APP = QtWidgets.QApplication(sys.argv)

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        BASE_PATH = sys._MEIPASS
        UI_PATH = os.path.join(BASE_PATH, 'GUI', 'Versa3dMainWindow.ui')
    except Exception:
        BASE_PATH = os.path.abspath(".")
        UI_PATH = os.path.join(
            BASE_PATH, 'designer_files', 'Versa3dMainWindow.ui')

    APP.setOrganizationName("msam")
    APP.setOrganizationDomain("https://msam-uwaterloo.ca/")
    APP.setApplicationName("Versa3d")

    WINDOW = MainWindow(UI_PATH)
    CONTROLLER = Versa3dController(parent = WINDOW)
    set_up_app(WINDOW, CONTROLLER)
    WINDOW.show()

    sys.exit(APP.exec_())
