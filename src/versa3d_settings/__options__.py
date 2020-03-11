from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QSettings

class generic_option():
    def __init__(self):
        self._value = None

        self.label = ""
        self.tooltip = ""
        self.sidetext = ""
        self.category = ""
        self.subcategory = ""

        self._default_value = None
        self._settings = QSettings()

    @property
    def value_type(self):
        return type(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val


class single_option(generic_option):
    def __init__(self, default_value):
        super().__init__()
        self._value = default_value
        self._default_value = default_value

    @pyqtSlot(int)
    @pyqtSlot(float)
    @pyqtSlot(str)
    def update_value(self, value):
        self._value = value


class enum_option(generic_option):
    def __init__(self, default_value, choices):
        super().__init__()
        self._value = default_value
        self._choices = choices

    @property
    def choices(self):
        return self._choices

    @pyqtSlot(int)
    def update_value(self, value):
        self._value = value


class ordered_array_option(generic_option):
    def __init__(self, default_value_array):
        super.__init__()
        self._value = default_value_array
        self._default_value = default_value_array

    @pyqtSlot(int, int)
    @pyqtSlot(float, int)
    @pyqtSlot(str, int)
    def update_value(self, value, index):
        self._value[index] = value
    
    def __len__(self):
        return len(self._value)
