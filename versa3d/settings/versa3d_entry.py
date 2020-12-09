from PyQt5.QtCore import QObject, QSettings, pyqtSlot
import numpy as np


class SingleEntry(QObject):
    def __init__(self, q_path, name, default_val = None, parent = None):
        QObject.__init__(self, parent)
        self.default_val = default_val
        self._value = default_val
        self.name = name
        self.entry_path = "%s/%s" % (q_path, self.name)
        self.modified = False
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if self._value != value:
            self.modified = True
            self._value = value
    
    def update_value(self, val):
        raise NotImplementedError
    
    def write_settings(self):
        settings = QSettings()
        settings.setValue("%s/%s" % (self.entry_path, 'value'), self.value)

    def load_entry(self):
        raise NotImplementedError

class IntEntry(SingleEntry):
    @pyqtSlot(int)
    def update_value(self, val):
        self.value = val
    
    def write_settings(self):
        SingleEntry.write_settings(self)
        settings = QSettings()
        settings.setValue("%s/%s" % (self.entry_path, 'type'), 'int')
    
    def load_entry(self):
        settings = QSettings()
        self.default_val = settings.value("%s/%s" % (self.entry_path, 'value'), type = int)
        self._value = self.default_val

class FloatEntry(SingleEntry):
    @pyqtSlot(float)
    def update_value(self, val):
        self.value = val
    
    def write_settings(self):
        SingleEntry.write_settings(self)
        settings = QSettings()
        settings.setValue("%s/%s" % (self.entry_path, 'type'), 'float')
    
    def load_entry(self):
        settings = QSettings()
        self.default_val = settings.value("%s/%s" % (self.entry_path, 'value'), type = float)
        self._value = self.default_val

class EnumEntry(SingleEntry):
    def __init__(self, q_path, name, default_val = None, enum_list = None, parent = None):
        SingleEntry.__init__(self, q_path, name, default_val, parent)
        self.enum_list = enum_list

    @pyqtSlot(int)
    def update_value(self, val):
        self.value = val
    
    def write_settings(self):
        SingleEntry.write_settings(self)
        settings = QSettings()
        settings.setValue("%s/%s" % (self.entry_path, 'type'), 'enum')
        settings.setValue("%s/%s" % (self.entry_path, 'enum_list'), self.enum_list)
    
    def load_entry(self):
        settings = QSettings()
        self.default_val = settings.value("%s/%s" % (self.entry_path, 'value'), type = int)
        self.enum_list = settings.value("%s/%s" % (self.entry_path, 'enum_list'))
        self._value = self.default_val

    
class ArrayIntEntry(SingleEntry):
    def __init__(self, q_path, name, default_val = None, parent = None):
        SingleEntry.__init__(self, q_path, name, default_val, parent)
        if isinstance(default_val, list):
            self._value = np.array(default_val, dtype = int)

    @pyqtSlot(int, int)
    def update_value(self, idx, val):
        if self._value[idx] != val:
            self._value[idx] = val
            self.modified = True
    
    def write_settings(self):
        settings = QSettings()
        settings.setValue("%s/%s" % (self.entry_path, 'value'), self.value.tolist())
        settings.setValue("%s/%s" % (self.entry_path, 'type'), 'array<int>')
    
    def load_entry(self):
        settings = QSettings()
        self.default_val = np.array(settings.value("%s/%s" % (self.entry_path, 'value')), dtype = int)
        self.value = self.default_val

class ArrayFloatEntry(SingleEntry):
    def __init__(self, q_path, name, default_val = None, parent = None):
        SingleEntry.__init__(self, q_path, name, default_val, parent)
        if isinstance(default_val, list):
            self.value = np.array(default_val, dtype = float)

    @pyqtSlot(int, float)
    def update_value(self, idx, val):
        if self._value[idx] != val:
            self._value[idx] = val
            self.modified = True
    
    def write_settings(self):
        settings = QSettings()
        settings.setValue("%s/%s" % (self.entry_path, 'value'), self.value.tolist())
        settings.setValue("%s/%s" % (self.entry_path, 'type'), 'array<float>')
    
    def load_entry(self):
        settings = QSettings()
        self.default_val = np.array(settings.value("%s/%s" % (self.entry_path, 'value')), dtype = float)
        self._value = self.default_val

MAP_TYPE = {
    'int': IntEntry,
    'float': FloatEntry,
    'enum' : EnumEntry,
    'array<int>': ArrayIntEntry,
    'array<float>': ArrayFloatEntry
}