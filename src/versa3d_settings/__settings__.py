from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSlot
from .__options__ import enum_option, ordered_array_option, single_option


class generic_settings():
    def __init__(self, name):
        super().__init__()
        self._name = name
        self._settings = QSettings()

        self._lso = {}

    @property
    def name(self):
        return self._name

    @pyqtSlot
    def save_settings(self):
        self._settings.beginGroup(self._name)
        for name, option in self._list_option.items():
            if(option is ordered_array_option):
                self._settings.beginWriteArray(name, len(option))
                for i, val in enumerate(option.value):
                    self._settings.setArrayIndex(i)
                    self._settings.setValue(name, val)
            else:
                self._settings.setValue(name, option.value)

    def load_settings(self):
        self._settings.beginGroup(self._name)
        for name, option in self._list_option.items():
            if(option is ordered_array_option):
                self._settings.beginReadArray(name, len(option))
                for i, val in enumerate(option.value):
                    self._settings.setArrayIndex(i)
                    self._settings.value(name, val)
                self._settings.endArray()
            else:
                self._settings.value(name, option.value)
        self._settings.endGroup()

class printer_settings(generic_settings):
    def __init__(self, name="basic_printer"):
        super().__init__(name)

        self._lso['build_bed_size'] = ordered_array_option([50, 50, 100])
        self._lso['build_bed_size'].label = 'build bed size'
        self._ls['build_bed_size'].sidetext = 'mm'
        self._lso['build_bed_size'].category = 'plate'

        self._lso['coord_offset'] = ordered_array_option([0.0, 0.0, 0.0])
        self._lso['coord_offset'].label = 'coordinate offset'
        self._lso['coord_offset'].sidetext = 'mm'
        self._lso['coord_offset'].category - 'plate'


class printhead_settings(generic_settings):
    def __init__(self, name='basic_printhead'):
        super().__init__(name)

        self._lso['dpi'] = ordered_array_option([150, 150])


class print_settings(generic_settings):
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
