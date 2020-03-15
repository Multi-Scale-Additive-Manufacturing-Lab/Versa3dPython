from enum import Enum

from PyQt5.QtCore import QSettings
from .__options__ import EnumOption, PointOption, SingleOption


class Setting(Enum):
    PRINTER = 'printer_settings'
    PRINTHEAD = 'printhead_settings'
    PRINT_PRESET = 'print_settings'


class Printhead(Enum):
    DPI = 'dpi'


class Printer(Enum):
    BUILD_BED_SIZE = 'bds'
    COORD_OFFSET = 'coord_o'
    MODEL = 'model'


class PrintParam(Enum):
    LAYER_THICKESS = 'lt'
    ROLLER_ROT = 'rol_rpm'
    ROLLER_LIN = 'rol_lin'
    POWDER_LOSS_OFFSET = 'pl'
    POWDER_HEIGHT_OFFSET = 'pho'
    ROLLER_WORK_DIST = 'rwd'
    BED_SELECT = 'bs'
    SATURATION = 'sat'
    N_PASS = 'n_p'
    PRINT_SPEED = 'ps'
    FEED_BED_VEL = 'fbv'
    BUILD_BED_VEL = 'bbv'


def load_stored_settings(name, settings):
    settings.beginGroup(name)
    list_stored = settings.childGroups()
    settings.endGroup()

    list_settings = []
    for setting_name in list_stored:
        setting_obj = PrintSettings(setting_name)
        setting_obj.load_settings()
        list_settings.append(setting_obj)

    return list_settings


def load_settings(settings=None):

    if(settings is None):
        settings = QSettings()

    list_printer = load_stored_settings(Setting.PRINTER, settings)
    list_printhead = load_stored_settings(Setting.PRINTHEAD, settings)
    list_print_setting = load_stored_settings(
        Setting.PRINT_PRESET, settings)

    if(len(list_printer) == 0):
        list_printer.append(PrinterSettings())

    if(len(list_printhead) == 0):
        list_printhead.append(PrintheadSettings())

    if(len(list_print_setting) == 0):
        list_print_setting.append(PrintSettings())

    return {Setting.PRINTER: list_printer,
            Setting.PRINTHEAD: list_printhead,
            Setting.PRINT_PRESET: list_print_setting}


class GenericSettings():
    def __init__(self, name):
        super().__init__()
        self._name = name
        self._settings = QSettings()

        self._prefix = None
        self._lso = {}

    def __getattr__(self, key):
        option = self._lso[key]
        return option.value

    @property
    def name(self):
        return self._name


class PrinterSettings(GenericSettings):

    def __init__(self, name="basic_printer"):
        super().__init__(name)

        self._prefix = Setting.PRINTER

        self._lso[Printer.BUILD_BED_SIZE] = PointOption(
            self._prefix, Printer.BUILD_BED_SIZE, [50, 50, 100])
        self._lso[Printer.BUILD_BED_SIZE].label = 'build bed size'
        self._lso[Printer.BUILD_BED_SIZE].sidetext = 'mm'
        self._lso[Printer.BUILD_BED_SIZE].category = 'plate'

        self._lso[Printer.COORD_OFFSET] = PointOption(
            self._prefix, Printer.COORD_OFFSET, [0.0, 0.0, 0.0])
        self._lso[Printer.COORD_OFFSET].label = 'coordinate offset'
        self._lso[Printer.COORD_OFFSET].sidetext = 'mm'
        self._lso[Printer.COORD_OFFSET].category = 'plate'


class PrintheadSettings(GenericSettings):

    def __init__(self, name='basic_printhead'):
        super().__init__(name)

        self._prefix = Setting.PRINTHEAD

        self._lso[Printhead.DPI] = PointOption(
            self._prefix, Printhead.DPI, [150, 150])
        self._lso[Printhead.DPI].label = 'dpi'
        self._lso[Printhead.DPI].category = 'resolution'


