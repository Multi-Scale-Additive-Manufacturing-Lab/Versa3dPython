# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:47:41 2018

@author: inst
"""

import sys
import os
from PyQt5 import QtWidgets
from src.main_window import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        ui_path = os.path.join(base_path, 'GUI', 'Versa3dMainWindow.ui')
    except Exception:
        base_path = os.path.abspath(".")
        ui_path = os.path.join(
            base_path, 'designer_files', 'Versa3dMainWindow.ui')

    window = MainWindow(ui_path)
    window.show()

    sys.exit(app.exec_())
