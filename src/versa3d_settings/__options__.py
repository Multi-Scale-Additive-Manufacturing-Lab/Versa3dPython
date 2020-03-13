from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QSettings


class GenericOption():
    def __init__(self, prefix, name):
        self._key = f'{prefix}/{name}'
        self._value = None

        self.label = ""
        self.tooltip = ""
        self.sidetext = ""
        self.category = ""
        self.subcategory = ""

        self._default_value = None
        self._settings = QSettings()

    @property
    def key(self):
        return self._key

    @property
    def value_type(self):
        return type(self._default_value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def default_value(self):
        return self._default_value


class SingleOption(GenericOption):
    def __init__(self, prefix, key, default_value):
        super().__init__(prefix, key)
        self._value = default_value
        self._default_value = default_value

    @pyqtSlot(int)
    @pyqtSlot(bool)
    @pyqtSlot(float)
    @pyqtSlot(str)
    def update_value(self, value):
        self._value = value


class EnumOption(GenericOption):
    def __init__(self, prefix, key, default_value, choices):
        super().__init__(prefix, key)
        self._value = default_value
        self._choices = choices

    @property
    def choices(self):
        return self._choices

    @pyqtSlot(int)
    def update_value(self, value):
        self._value = value


class OrderedArrayOption(GenericOption):
    def __init__(self, prefix, key, default_value_array):
        super().__init__(prefix, key)
        self._value = default_value_array
        self._default_value = default_value_array

    @property
    def value_type(self):
        return type(self._default_value[0])

    def set_value_at_index(self, i, value):
        self._value[i] = value

    @pyqtSlot(bool, int)
    @pyqtSlot(int, int)
    @pyqtSlot(float, int)
    @pyqtSlot(str, int)
    def update_value(self, value, index):
        self._value[index] = value

    def __len__(self):
        return len(self._value)
