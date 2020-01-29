# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:47:41 2018

@author: inst
"""

import sys
from os import path
from PyQt5 import QtWidgets
from src.mainWindow import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(path.join('GUI', 'Versa3dMainWindow.ui'))
    window.show()

    sys.exit(app.exec_())
