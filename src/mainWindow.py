# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import PyQt5.QtCore as QtCore
import vtk

from src.GUI.ui_Versa3dMainWindow import Ui_Versa3dMainWindow
import src.GUI.res_rc

from src.lib.command import stlImportCommand
from src.lib.versa3dConfig import config
import src.lib.slicing as sl
from collections import deque
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
