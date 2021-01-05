from PyQt5.QtCore import QObject, QSettings, pyqtSlot
from PyQt5 import QtWidgets
import numpy as np

from typing import Any, AnyStr, List, Callable, Dict


class SingleEntry(QObject):
    def __init__(self, name: str, ui_dict: Dict[str, str] = None, default_val: Any = None, parent: QObject = None) -> None:
        QObject.__init__(self, parent)
        self.parent = parent
        self._value = default_val
        self._temp_val = self._value
        self.name = name
        if ui_dict is None:
            self.ui = {}
        else:
            self.ui = ui_dict

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        if self._value != value:
            self._temp_val = value
            self._value = value

    def _update_temp(self, val: Any):
        raise NotImplementedError

    @pyqtSlot()
    def commit_value(self) -> None:
        self._value = self._temp_val

    def write_settings(self, q_path: str) -> None:
        settings = QSettings()
        settings.setValue("%s/%s/%s" %
                          (q_path, self.name, 'value'), self.value)
        self.write_ui_settings(q_path)

    def write_ui_settings(self, q_path: str) -> None:
        settings = QSettings()
        for ui_label, ui_val in self.ui.items():
            settings.setValue("%s/%s/%s/%s" %
                              (q_path, self.name, 'ui', ui_label), ui_val)

    def load_ui_settings(self, q_path: str) -> None:
        settings = QSettings()
        settings.beginGroup("%s/%s/%s" % (q_path, self.name, 'ui'))
        for ui_label in settings.childKeys():
            self.ui[ui_label] = settings.value(ui_label)

    def load_entry(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def create_ui_entry(self) -> QtWidgets.QWidget:
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(self.ui['label'])
        layout.insertWidget(0, label)
        if 'unit' in self.ui.keys():
            unit_label = QtWidgets.QLabel(self.ui['unit'])
            layout.insertWidget(2, unit_label)
        layout.insertSpacing(-1, 20)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget


class IntEntry(SingleEntry):
    @pyqtSlot(int)
    def _update_temp(self, val: int) -> None:
        self._temp_val = val

    def write_settings(self, q_path: str) -> None:
        SingleEntry.write_settings(self, q_path)
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'int')

    def load_entry(self, q_path: str) -> None:
        settings = QSettings()
        self._value = settings.value(
            "%s/%s/%s" % (q_path, self.name, 'value'), type=int)
        self._temp_val = self._value
        self.load_ui_settings(q_path)

    def copy(self):
        return IntEntry(self.name, self.ui.copy(), self._value, self.parent)

    def create_ui_entry(self) -> QtWidgets.QWidget:
        widget = SingleEntry.create_ui_entry(self)
        input_widget = QtWidgets.QSpinBox()
        if 'range' in self.ui.keys():
            input_widget.setMinimum(int(self.ui['range'][0]))
            input_widget.setMaximum(int(self.ui['range'][1]))
        input_widget.setValue(self.value)
        input_widget.valueChanged.connect(self._update_temp)
        widget.layout().insertWidget(1, input_widget)
        return widget


class FloatEntry(SingleEntry):
    @pyqtSlot(float)
    def _update_temp(self, val: float) -> None:
        self._temp_val = val

    def write_settings(self, q_path: str) -> None:
        SingleEntry.write_settings(self, q_path)
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'float')

    def load_entry(self, q_path: str) -> None:
        settings = QSettings()
        self._value = settings.value(
            "%s/%s/%s" % (q_path, self.name, 'value'), type=float)
        self._temp_val = self._value
        self.load_ui_settings(q_path)

    def copy(self):
        return FloatEntry(self.name, self.ui.copy(), self._value, self.parent)

    def create_ui_entry(self) -> QtWidgets.QWidget:
        widget = SingleEntry.create_ui_entry(self)
        input_widget = QtWidgets.QDoubleSpinBox()
        if 'range' in self.ui.keys():
            input_widget.setMinimum(float(self.ui['range'][0]))
            input_widget.setMaximum(float(self.ui['range'][1]))

        input_widget.setValue(self.value)
        input_widget.valueChanged.connect(self._update_temp)
        widget.layout().insertWidget(1, input_widget)
        return widget


class EnumEntry(SingleEntry):
    @pyqtSlot(int)
    def _update_temp(self, val: int) -> None:
        self._temp_val = val

    def write_settings(self, q_path: str) -> None:
        SingleEntry.write_settings(self, q_path)
        settings = QSettings()
        settings.setValue("%s/%s/%s" % (q_path, self.name, 'type'), 'enum')

    def load_entry(self, q_path: str) -> None:
        settings = QSettings()
        self._value = settings.value(
            "%s/%s/%s" % (q_path, self.name, 'value'), type=int)
        self._temp_val = self._value
        self.load_ui_settings(q_path)

    def copy(self):
        return EnumEntry(self.name, self.ui.copy(), self._value, self.parent)

    def create_ui_entry(self) -> QtWidgets.QWidget:
        widget = SingleEntry.create_ui_entry(self)
        input_widget = QtWidgets.QComboBox()
        input_widget.addItems(self.ui['enum_list'])
        input_widget.setCurrentIndex(self.value)
        input_widget.currentIndexChanged.connect(self._update_temp)
        widget.layout().insertWidget(1, input_widget)
        return widget


