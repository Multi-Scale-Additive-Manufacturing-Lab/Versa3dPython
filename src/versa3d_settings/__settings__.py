from PyQt5.QtCore import QSettings

class generic_settings():
    def __init__(self, name):
        super().__init__()
        self._name = name
        self._settings = QSettings()

    @property
    def name(self):
        return self._name

    def single_property(self,property_name):
        prop_name = '{}/{}'.format()
        self._settings.value('/')

class printer_settings(generic_settings):
    def __init__(self, name="basic_printer"):
        super().__init__(name)

        self._bds = self.build_bed_size

    @property
    def build_bed_size(self):
        x_sc = self._settings.value(
            '{}/bed_x'.format(self._name), 50.0, type=float)
        y_sc = self._settings.value(
            '{}/bed_y'.format(self._name), 50.0, type=float)
        z_sc = self._settings.value(
            '{}/bed_z'.format(self._name), 100.0, type=float)

        return (x_sc, y_sc, z_sc)


class printhead_settings(generic_settings):
    def __init__(self, name='basic_printhead'):
        super().__init__(name)

        self._dpi = self.dpi
        self._variable_vol = self.variable_volume

    @property
    def dpi(self):
        x_dpi = self._settings.value(
            '{}/dpi_x'.format(self._name), 300.0, type=float)
        y_dpi = self._settings.value(
            '{}/dpi_y'.format(self._name), 300.0, type=float)
        return (x_dpi, y_dpi)

    @property
    def variable_volume(self):
        vv = self._settings.value(
            '{}/variable_volume'.format(self._name), False, type=bool)
        return vv


class print_settings(generic_settings):
    def __init__(self, name='default_settings'):
        super().__init__(name)

        self._lt = self.layer_thickness
        self._roller_rpm = self.roller_rpm
        self._roller_lin = self.roller_lin

        self._powder_loss_offset 
        self._print_height_offset
        self._roller_work_distance

        self._feed_bed_selection

        self._coord_offset

        self._saturation
        self._n_pass

    @property
    def layer_thickness(self):
        return self._settings(
            '{}/layer_thickness'.format(self._name), 100.0, type=float)

    @property
    def roller_rpm(self):
        return self._settings(
            '{}/roller_rpm'.format(self._name), 100.0, type=float)

    @property
    def roller_lin(self):
        return self._settings(
            '{}/roller_lin'.format(self._name), 100.0, type=float)
    
    @property
    def powder_loss_offset(self):
        return self._settings(
            '{}/powder_loss_offset'.format(self._name), 20.0, type=float)
    
    @property
    def print_height_offset(self):
        return self._settings(
            '{}/print_height_offset'.format(self._name), 20.0, type=float)  
