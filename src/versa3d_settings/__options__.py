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
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val


class versa3d_float_option(versa3d_single_option):
    def __init__(self, value):
        super().__init__(self, value)

    @pyqtSlot(float)
    def update_value(self, value):
        self._value = value


class versa3d_int_option(versa3d_single_option):
    def __init__(self, value):
        super().__init__(self, value)

    @pyqtSlot(int)
    def update_value(self, value):
        self._value = value
