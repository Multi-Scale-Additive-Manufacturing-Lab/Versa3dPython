# -*- coding: utf-8 -*

from PyQt5 import QtWidgets, uic

class MainWindow(QtWidgets.QMainWindow):
    """
    main window
    Arguments:
        QtWidgets {QMainWindow} -- main window
    """
    def __init__(self, ui_file_path):
        super().__init__()
        uic.loadUi(ui_file_path, self)
        