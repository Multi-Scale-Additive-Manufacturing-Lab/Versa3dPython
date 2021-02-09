
import json
from collections import OrderedDict

from PyQt5.QtCore import QSettings, QObject, pyqtSignal, pyqtSlot
from enum import Enum

from typing import Dict, List, Callable
import attr
import copy

from .versa3d_entry import MAP_TYPE, SingleEntry, IntEntry, FloatEntry, EnumEntry, ArrayIntEntry, ArrayFloatEntry

PRINTER_CONFIG = './configs/default_printer.json'
PRINTHEAD_CONFIG = './configs/default_printhead.json'
PRESET_PARAM_CONFIG = './configs/default_preset.json'


class SettingTypeKey(Enum):
    printer = 'preset_printer'
    printhead = 'preset_printhead'
    print_param = 'preset_param'

@attr.s(auto_attribs=True)
class PrintSetting:
    process: str

    def save_settings(self, q_path: str) -> None:
        qsetting = QSettings()
        for attr_n, val in self.__dict__.items():
            if isinstance(val, SingleEntry):
                val.write_settings(q_path)
            else:
                qsetting.setValue('%s/%s' % (q_path, attr_n), val)

    def clone(self):
        cls = self.__class__
        setting_dict = {}
        for attr_n, val in self.__dict__.items():
            if isinstance(val, SingleEntry):
                setting_dict[attr_n] = val.copy()
            else:
                setting_dict[attr_n] = copy.deepcopy(val)
        return cls(**setting_dict)

@attr.s(auto_attribs=True)
class SettingWrapper:
    setting : Dict[str, PrintSetting]
    clone : Callable[[int, str], None]
    remove : Callable[[int], None]
    save : Callable[[int], None]

@attr.s(auto_attribs=True)
class GenericPrinter(PrintSetting):
    build_bed_size: ArrayFloatEntry
    coord_offset: ArrayFloatEntry
    gcode_flavour: EnumEntry


@attr.s(auto_attribs=True)
class BinderJettingPrinter(GenericPrinter):
    process: str = 'bjp'


@attr.s(auto_attribs=True)
class DLPPrinter(GenericPrinter):
    process: str = 'dlp'


@attr.s(auto_attribs=True)
class GenericPrintParameter(PrintSetting):
    layer_thickness: FloatEntry


@attr.s(auto_attribs=True)
class BinderJettingPrintParameter(GenericPrintParameter):
    roller_rpm: FloatEntry
    roller_linear_speed: FloatEntry
    powder_loss_offset: FloatEntry
    powder_height_offset: FloatEntry
    roller_work_dist: FloatEntry
    bed_select: IntEntry
    saturation: FloatEntry
    n_pass: IntEntry
    print_speed: FloatEntry
    build_bed_velocity: FloatEntry
    fill_pattern: IntEntry
    tool_path_pattern: IntEntry
    feed_bed_velocity: FloatEntry

    process: str = 'bjp'


@attr.s(auto_attribs=True)
class DLPPrintParameter(GenericPrintParameter):
    layer_offset: FloatEntry
    process: str = 'dlp'


@attr.s(auto_attribs=True)
class PixelPrinthead(PrintSetting):
    dpi: ArrayIntEntry


@attr.s(auto_attribs=True)
class BinderJettingPrinthead(PixelPrinthead):
    process: str = 'bjp'


@attr.s(auto_attribs=True)
class DLPPrinthead(PixelPrinthead):
    process: str = 'dlp'


SETTING_TYPE_MAP = {
    'preset_printer': {
        'bjp': BinderJettingPrinter,
        'dlp': DLPPrinter
    },
    'preset_printhead': {
        'bjp': BinderJettingPrinthead,
        'dlp': DLPPrinthead
    },
    'preset_param': {
        'bjp': BinderJettingPrintParameter,
        'dlp': DLPPrintParameter
    }
}


