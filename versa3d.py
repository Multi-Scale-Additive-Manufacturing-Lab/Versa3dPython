# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:47:41 2018

@author: inst
"""

import sys
import os
from PyQt5 import QtWidgets
from versa3d.main_window import MainWindow

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
    APP.setOrganizationDomain("uw.msam")
    APP.setApplicationName("Versa3d")

    WINDOW = MainWindow(UI_PATH)
    WINDOW.show()

    sys.exit(APP.exec_())
