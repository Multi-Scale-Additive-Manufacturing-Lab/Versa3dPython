
import json
import re
from collections import namedtuple

from PyQt5.QtCore import QSettings
import numpy as np

DEFAULT_CONFIG = './configs/default_config.json'


class Versa3dSettings():

    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.initialized = False
        self.printer_name = 'default_machine'
        self.printhead_name = 'default_printhead'
        self.parameter_preset_name = 'default_preset'

        if not self.initialized:
            self.settings = self.init_default()
            self.initialized = True

        self._printer_obj = self.load_settings('printer', self.printer_name)
        self._printhead_obj = self.load_settings(
            'printhead', self.printhead_name)
        self._preset_obj = self.load_settings(
            'parameter_preset', self.parameter_preset_name)

        self.printer = self._printer_obj()
        self.printhead = self._printhead_obj()
        self.parameter_preset = self._preset_obj()

    def check_if_empty(self):
        return len(self.settings.allKeys()) == 0

    def _map_to_name(self, section):
        if(section == 'printer'):
            return self.printer_name
        elif(section == 'parameter_preset'):
            return self.parameter_preset_name
        elif(section == 'printhead'):
            return self.printhead_name
        else:
            raise Exception('unknown section')

    def init_default(self):
        if self.check_if_empty():
            with open(DEFAULT_CONFIG) as f:
                default_config = json.load(f)

            for section, sec_val in default_config.items():
                self.settings.beginGroup(section)
                self.settings.beginGroup(self._map_to_name(section))
                for param, value in sec_val.items():
                    self.settings.beginGroup(param)
                    self.settings.setValue('value', value['value'])
                    self.settings.setValue('type', value['type'])
                    self.settings.endGroup()
                self.settings.endGroup()
                self.settings.endGroup()
        return self.settings

    def change_printer(self, name, new_set=False):
        self.printer_name = name
        self._preset_obj = self.load_settings('printer', name, new_set)
        self.printer = self._preset_obj()
        return self.printer

    def change_printhead(self, name, new_set=False):
        self.printhead_name = name
        self._printhead_obj = self.load_settings('printhead', name, new_set)
        self.printhead = self._printhead_obj()
        return self.printhead

    def change_preset(self, name, new_set=False):
        self.parameter_preset_name = name
        self._preset_obj = self.load_settings(
            'parameter_preset', name, new_set)
        self.parameter_preset = self._preset_obj()
        return self.parameter_preset

    def update_printer_value(self, key, value):
        self.printer = self.printer._replace(**{key: value})
        return self.printer

    def update_printhead_value(self, key, value):
        self.printhead = self.printhead._replace(**{key: value})
        return self.printhead

    def update_preset_value(self, key, value):
        self.parameter_preset = self.parameter_preset._replace(**{key: value})
        return self.parameter_preset

    def save_to_disk(self):
        list_settings = {
            'printer': self.printer,
            'printhead': self.printhead,
            'parameter_preset': self.parameter_preset
        }

        list_name = {
            'printer': self.printer_name,
            'printhead': self.printhead_name,
            'parameter_preset': self.parameter_preset_name
        }

        try:
            for section, obj in list_settings.items():
                name = list_name[section]
                for param, value in obj._asdict().items():
                    self.set_key_to_disk(section, name, param, value)

            return True
        except:
            raise Exception('disk write failed')

    def load_settings(self, section, name, new_set=False):
        self.settings.beginGroup(section)
        list_of_preset = self.settings.childGroups()
        self.settings.beginGroup(name)
        list_of_settings = self.settings.childGroups()
        self.settings.endGroup()
        self.settings.endGroup()

        if name in list_of_preset:
            setting_dict = {}
            for g in list_of_settings:
                setting_dict[g] = self.get_key_from_disk(section, g, name)
            return namedtuple(section, setting_dict.keys(), defaults=setting_dict.values())
        elif new_set:
            setting_dict = {}
            obj = getattr(self, section)._asdict()
            return namedtuple(section, obj.keys(), defaults=obj.values())
        else:
            raise Exception(
                'no {} settings with name {}'.format(section, name))

    def get_key_from_disk(self, section, key, name=None):
        if name is None:
            name = self._map_to_name(section)

        self.settings.beginGroup(section)
        self.settings.beginGroup(name)
        self.settings.beginGroup(key)
        type_str = self.settings.value('type', None, str)
        if(type_str is None or len(type_str) == 0):
            raise Exception('type not specified for {}'.format(key))
        elif re.match(r'Array(?=\<)', type_str):
            t_str = re.search(r'(?<=\<)[a-z]+(?=\>)', type_str).group()
            val = np.array(self.settings.value(
                'value', [], self.string_to_type(t_str)))
        else:
            val = self.settings.value(
                'value', type=self.string_to_type(type_str))
        self.settings.endGroup()
        self.settings.endGroup()
        self.settings.endGroup()
        return val

    def set_key_to_disk(self, section, name, key, value):
        if name is None:
            name = self._map_to_name(section)

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

    @staticmethod
    def string_to_type(type_str):
        """from string return type

        Args:
            type_str (string): type string

        Raises:
            Exception: unsupported type

        Returns:
            type: return type object
        """
        if type_str == 'int':
            return int
        elif type_str == 'float':
            return float
        elif type_str == 'string':
            return str
        else:
            raise Exception("unsupported type")
