from PyQt5.QtCore import QObject, QSettings, pyqtSlot
import numpy as np


class SingleEntry(QObject):
    def __init__(self, name, default_val = None, parent = None):
        QObject.__init__(self, parent)
        self.parent = parent
        self.default_val = default_val
        self._value = default_val
        self.name = name
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
    
    def write_settings(self, q_path):
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'value'), self.value)

    def load_entry(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

class IntEntry(SingleEntry):
    @pyqtSlot(int)
    def update_value(self, val):
        self.value = val
    
    def write_settings(self, q_path):
        SingleEntry.write_settings(self, q_path)
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'int')
    
    def load_entry(self, q_path):
        settings = QSettings()
        self.default_val = settings.value("%s/%s/%s" % (q_path, self.name, 'value'), type = int)
        self._value = self.default_val
    
    def copy(self):
        return IntEntry(self.name, self._value, self.parent)

class FloatEntry(SingleEntry):
    @pyqtSlot(float)
    def update_value(self, val):
        self.value = val
    
    def write_settings(self, q_path):
        SingleEntry.write_settings(self, q_path)
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'float')
    
    def load_entry(self, q_path):
        settings = QSettings()
        self.default_val = settings.value("%s/%s/%s" % (q_path, self.name, 'value'), type = float)
        self._value = self.default_val
    
    def copy(self):
        return FloatEntry(self.name, self._value, self.parent)

class EnumEntry(SingleEntry):
    def __init__(self, name, default_val = None, enum_list = None, parent = None):
        SingleEntry.__init__(self, name, default_val, parent)
        self.enum_list = enum_list

    @pyqtSlot(int)
    def update_value(self, val):
        self.value = val
    
    def write_settings(self, q_path):
        SingleEntry.write_settings(self, q_path)
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'enum')
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'enum_list'), self.enum_list)
    
    def load_entry(self, q_path):
        settings = QSettings()
        self.default_val = settings.value("%s/%s/%s" % (q_path, self.name, 'value'), type = int)
        self.enum_list = settings.value("%s/%s/%s" % (q_path, self.name, 'enum_list'))
        self._value = self.default_val
    
    def copy(self):
        return EnumEntry(self.q_path, self.name, self._value, self.enum_list.copy(), self.parent)

class ArrayEntry(SingleEntry):
    def update_value(self, idx, val):
        if self._value[idx] != val:
            self._value[idx] = val
            self.modified = True
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if np.all(self._value != value):
            self.modified = True
            self._value = value
    
class ArrayIntEntry(ArrayEntry):
    def __init__(self, name, default_val = None, parent = None):
        SingleEntry.__init__(self, name, default_val, parent)
        if isinstance(default_val, list):
            self.default_val = np.array(default_val, dtype = int)
            self._value = self.default_val

    @pyqtSlot(int, int)
    def update_value(self, idx, val):
        ArrayEntry.update_value(self, idx, val)

    def write_settings(self, q_path):
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'value'), self.value.tolist())
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'array<int>')
    
    def load_entry(self, q_path):
        settings = QSettings()
        val = settings.value("%s/%s/%s" % (q_path, self.name, 'value'))
        self.default_val = np.array(val, dtype = int)
        self._value = self.default_val
    
    def copy(self):
        return ArrayIntEntry( self.name, self._value.copy(), self.parent)

class ArrayFloatEntry(ArrayEntry):
    def __init__(self, name, default_val = None, parent = None):
        ArrayEntry.__init__(self, name, default_val, parent)
        if isinstance(default_val, list):
            self.default_val = np.array(default_val, dtype = float)
            self._value = self.default_val

    @pyqtSlot(int, int)
    def update_value(self, idx, val):
        ArrayEntry.update_value(self, idx, val)
    
    def write_settings(self, q_path):
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'value'), self.value.tolist())
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'array<float>')
    
    def load_entry(self, q_path):
        settings = QSettings()
        val = settings.value("%s/%s/%s" % (q_path, self.name, 'value'))
        self.default_val = np.array(val, dtype = float)
        self._value = self.default_val
    
    def copy(self):
        return ArrayFloatEntry( self.name, self._value.copy(), self.parent)

MAP_TYPE = {
    'int': IntEntry,
    'float': FloatEntry,
    'enum' : EnumEntry,
    'array<int>': ArrayIntEntry,
    'array<float>': ArrayFloatEntry
}