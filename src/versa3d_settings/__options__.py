from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot


class versa3d_single_option():
    def __init__(self, default_value):
        super().__init__()
        self._value = default_value

        self.label = ""
        self.tooltip = ""
        self.sidetext = ""
        self.category = ""
        self.subcategory = ""

        self._default_value = default_value

    @property
    def value_type(self):
        return type(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @pyqtSlot(int)
    @pyqtSlot(float)
    @pyqtSlot(str)
    def update_value(self, value):
        self._value = value
