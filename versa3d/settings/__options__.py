from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QSettings


class GenericOption():
    def __init__(self, prefix, name):
        self._key = f'{prefix}/{name}'

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
    def default_value(self):
        return self._default_value


class SingleOption(GenericOption):
    def __init__(self, prefix, name, default_value):
        super().__init__(prefix, name)
        self._type = type(default_value)
        self._default_value = default_value

    @property
    def value(self):
        value = self._settings.value(
            self._key, self._default_value, self._type)
        return value

    @value.setter
    def value(self, val):
        self._settings.setValue(self._key, val)

    @pyqtSlot(int)
    @pyqtSlot(bool)
    @pyqtSlot(float)
    @pyqtSlot(str)
    def update_value(self, val):
        self._settings.setValue(self._key, val)


class EnumOption(GenericOption):
    def __init__(self, prefix, name, default_value, choices):
        super().__init__(prefix, name)
        self._default_value = default_value
        self._choices = choices

    @property
    def choices(self):
        return self._choices

    @property
    def value(self):
        value = self._settings.value(
            self._key, self._default_value, int)
        return value

    @pyqtSlot(int)
    def update_value(self, val):
        self._settings.setValue(self._key, val)


class PointOption(GenericOption):
    def __init__(self, prefix, name, default_value_array):
        super().__init__(prefix, name)
        self._default_value = default_value_array
        self._size = len(default_value_array)

    @property
    def value(self):
        point = []
        self._settings.beginReadArray(self._key)
        for i in range(self._size):
            self._settings.setArrayIndex(i)
            default_val = self._default_value[i]
            point.append(self._settings.value('p', default_val, float))
        self._settings.endArray()
        return point

    @pyqtSlot(int, float)
    def update_value(self, index, val):
        self._settings.beginWriteArray(self._key, self._size)
        self._settings.setArrayIndex(index)
        self._settings.setValue('p', val)
        self._settings.endArray()

    def __len__(self):
        return self._size
