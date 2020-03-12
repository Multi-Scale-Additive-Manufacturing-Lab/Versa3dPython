from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSlot
from .__options__ import enum_option, ordered_array_option, single_option


def load_stored_settings(name, settings):
    settings.beginGroup(name)
    list_stored = settings.childGroups()
    settings.endGroup()

    list_settings = []
    for setting_name in list_stored:
        setting_obj = print_settings(printer_name)
        setting_obj.load_settings()
        list_settings.append(setting_obj)

    return list_settings


def load_settings(settings = None):

    if(settings is None):
        settings = QSettings()

    list_printer = load_stored_settings('printer_settings', settings)
    list_printhead = load_stored_settings('printhead_settings', settings)
    list_print_setting = load_stored_settings('print_settings', settings)

    if(len(list_printer) == 0):
        list_printer.append(printer_settings())

    if(len(list_printhead) == 0):
        list_printhead.append(printhead_settings())

    if(len(list_print_setting) == 0):
        list_print_setting.append(print_settings())

    return {'printer_settings': list_printer,
            'printhead_settings': list_printhead,
            'print_settings': list_print_setting}


class generic_settings():
    def __init__(self, name):
        super().__init__()
        self._name = name
        self._settings = QSettings()

        self._lso = {}
        self._prefix = None
        self._category = None

    @property
    def name(self):
        return self._name
    
    @property
    def category(self):
        return self._category

    #@pyqtSlot
    def save_settings(self):
        self._settings.beginGroup(self._name)
        for name, option in self._lso.items():
            if(option is ordered_array_option):
                self._settings.beginWriteArray(name, len(option))
                for i, val in enumerate(option.value):
                    self._settings.setArrayIndex(i)
                    self._settings.setValue(name, val)
                self._settings.endArray()
            else:
                self._settings.setValue(name, option.value)
        self._settings.endGroup()

    def load_settings(self):
        self._settings.beginGroup(self._name)
        for name, option in self._lso.items():
            if(type(option) is ordered_array_option):
                self._settings.beginReadArray(name)
                for i, val in enumerate(option.value):
                    self._settings.setArrayIndex(i)
                    variant = self._settings.value(name, val)
                    option.set_value_at_index(i, variant)
                self._settings.endArray()
            else:
                variant = self._settings.value(name, option.default_value)
                option.value = variant

        self._settings.endGroup()


class printer_settings(generic_settings):
    category = ['plate']
    def __init__(self, name="basic_printer"):
        super().__init__(name)

        self._lso['build_bed_size'] = ordered_array_option([50, 50, 100])
        self._lso['build_bed_size'].label = 'build bed size'
        self._lso['build_bed_size'].sidetext = 'mm'
        self._lso['build_bed_size'].category = 'plate'

        self._lso['coord_offset'] = ordered_array_option([0.0, 0.0, 0.0])
        self._lso['coord_offset'].label = 'coordinate offset'
        self._lso['coord_offset'].sidetext = 'mm'
        self._lso['coord_offset'].category = 'plate'

        self.load_settings()

    def load_settings(self):
        self._settings.beginGroup('printer_settings')
        super().load_settings()
        self._settings.endGroup()


class printhead_settings(generic_settings):
    category = ['resolution']

    def __init__(self, name='basic_printhead'):
        super().__init__(name)

        self._lso['dpi'] = ordered_array_option([150, 150])
        self._lso['dpi'].label = 'dpi'
        self._lso['dpi'].category = 'resolution'

        self.load_settings()

    def load_settings(self):
        self._settings.beginGroup('printhead_settings')
        super().load_settings()
        self._settings.endGroup()


class print_settings(generic_settings):
    category = ['layer', 'infill']

    def __init__(self, name='default_settings'):
        super().__init__(name)

        self._lso['layer_thickness'] = single_option(100.0)
        self._lso['layer_thickness'].label = 'layer thickness'
        # do greek letter later
        self._lso['layer_thickness'].sidetext = 'microns'
        self._lso['layer_thickness'].category = 'layer'

        self._lso['roller_rpm'] = single_option(100.0)
        self._lso['roller_rpm'].label = 'roller rotation speed'
        self._lso['roller_rpm'].sidetext = 'rpm'
        self._lso['roller_rpm'].category = 'layer'

        self._lso['roller_lin'] = single_option(10.0)
        self._lso['roller_lin'].label = 'roller linear speed'
        self._lso['roller_lin'].sidetext = 'mm'
        self._lso['roller_lin'].category = 'layer'

        self._lso['powder_loss_offset'] = single_option(10.0)
        self._lso['powder_loss_offset'].label = 'powder loss offset'
        self._lso['powder_loss_offset'].sidetext = '%'
        self._lso['powder_loss_offset'].category = 'layer'

        self._lso['print_height_offset'] = single_option(10.0)
        self._lso['print_height_offset'].label = 'printheight offset'
        self._lso['print_height_offset'].sidetext = 'microns'
        self._lso['print_height_offset'].category = 'layer'

        self._lso['roller_work_distance'] = single_option(10.0)
        self._lso['roller_work_distance'].label = 'roller work distance'
        self._lso['roller_work_distance'].sidetext = 'microns'
        self._lso['roller_work_distance'].category = 'layer'

        self._lso['bed_selection'] = enum_option(
            0, ['bed 1', 'bed 2', 'bed 3'])
        self._lso['bed_selection'].label = 'bed selection'
        self._lso['bed_selection'].category = 'layer'

        self._lso['saturation'] = single_option(100.0)
        self._lso['saturation'].label = 'saturation'
        self._lso['saturation'].sidetext = '%'
        self._lso['saturation'].category = 'infill'

        self._lso['n_pass'] = single_option(1)
        self._lso['n_pass'].label = 'number of pass'
        self._lso['n_pass'].category = 'infill'

        self.load_settings()

    def load_settings(self):
        self._settings.beginGroup('print_settings')
        super().load_settings()
        self._settings.endGroup()
