
import json
import copy
from collections import UserDict, OrderedDict

from PyQt5.QtCore import QSettings, QObject, pyqtSignal, pyqtSlot
import numpy as np
from os import path
from enum import Enum

from .versa3d_entry import MAP_TYPE

PRINTER_CONFIG = './configs/default_printer.json'
PRINTHEAD_CONFIG = './configs/default_printhead.json'
PRESET_PARAM_CONFIG = './configs/default_preset.json'

class SettingTypeKey(Enum):
    printer = 'preset_printer'
    printhead = 'preset_printhead'
    print_param = 'preset_param'

class PrintSettings(UserDict):
    def __init__(self, process_type, setting_type, val=None):
        if val is None:
            val = {}
        super().__init__(val)
        self.process_type = process_type
        self.type = setting_type

class Versa3dSettings(QObject):
    add_setting_signal = pyqtSignal(str, str)
    remove_setting_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        
        self.init_default()
        
        self._printer_list = {}
        self._printhead_list = {}
        self._param_preset_list = {}
    
    def load_all(self):
        self._printer_list = self.load_from_qsetting(str(SettingTypeKey.printer))
        self._printhead_list = self.load_from_qsetting(str(SettingTypeKey.printhead))
        self._param_preset_list = self.load_from_qsetting(str(SettingTypeKey.print_param))

    @property
    def printer(self):
        return self._printer_list

    @property
    def printhead(self):
        return self._printhead_list

    @property
    def parameter_preset(self):
        return self._param_preset_list

    def is_empty(self):
        qsetting = QSettings()
        return len(qsetting.allKeys()) == 0

    def init_from_json(self, setting_class, json_path):
        with open(json_path) as f:
            config = json.load(f)
        qsetting = QSettings()
        for setting_name, setting_val in config.items():
            q_path = '%s/%s' % (setting_class, setting_name)
            process_type = setting_val.pop('process')
            qsetting.setValue('%s/%s' % (q_path, 'process'), process_type)
            qsetting.setValue('%s/%s' % (q_path, 'type'), setting_name)
            for param, param_value in setting_val.items():
                entry_obj = MAP_TYPE[param_value['type']]
                entry_inst = entry_obj(param, param_value['ui'], param_value['value'])
                entry_inst.write_settings(q_path)

    def init_default(self):
        file_ls = [PRESET_PARAM_CONFIG, PRINTHEAD_CONFIG, PRINTER_CONFIG]
        setting_cls = [SettingTypeKey.print_param, SettingTypeKey.printhead, SettingTypeKey.printer]
        for s_cls, f_path in zip(setting_cls, file_ls):
            self.init_from_json(s_cls, f_path)
        
    def load_from_qsetting(self, setting_class):
        settings = QSettings()
        settings.beginGroup(setting_class)

        ls_setting_dict = OrderedDict()
        for setting_name in settings.childGroups():
            settings.beginGroup(setting_name)
            q_path = '%s/%s' % (setting_class, setting_name)
            process_type = settings.value('process', type = str)
            setting_type = settings.value('type', type = str)
            
            setting_dict = PrintSettings(process_type, setting_type)
            for param in settings.childGroups():
                settings.beginGroup(param)
                param_type = settings.value('type', type = str)
                entry_obj = MAP_TYPE[param_type]
                entry_inst = entry_obj(param)
                entry_inst.load_entry(q_path)
                setting_dict[param] = entry_inst
                settings.endGroup()
            settings.endGroup()
            ls_setting_dict[setting_name] = setting_dict
            self.add_setting_signal.emit(setting_class, setting_name)
        settings.endGroup()

        return ls_setting_dict

    def get_printer(self, name):
        return self._printer_list[name]

    def get_printhead(self, name):
        return self._printhead_list[name]

    def get_parameter_preset(self, name):
        return self._param_preset_list[name]

    def clone_setting(self, setting_set):
        new_setting = {}
        for entry_name, entry in setting_set.items():
            new_setting[entry_name] = entry.copy()
        return new_setting
    
    def clone_printer(self, name, new_name):
        self._printer_list[new_name] = self.clone_setting(self._printer_list[name])
        self.add_setting_signal.emit(str(SettingTypeKey.printer), new_name)
        return self._printer_list[new_name]

    def clone_printhead(self, name, new_name):
        self._printhead_list[new_name] = self.clone_setting(self._printhead_list[name])
        self.add_setting_signal.emit(str(SettingTypeKey.printer), new_name)
        return self._printhead_list[new_name]
    
    def clone_parameter_preset(self, name, new_name):
        self._param_preset_list[new_name] = self.clone_setting(self._param_preset_list[name])
        self.add_setting_signal.emit(str(SettingTypeKey.print_param), new_name)
        return self._param_preset_list[new_name]
    
    def save_to_disk(self, q_path, setting_dict):
        for entry in setting_dict.values():
            entry.write_settings(q_path)
    
    def save_printer(self, name):
        self.save_to_disk( '%s/%s' % (SettingTypeKey.printer,name), self._printer_list[name])
    
    def save_printhead(self, name):
        self.save_to_disk( '%s/%s' % (SettingTypeKey.printhead, name), self._printhead_list[name])
    
    def save_parameter_preset(self, name):
        self.save_to_disk('%s/%s' % (SettingTypeKey.print_param, name), self._param_preset_list[name])
    
    def remove_printer(self, name):
        qsetting = QSettings()
        qsetting.beginGroup(str(SettingTypeKey.printer))
        qsetting.remove(name)
        qsetting.endGroup()
        self.remove_setting_signal.emit(str(SettingTypeKey.printer), name)
        return self._printer_list.pop(name)
    
    def remove_printhead(self, name):
        qsetting = QSettings()
        qsetting.beginGroup(str(SettingTypeKey.printhead))
        qsetting.remove(name)
        qsetting.endGroup()
        self.remove_setting_signal.emit(str(SettingTypeKey.printhead), name)
        return self._printhead_list.pop(name)
    
    def remove_parameter_preset(self, name):
        qsetting = QSettings()
        qsetting.beginGroup(str(SettingTypeKey.print_param))
        qsetting.remove(name)
        qsetting.endGroup()
        self.remove_setting_signal.emit(str(SettingTypeKey.print_param), name)
        return self._param_preset_list.pop(name)