class PrintSettings(GenericSettings):

    def __init__(self, name='default_settings'):
        super().__init__(name)

        self._prefix = f'{Setting.PRINT_PRESET}/{name}'

        self._lso[PrintParam.LAYER_THICKNESS] = SingleOption(
            self._prefix, PrintParam.LAYER_THICKESS, 100.0)
        self._lso[PrintParam.LAYER_THICKNESS].label = 'layer thickness'
        # do greek letter later
        self._lso[PrintParam.LAYER_THICKNESS].sidetext = 'microns'
        self._lso[PrintParam.LAYER_THICKNESS].category = 'layer'

        self._lso[PrintParam.ROLLER_ROT] = SingleOption(
            self._prefix, PrintParam.ROLLER_ROT, 100.0)
        self._lso[PrintParam.ROLLER_ROT].label = 'roller rotation speed'
        self._lso[PrintParam.ROLLER_ROT].sidetext = 'rpm'
        self._lso[PrintParam.ROLLER_ROT].category = 'layer'

        self._lso[PrintParam.ROLLER_LIN] = SingleOption(
            self._prefix, PrintParam.ROLLER_LIN, 10.0)
        self._lso[PrintParam.ROLLER_LIN].label = 'roller linear speed'
        self._lso[PrintParam.ROLLER_LIN].sidetext = 'mm'
        self._lso[PrintParam.ROLLER_LIN].category = 'layer'

        self._lso[PrintParam.POWDER_LOSS_OFFSET] = SingleOption(
            self._prefix, PrintParam.POWDER_LOSS_OFFSET, 10.0)
        self._lso[PrintParam.POWDER_LOSS_OFFSET].label = 'powder loss offset'
        self._lso[PrintParam.POWDER_LOSS_OFFSET].sidetext = '%'
        self._lso[PrintParam.POWDER_LOSS_OFFSET].category = 'layer'

        self._lso[PrintParam.POWDER_HEIGHT_OFFSET] = SingleOption(
            self._prefix, PrintParam.POWDER_HEIGHT_OFFSET, 10.0)
        self._lso[PrintParam.POWDER_HEIGHT_OFFSET].label = 'printheight offset'
        self._lso[PrintParam.POWDER_HEIGHT_OFFSET].sidetext = 'microns'
        self._lso[PrintParam.POWDER_HEIGHT_OFFSET].category = 'layer'

        self._lso[PrintParam.ROLLER_WORK_DIST] = SingleOption(
            self._prefix, PrintParam.ROLLER_WORK_DIST, 10.0)
        self._lso[PrintParam.ROLLER_WORK_DIST].label = 'roller work distance'
        self._lso[PrintParam.ROLLER_WORK_DIST].sidetext = 'microns'
        self._lso[PrintParam.ROLLER_WORK_DIST].category = 'layer'

        self._lso[PrintParam.BED_SELECT] = EnumOption(
            self._prefix, PrintParam.BED_SELECT, 0, ['bed 1', 'bed 2', 'bed 3'])
        self._lso[PrintParam.BED_SELECT].label = 'bed selection'
        self._lso[PrintParam.BED_SELECT].category = 'layer'

        self._lso[PrintParam.SATURATION] = SingleOption(
            self._prefix, PrintParam.SATURATION, 100.0)
        self._lso[PrintParam.SATURATION].label = 'saturation'
        self._lso[PrintParam.SATURATION].sidetext = '%'
        self._lso[PrintParam.SATURATION].category = 'infill'

        self._lso[PrintParam.N_PASS] = SingleOption(
            self._prefix, PrintParam.N_PASS, 1)
        self._lso[PrintParam.N_PASS].label = 'number of pass'
        self._lso[PrintParam.N_PASS].category = 'infill'

        self._lso[PrintParam.PRINT_SPEED] = SingleOption(
            self._prefix, PrintParam.PRINT_SPEED, 1.0)
        self._lso[PrintParam.PRINT_SPEED].label = 'print speed'
        self._lso[PrintParam.PRINT_SPEED].category = 'layer'
        self._lso[PrintParam.PRINT_SPEED].sidetext = 'm/s'

        self._lso[PrintParam.FEED_BED_VEL] = SingleOption(
            self._prefix, PrintParam.FEED_BED_VEL, 1.0)
        self._lso[PrintParam.FEED_BED_VEL].label = 'feed bed velocity'
        self._lso[PrintParam.FEED_BED_VEL].category = 'layer'
        self._lso[PrintParam.FEED_BED_VEL].sidetext = 'mm/s'

        self._lso[PrintParam.BUILD_BED_VEL] = SingleOption(
            self._prefix, PrintParam.BUILD_BED_VEL, 1.0)
        self._lso[PrintParam.BUILD_BED_VEL].label = 'feed bed velocity'
        self._lso[PrintParam.BUILD_BED_VEL].category = 'layer'
        self._lso[PrintParam.BUILD_BED_VEL].sidetext = 'mm/s'
