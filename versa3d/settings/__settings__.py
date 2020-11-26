
import json
from functools import partial
from collections import namedtuple

from PyQt5.QtCore import QSettings, QObject, pyqtSignal
import numpy as np
from os import path

DEFAULT_CONFIG = './configs/default_config.json'

MAP_TYPE = {
    'int': int,
    'string': str,
    'float': float,
    'Array<int>': partial(np.array, dtype=int),
    'Array<float>': partial(np.array, dtype=float),
    'Array<string>': partial(np.array, dtype=str)
}

UI_PATH = 'ui_settings'
PARAM_PATH = 'presets'


class Versa3dSettings(QObject):
    add_printer_signal = pyqtSignal(str)
    add_printhead_signal = pyqtSignal(str)
    add_parameter_preset_signal = pyqtSignal(str)

    remove_printer_signal = pyqtSignal(str)
    remove_printhead_signal = pyqtSignal(str)
    remove_parameter_preset_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.settings = QSettings()

        self._printer_list = {}
        self._printhead_list = {}
        self._parameter_preset_list = {}

    @property
    def printer(self):
        return self._printer_list

    @property
    def printhead(self):
        return self._printhead_list

    @property
    def parameter_preset(self):
        return self._parameter_preset_list

    def is_empty(self):
        return len(self.settings.allKeys()) == 0

    def init_default(self):
        with open(DEFAULT_CONFIG) as f:
            default_config = json.load(f)

        param_key_list = ['type', 'value']
        ui_key_list = ['label', 'section', 'category', 'section', 'unit']

        for setting_class_name, setting_dict in default_config.items():
            setting_type = setting_dict.pop('type')
            default_name = setting_dict.pop('default_name')

            ui_path = "%s/%s/%s" % (UI_PATH, setting_type, setting_class_name)
            param_path = "%s/%s/%s" % (PARAM_PATH, setting_type, default_name)
            self.settings.setValue("%s/cls_name" %
                                   format(param_path), setting_class_name)
            for param_key, param_dict in setting_dict.items():
                for u_key in ui_key_list:
                    self.settings.setValue(
                        "%s/%s/%s" % (ui_path, param_key, u_key), param_dict[u_key])

                for p_key in param_key_list:
                    self.settings.setValue(
                        "%s/%s/%s" % (param_path, param_key, p_key), param_dict[p_key])

    def get_ui_param(self, section):
        self.settings.beginGroup(UI_PATH)
        self.settings.beginGroup(section)
        preset_name = self.settings.childGroups()
        ls_ui = {}
        for name in preset_name:
            ls_ui[name] = {}
            self.settings.beginGroup(name)
            preset_type = self.settings.value('type')
            ls_ui[name]['type'] = preset_type
            param_list = self.settings.childGroups()
            for param in param_list:
                self.settings.beginGroup(param)
                ui_dict = {}
                labels = ['label', 'category', 'section']
                for l in labels:
                    ui_dict[l] = self.settings.value(l)

                ls_ui[param] = ui_dict

        return ls_ui

    def load_all(self):
        self._printer_list = self.load_settings('printer')
        self._printhead_list = self.load_settings('printhead')
        self._parameter_preset_list = self.load_settings('parameter_preset')

    def get_printer(self, name):
        return self._printer_list[name]

    def get_printhead(self, name):
        return self._printhead_list[name]

    def get_preset(self, name):
        return self._parameter_preset_list[name]

    def clone_printer(self, name, target_name):
        obj = self.clone_setting( self._printer_list[name])
        self.add_printer_signal.emit(target_name)
        self._printer_list[target_name] = obj
        self.save_to_disk('printer', target_name)

    def clone_printhead(self, name, target_name):
        obj = self.clone_setting( self._printhead_list[name])
        self.add_printhead_signal.emit(target_name)
        self._printhead_list[target_name] = obj
        self.save_to_disk('printhead', target_name)

    def clone_param(self, name, target_name):
        obj = self.clone_setting(self._parameter_preset_list[name])
        self.add_parameter_preset_signal.emit(target_name)
        self._parameter_preset_list[target_name] = obj
        self.save_to_disk('parameter_preset', target_name)

    def remove_printer(self, name):
        self._printer_list.pop(name)
        self.remove_from_disk('printer', name)
        self.remove_printer_signal.emit(name)

    def remove_printhead(self, name):
        self._printhead_list.pop(name)
        self.remove_from_disk('printhead', name)
        self.remove_printhead_signal.emit(name)

    def remove_parameter(self, name):
        self._parameter_preset_list.pop(name)
        self.remove_from_disk('parameter_preset', name)
        self.remove_parameter_preset_signal.emit(name)

    def remove_from_disk(self, section, name):
        key = "%s/%s/%s" % (PARAM_PATH, section, name)
        self.settings.remove(key)

    def clone_setting(self, old_obj):
        name = type(old_obj).__name__
        dict_obj = old_obj._asdict()
        return namedtuple(name, dict_obj.keys(), defaults=dict_obj.values())()

    def update_printer_value(self, name, key, value):
        self._printer_list[name] = self._printer_list[name]._replace(
            **{key: value})
        return self._printer_list[name]

    def update_printhead_value(self, name, key, value):
        self._printhead_list[name] = self._printhead_list[name]._replace(
            **{key: value})
        return self._printhead_list[name]

    def update_preset_value(self, name, key, value):
        self._parameter_preset_list[name] = self._parameter_preset_list[name]._replace(
            **{key: value})
        return self._parameter_preset_list[name]

    def save_to_disk(self, section, name):
        obj_ls = getattr(self, section)
        settings = obj_ls[name]
        try:
            setting_path = '%s/%s/%s' % (PARAM_PATH, section, name)
            cls_name = type(settings).__name__
            self.settings.setValue('%s/cls_name' % (setting_path), cls_name)
            for param, value in settings._asdict().items():
                p_key = '%s/%s' % (setting_path, param)
                self.settings.setValue('%s/value' % (p_key), value)
                val_type = self.type_to_string(value)
                self.settings.setValue('%s/type' % (p_key), val_type)
        except:
            raise Exception('disk write failed')

    def get_list_preset(self, section):
        self.settings.beginGroup(PARAM_PATH)
        self.settings.beginGroup(section)
        list_of_preset = self.settings.childGroups()
        self.settings.endGroup()
        self.settings.endGroup()
        return list_of_preset

    def get_list_parameter(self, section, name):
        self.settings.beginGroup(PARAM_PATH)
        self.settings.beginGroup(section)
        self.settings.beginGroup(name)
        list_of_settings = self.settings.childGroups()
        self.settings.endGroup()
        self.settings.endGroup()
        self.settings.endGroup()

        return list_of_settings

    def load_settings(self, section):
        list_of_preset = self.get_list_preset(section)
        preset_dict = {}
        for name in list_of_preset:
            setting_dict = {}

            list_of_settings = self.get_list_parameter(section, name)
            param_cls = self.settings.value(
                '%s/%s/%s/cls_name' % (PARAM_PATH, section, name))
            setting_dict['cls_name'] = param_cls
            for g in list_of_settings:
                key_path = '%s/%s/%s/%s' % (PARAM_PATH, section, name, g)
                type_str = self.settings.value('%s/type' % key_path, None, str)
                if(type_str is None or len(type_str) == 0):
                    raise Exception('type not specified for {}'.format(key_path))
                val = MAP_TYPE[type_str](self.settings.value('%s/value' % key_path))
                setting_dict[g] = val

            obj = namedtuple(param_cls, setting_dict.keys(),
                             defaults=setting_dict.values())
            preset_dict[name] = obj()

        return preset_dict

    @staticmethod
    def np_type_to_string(value):
        """convert np.array to type string

        Args:
            value (np.ndarray): convert numpy array to type string

        Raises:
            Exception: unsupported type

        Returns:
            string: string description of type
        """
        if np.issubdtype(value.dtype, np.integer):
            return 'Array<{}>'.format('int')
        elif np.issubdtype(value.dtype, np.floating):
            return 'Array<{}>'.format('float')
        elif np.issubdtype(value.dtype, np.unicode_) or np.issubdtype(value.dtype, np.string_):
            return 'Array<{}>'.format('string')
        else:
            raise Exception("unsupported array type")

    @staticmethod
    def type_to_string(value):
        """convert single value to string type

        Args:
            value (non-iterable): Anything except iteratble

        Raises:
            Exception: unsupported type

        Returns:
            string: string description of type
        """
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, np.ndarray):
            return Versa3dSettings.np_type_to_string(value)
        else:
            raise Exception("unsupported type")
