
import json
from functools import partial
from collections import namedtuple

from PyQt5.QtCore import QSettings
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


class Versa3dSettings():

    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.initialized = self.init_default()

        self._printer_obj = self.load_settings('printer')
        self._printhead_obj = self.load_settings('printhead')
        self._parameter_preset_obj = self.load_settings('parameter_preset')

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
        if not self.check_if_empty():
            return True

        with open(DEFAULT_CONFIG) as f:
            default_config = json.load(f)

        param_key = ['type', 'value']
        ui_key = ['label', 'section', 'category', 'section', 'unit']

        for setting_class_name, setting_dict in default_config.items():
            setting_type = setting_dict.pop('type')
            default_name = setting_dict.pop('default_name')
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

    def get_printer(self, name):
        return self._printer_obj[name]

    def get_printhead(self, name):
        return self._printhead_obj[name]

    def get_preset(self, name):
        return self._parameter_preset_obj[name]

    def clone_printer(self, name, target_name):
        obj = self.clone_setting('printer', self._printer_obj[name])
        self._printer_obj[target_name] = obj

    def clone_printhead(self, name, target_name):
        obj = self.clone_setting('printhead', self._printhead_obj[name])
        self._printhead_obj[target_name] = obj

    def clone_param(self, name, target_name):
        obj = self.clone_setting(
            'parameter_preset', self._parameter_preset_obj[name])
        self._parameter_preset_obj[target_name] = obj

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