class ArrayEntry(SingleEntry):
    def __init__(self, name: str, ui_dict: Dict[str, str] = None, parent: QObject = None):
        QObject.__init__(self, parent)
        self.parent = parent
        self.name = name
        if ui_dict is None:
            self.ui = {}
        else:
            self.ui = ui_dict

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value):
        if np.all(self._value != value):
            self._value = value
            self._temp_val = value


class ArrayIntEntry(ArrayEntry):
    def __init__(self, name: str, ui: Dict[str, str] = None, default_val: List[int] = None, parent: QObject = None) -> None:
        ArrayEntry.__init__(self, name, ui, parent)
        if isinstance(default_val, list):
            self._value = np.array(default_val, dtype=int)
        else:
            self._value = default_val
        self._temp_val = self._value

    def _update_temp(self, idx: int) -> Callable[[int], None]:
        @pyqtSlot(int)
        def f(val: int):
            self._temp_val[idx] = val
        return f

    def write_settings(self, q_path: str) -> None:
        settings = QSettings()
        settings.setValue("%s/%s/%s" %
                          (q_path, self.name, 'value'), self.value.tolist())
        settings.setValue("%s/%s/%s" %
                          (q_path, self.name, 'type'), 'array<int>')
        self.write_ui_settings(q_path)

    def load_entry(self, q_path: str) -> None:
        settings = QSettings()
        val = settings.value("%s/%s/%s" % (q_path, self.name, 'value'))
        self._value = np.array(val, dtype=int)
        self._temp_val = self._value.copy()
        self.load_ui_settings(q_path)

    def copy(self):
        return ArrayIntEntry(self.name, self.ui.copy(), self._value.copy(), self.parent)

    def create_ui_entry(self) -> QtWidgets.QWidget:
        widget = ArrayEntry.create_ui_entry(self)
        row_layout = QtWidgets.QHBoxLayout()
        for idx, val in enumerate(self.value):
            i_input = QtWidgets.QSpinBox()
            if 'range' in self.ui.keys():
                i_input.setMinimum(int(self.ui['range'][idx][0]))
                i_input.setMaximum(int(self.ui['range'][idx][1]))
            i_input.setValue(val)
            i_input.valueChanged.connect(self._update_temp(idx))
            row_layout.addWidget(i_input)
        widget.layout().insertLayout(1, row_layout)
        return widget


class ArrayFloatEntry(ArrayEntry):
    def __init__(self, name: str, ui: Dict[str, str] = None, default_val: List[float] = None, parent: QObject = None) -> None:
        ArrayEntry.__init__(self, name, ui, parent)
        if isinstance(default_val, list):
            self._value = np.array(default_val, dtype=int)
        else:
            self._value = default_val
        self._temp_val = self._value

    def _update_temp(self, idx: int) -> Callable[[int], None]:
        @pyqtSlot(float)
        def f(val):
            self._temp_val[idx] = val
        return f

    def write_settings(self, q_path: str) -> None:
        settings = QSettings()
        settings.setValue("%s/%s/%s" %
                          (q_path, self.name, 'value'), self.value.tolist())
        settings.setValue("%s/%s/%s" %
                          (q_path, self.name, 'type'), 'array<float>')
        self.write_ui_settings(q_path)

    def load_entry(self, q_path: str) -> None:
        settings = QSettings()
        val = settings.value("%s/%s/%s" % (q_path, self.name, 'value'))
        self._value = np.array(val, dtype=float)
        self._temp_val = self._value.copy()
        self.load_ui_settings(q_path)

    def copy(self):
        return ArrayFloatEntry(self.name, self.ui.copy(), self._value.copy(), self.parent)

    def create_ui_entry(self) -> QtWidgets.QWidget:
        widget = ArrayEntry.create_ui_entry(self)
        row_layout = QtWidgets.QHBoxLayout()
        for idx, val in enumerate(self.value):
            i_input = QtWidgets.QSpinBox()
            if 'range' in self.ui.keys():
                i_input.setMinimum(float(self.ui['range'][idx][0]))
                i_input.setMaximum(float(self.ui['range'][idx][1]))
            i_input.setValue(val)
            i_input.valueChanged.connect(self._update_temp(idx))
            row_layout.addWidget(i_input)
        widget.layout().insertLayout(1, row_layout)
        return widget


MAP_TYPE = {
    'int': IntEntry,
    'float': FloatEntry,
    'enum': EnumEntry,
    'array<int>': ArrayIntEntry,
    'array<float>': ArrayFloatEntry
}
