
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

        self._printer_obj = None
        self._printhead_obj = None
        self._parameter_preset_obj = None

    @property
    def printer(self):
        return self._printer_obj

    @property
    def printhead(self):
        return self._printhead_obj

    @property
    def parameter_preset(self):
        return self._parameter_preset_obj

    def check_if_empty(self):
        return len(self.settings.allKeys()) == 0

    def init_default(self):
        with open(DEFAULT_CONFIG) as f:
            default_config = json.load(f)

        param_key = ['type', 'value']
        ui_key = ['label', 'section', 'category', 'section', 'unit']

        for setting_class_name, setting_dict in default_config.items():
            setting_type = setting_dict.pop('type')
            default_name = setting_dict.pop('default_name')

            if setting_type == 'printer':
                self.add_printer_signal.emit(default_name)
            elif setting_type == 'printhead':
                self.add_printhead_signal.emit(default_name)
            elif setting_type == 'parameter_preset':
                self.add_parameter_preset_signal.emit(default_name)
            else:
                raise 'unknown setting type'

            self.settings.setValue(
                "%s/%s/%s/%s" % (PARAM_PATH, setting_type, default_name, 'type'), setting_class_name)
            for key, param_dict in setting_dict.items():
                for sub_key, val in param_dict.items():
                    if sub_key in ui_key:
                        set_key = "%s/%s/%s/%s/%s" % (
                            UI_PATH, setting_type, setting_class_name, key, sub_key)
                        self.settings.setValue(set_key, val)
                    elif sub_key in param_key:
                        set_key = "%s/%s/%s/%s/%s" % (
                            PARAM_PATH, setting_type, default_name, key, sub_key)
                        self.settings.setValue(set_key, val)

        return True

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
        self._printer_obj = self.load_settings('printer')
        self._printhead_obj = self.load_settings('printhead')
        self._parameter_preset_obj = self.load_settings('parameter_preset')

    def get_printer(self, name):
        return self._printer_obj[name]

    def get_printhead(self, name):
        return self._printhead_obj[name]

    def get_preset(self, name):
        return self._parameter_preset_obj[name]

    def clone_printer(self, name, target_name):
        obj = self.clone_setting('printer', self._printer_obj[name])
        self.add_printer_signal.emit(target_name)
        self._printer_obj[target_name] = obj
        self.save_to_disk('printer', target_name)

    def clone_printhead(self, name, target_name):
        obj = self.clone_setting('printhead', self._printhead_obj[name])
        self.add_printhead_signal.emit(target_name)
        self._printhead_obj[target_name] = obj
        self.save_to_disk('printhead', target_name)

    def clone_param(self, name, target_name):
        obj = self.clone_setting(
            'parameter_preset', self._parameter_preset_obj[name])
        self.add_parameter_preset_signal.emit(target_name)
        self._parameter_preset_obj[target_name] = obj
        self.save_to_disk('parameter_preset', target_name)

    def remove_printer(self, name):
        self._printer_obj.pop(name)
        self.remove_from_disk('printer', name)
        self.remove_printer_signal.emit(name)

    def remove_printhead(self, name):
        self._printhead_obj.pop(name)
        self.remove_from_disk('printhead', name)
        self.remove_printhead_signal.emit(name)

    def remove_parameter(self, name):
        self._parameter_preset_obj.pop(name)
        self.remove_from_disk('parameter_preset', name)
        self.remove_parameter_preset_signal.emit(name)

    def remove_from_disk(self, section, name):
        key = "%s/%s/%s" % (PARAM_PATH, section, name)
        self.settings.remove(key)

    def clone_setting(self, section, old_obj):
        dict_obj = old_obj._asdict()
        return namedtuple(section, dict_obj.keys(), defaults=dict_obj.values())()

    def update_printer_value(self, name, key, value):
        self._printer_obj[name] = self._printer_obj[name]._replace(
            **{key: value})
        return self._printer_obj[name]

    def update_printhead_value(self, name, key, value):
        self._printhead_obj[name] = self._printhead_obj[name]._replace(
            **{key: value})
        return self._printhead_obj[name]

    def update_preset_value(self, name, key, value):
        self._parameter_preset_obj[name] = self._parameter_preset_obj[name]._replace(
            **{key: value})
        return self._parameter_preset_obj[name]

    def save_to_disk(self, section, name):
        obj_ls = getattr(self, section)
        settings = obj_ls[name]
        try:
            for param, value in settings._asdict().items():
                self.set_key_to_disk(section, name, param, value)
            return True
        except:
            raise Exception('disk write failed')

    def load_settings(self, section):
        self.settings.beginGroup(PARAM_PATH)
        self.settings.beginGroup(section)
        list_of_preset = self.settings.childGroups()
        self.settings.endGroup()
        self.settings.endGroup()

        preset_dict = {}
        for name in list_of_preset:
            setting_dict = {}

            self.settings.beginGroup(PARAM_PATH)
            self.settings.beginGroup(section)
            self.settings.beginGroup(name)
            list_of_settings = self.settings.childGroups()
            self.settings.endGroup()
            self.settings.endGroup()
            self.settings.endGroup()

            obj_name = self.settings.value(
                '%s/%s/%s/%s' % (PARAM_PATH, section, name, 'type'))
            setting_dict['type'] = section
            for g in list_of_settings:
                setting_dict[g] = self.get_key_from_disk(section, g, name)

            obj = namedtuple(name, setting_dict.keys(),
                             defaults=setting_dict.values())
            preset_dict[name] = obj()

        return preset_dict

    def get_key_from_disk(self, section, key, name):
        self.settings.beginGroup(PARAM_PATH)
        self.settings.beginGroup(section)
        self.settings.beginGroup(name)
        self.settings.beginGroup(key)
        type_str = self.settings.value('type', None, str)
        if(type_str is None or len(type_str) == 0):
            raise Exception('type not specified for {}'.format(key))
        else:
            val = MAP_TYPE[type_str](self.settings.value(
                'value'))
        self.settings.endGroup()
        self.settings.endGroup()
        self.settings.endGroup()
        self.settings.endGroup()
        return val

    def set_key_to_disk(self, section, name, key, value):
        self.settings.beginGroup(PARAM_PATH)
        self.settings.beginGroup(section)
        self.settings.beginGroup(name)
        self.settings.beginGroup(key)
        if isinstance(value, np.ndarray):
            self.settings.setValue('type', self.np_type_to_string(value))
            self.settings.setValue('value', value.tolist())
        else:
            self.settings.setValue('type', self.type_to_string(value))
            self.settings.setValue('value', value)
        self.settings.endGroup()
        self.settings.endGroup()
        self.settings.endGroup()
        self.settings.endGroup()

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
            raise Exception("unsupported type")

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
        else:
            raise Exception("unsupported type")