class Versa3dSettings(QObject):
    add_setting_signal = pyqtSignal(str, str)
    remove_setting_signal = pyqtSignal(str, str)

    update_printhead_signal = pyqtSignal(int, str)
    update_printer_signal = pyqtSignal(int, str)
    update_print_param_signal = pyqtSignal(int, str)

    def __init__(self) -> None:
        super().__init__()

        self.init_default()

        self._printer_list = OrderedDict()
        self._printhead_list = OrderedDict()
        self._param_preset_list = OrderedDict()

    def load_all(self) -> None:
        self._printer_list = self.load_from_qsetting(
            SettingTypeKey.printer.value)
        self._printhead_list = self.load_from_qsetting(
            SettingTypeKey.printhead.value)
        self._param_preset_list = self.load_from_qsetting(
            SettingTypeKey.print_param.value)

    @property
    def printer(self) -> Dict[str, PrintSetting]:
        return self._printer_list

    @property
    def printhead(self) -> Dict[str, PrintSetting]:
        return self._printhead_list

    @property
    def parameter_preset(self) -> Dict[str, PrintSetting]:
        return self._param_preset_list

    @pyqtSlot(str, str)
    def printer_update_cb(self, name: str, parent: str):
        idx = list(self.printer.keys()).index(parent)
        self.update_printer_signal.emit(idx, name)

    @pyqtSlot(str, str)
    def printhead_update_cb(self, name: str, parent: str):
        idx = list(self.printhead.keys()).index(parent)
        self.update_printhead_signal.emit(idx, name)

    @pyqtSlot(str, str)
    def print_param_update_cb(self, name: str, parent: str):
        idx = list(self.parameter_preset.keys()).index(parent)
        self.update_print_param_signal.emit(idx, name)

    def is_empty(self) -> bool:
        qsetting = QSettings()
        return len(qsetting.allKeys()) == 0

    def init_from_json(self, setting_class: str, json_path: str) -> None:
        with open(json_path) as f:
            config = json.load(f)
        qsetting = QSettings()
        for setting_name, setting_val in config.items():
            q_path = '%s/%s' % (setting_class, setting_name)
            process_type = setting_val.pop('process')
            qsetting.setValue('%s/%s' % (q_path, 'process'), process_type)
            for param, param_value in setting_val.items():
                entry_obj = MAP_TYPE[param_value['type']]
                entry_inst = entry_obj(
                    param, param_value['ui'], param_value['value'])
                entry_inst.write_settings(q_path)

    def init_default(self) -> None:
        file_ls = [PRESET_PARAM_CONFIG, PRINTHEAD_CONFIG, PRINTER_CONFIG]
        setting_cls = [SettingTypeKey.print_param.value,
                       SettingTypeKey.printhead.value, SettingTypeKey.printer.value]
        for s_cls, f_path in zip(setting_cls, file_ls):
            self.init_from_json(s_cls, f_path)

    def load_from_qsetting(self, setting_class: str) -> Dict[str, PrintSetting]:
        settings = QSettings()
        settings.beginGroup(setting_class)

        ls_setting_dict = OrderedDict()
        for setting_name in settings.childGroups():
            settings.beginGroup(setting_name)
            q_path = '%s/%s' % (setting_class, setting_name)
            process_type = settings.value('process', type=str)
            setting_dict = {}
            for param in settings.childGroups():
                settings.beginGroup(param)
                param_type = settings.value('type', type=str)
                entry_obj = MAP_TYPE[param_type]
                entry_inst = entry_obj(param, parent_key=setting_name)

                if setting_class == SettingTypeKey.printer.value:
                    entry_inst.update_val.connect(self.printer_update_cb)
                elif setting_class == SettingTypeKey.printhead.value:
                    entry_inst.update_val.connect(self.printhead_update_cb)
                elif setting_class == SettingTypeKey.print_param.value:
                    entry_inst.update_val.connect(self.print_param_update_cb)
                else:
                    raise ValueError(
                        'unknown setting class {%s}' % (setting_class))

                entry_inst.load_entry(q_path)
                setting_dict[param] = entry_inst
                settings.endGroup()
            settings.endGroup()

            ls_setting_dict[setting_name] = SETTING_TYPE_MAP[setting_class][process_type](
                **setting_dict)
            self.add_setting_signal.emit(setting_class, setting_name)
        settings.endGroup()

        return ls_setting_dict

    def get_printer(self, idx: int) -> PrintSetting:
        key = list(self._printer_list.keys())[idx]
        return self._printer_list[key]

    def get_printhead(self, idx: int) -> PrintSetting:
        key = list(self._printhead_list.keys())[idx]
        return self._printhead_list[key]

    def get_parameter_preset(self, idx: int) -> PrintSetting:
        key = list(self._param_preset_list.keys())[idx]
        return self._param_preset_list[key]

    def clone_printer(self, idx: int, new_name: str) -> PrintSetting:
        self._printer_list[new_name] = self.get_printer(idx).clone()
        self.add_setting_signal.emit(SettingTypeKey.printer.value, new_name)
        return self._printer_list[new_name]

    def clone_printhead(self, idx: int, new_name: str) -> PrintSetting:
        self._printhead_list[new_name] = self.get_printhead(idx).clone()
        self.add_setting_signal.emit(SettingTypeKey.printer.value, new_name)
        return self._printhead_list[new_name]

    def clone_parameter_preset(self, idx: int, new_name: str) -> PrintSetting:
        self._param_preset_list[new_name] = self.get_parameter_preset(
            idx).clone()
        self.add_setting_signal.emit(
            SettingTypeKey.print_param.value, new_name)
        return self._param_preset_list[new_name]

    def save_printer(self, idx: int) -> None:
        name = list(self._printer_list.keys())[idx]
        q_path = '%s/%s' % (SettingTypeKey.printer.value, name)
        setting_dict = self._printer_list[name]
        setting_dict.save_settings(q_path)

    def save_printhead(self, idx: int) -> None:
        name = list(self._printhead_list.keys())[idx]
        q_path = '%s/%s' % (SettingTypeKey.printhead.value, name)
        setting_dict = self._printhead_list[name]
        setting_dict.save_settings(q_path)

    def save_parameter_preset(self, idx: int) -> None:
        name = list(self._param_preset_list.keys())[idx]
        q_path = '%s/%s' % (SettingTypeKey.print_param.value, name)
        setting_dict = self._param_preset_list[name]
        setting_dict.save_settings(q_path)

    def remove_printer(self, idx: int) -> None:
        name = list(self._printer_list.keys())[idx]
        qsetting = QSettings()
        qsetting.beginGroup(SettingTypeKey.printer.value)
        qsetting.remove(name)
        qsetting.endGroup()
        self.remove_setting_signal.emit(SettingTypeKey.printer.value, name)
        return self._printer_list.pop(name)

    def remove_printhead(self, idx: int) -> None:
        name = list(self._printhead_list.keys())[idx]
        qsetting = QSettings()
        qsetting.beginGroup(SettingTypeKey.printhead.value)
        qsetting.remove(name)
        qsetting.endGroup()
        self.remove_setting_signal.emit(SettingTypeKey.printhead.value, name)
        return self._printhead_list.pop(name)

    def remove_parameter_preset(self, idx: int) -> None:
        name = list(self._param_preset_list.keys())[idx]
        qsetting = QSettings()
        qsetting.beginGroup(SettingTypeKey.print_param.value)
        qsetting.remove(name)
        qsetting.endGroup()
        self.remove_setting_signal.emit(SettingTypeKey.print_param.value, name)
        return self._param_preset_list.pop(name)
